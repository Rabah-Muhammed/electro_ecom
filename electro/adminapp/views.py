from datetime import datetime, timedelta
import json
from django.utils import timezone
from io import BytesIO
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
import logging
from django.shortcuts import render
from django.contrib.auth.models import User
from carts.models import Coupon, Order, OrderItem
from product.forms import ProductForm
from .models import Profile
from category.models import Category
from product.models import Brand, Product, ProductGallery
from django.views.decorators.cache import cache_control
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum,Count
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from .utils import generate_ledger_pdf
from .forms import BrandForm, DateRangeForm
from django.views.decorators.http import require_POST
from django.db.models import Min, Max

User = get_user_model()

logger = logging.getLogger(__name__)

# Decorator to check if the user is a superuser

def admin_required(view_func):
    @login_required(login_url='alogin')
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('alogin')  
        return view_func(request, *args, **kwargs)
    return wrapper

def adminlogin(request):
    error_message = None 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        logger.debug(f"Username: {username}, Password: {password}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            logger.debug(f"Authenticated user: {user.username}, is_superuser: {user.is_superuser}")
        else:
            logger.debug("Authentication failed")

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('ahome')
        else:
            error_message = "Invalid credentials or not a superuser"
    
    return render(request, 'adminlogin.html', {'error_message': error_message})

@admin_required
def ahome(request):
    return render(request, 'ahome.html')

def adminlogout(request):
    logout(request)
    return redirect('alogin')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def user_list(request):
    users = User.objects.filter(is_superuser=False).order_by('-id')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_status = request.POST.get('new_status')
        user = User.objects.get(id=user_id)
        user.status = new_status
        user.save()
        return redirect('userlist')  # Redirect to the user list page
    return render(request, 'userlist.html', {'users': users})


# function for user list update block and unblock


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def update_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'blocked':
            user.is_active = False
        elif new_status == 'active':
            user.is_active = True
        user.save()
        return redirect('userlist')  # Redirect to the user list page 
    return render(request, 'userlist.html', {'users': User.objects.all()})


def categorylist(request):
    categories = Category.objects.all()
    return render(request, 'categorylist.html', {'categories': categories})

def addcategory(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        offer_percentage_str = request.POST.get('offer_percentage')
        cat_image = request.FILES.get('cat_image')

        try:
            offer_percentage = float(offer_percentage_str) if offer_percentage_str else None
        except ValueError:
            messages.error(request, 'Invalid offer percentage value.')
            return redirect('categorylist')

        if Category.objects.filter(category_name=category_name).exists():
            messages.error(request, f'A category with the name "{category_name}" already exists.')
        elif Category.objects.filter(slug=slug).exists():
            messages.error(request, f'A category with the slug "{slug}" already exists.')
        else:
            Category.objects.create(
                category_name=category_name,
                slug=slug,
                description=description,
                offer_percentage=offer_percentage,
                cat_image=cat_image
            )
            messages.success(request, 'Category added successfully.')
        return redirect('categorylist')
    
    return redirect('categorylist')


def editcategory(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        offer_percentage_str = request.POST.get('offer_percentage')
        cat_image = request.FILES.get('cat_image')

        try:
            offer_percentage = float(offer_percentage_str) if offer_percentage_str else None
        except ValueError:
            messages.error(request, 'Invalid offer percentage value.')
            return render(request, 'categoryform.html', {'category': category})

        if category_name != category.category_name and Category.objects.filter(category_name=category_name).exists():
            messages.error(request, f'A category with the name "{category_name}" already exists.')
            return render(request, 'categoryform.html', {'category': category})
        
        category.category_name = category_name
        category.slug = slug
        category.description = description
        category.offer_percentage = offer_percentage
        if cat_image:
            category.cat_image = cat_image
        category.save()
        
        messages.success(request, 'Category updated successfully.')
        return redirect('categorylist')
    
    return render(request, 'categoryform.html', {'category': category})


def deletecategory(request, category_id, soft_delete=True):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        if soft_delete:
            category.is_deleted = True
            category.save()
            messages.success(request, f'Category "{category.category_name}" has been marked as deleted.')
        else:
            category.delete()
            messages.success(request, f'Category "{category.category_name}" has been deleted successfully.')
        
        return redirect('categorylist')
    
    return render(request, 'deletecategory.html', {'category': category})


def productlist(request):
    products = Product.objects.all().order_by('id')
    paginator = Paginator(products, 10)  # Show 10 products per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
    }
    return render(request, 'productlist.html', context)


def addproduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()  # Save the main product details
            
            # Handle gallery images
            gallery_images = request.FILES.getlist('gallery_images')
            for image in gallery_images:
                ProductGallery.objects.create(product=product, image=image)
                
            messages.success(request, 'Product added successfully.')
            return redirect('productlist')
        else:
            messages.error(request, 'Error adding product. Please correct the form errors.')
    else:
        form = ProductForm()
        
    return render(request, 'addproduct.html', {'form': form})

def editproduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            # Handle gallery images update if any
            gallery_images = request.FILES.getlist('gallery_images')
            if gallery_images:
                for image in gallery_images:
                    ProductGallery.objects.create(product=product, image=image)

            messages.success(request, 'Product updated successfully.')
            return redirect('productlist')
        else:
            messages.error(request, 'Error updating product. Please correct the form errors.')
    else:
        form = ProductForm(instance=product)

    return render(request, 'editproduct.html', {'form': form, 'product': product})


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if 'hard_delete' in request.path:
        # Perform hard delete
        product.delete()
        return redirect('productlist')
    elif request.GET.get('soft_delete') == 'True':
        # Perform soft delete
        product.is_deleted = True
        product.save()
        return redirect('productlist')
    
    return redirect('productlist')


def delete_gallery_image(request, product_id, image_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        image = get_object_or_404(ProductGallery, pk=image_id, product=product)
        image.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


def manage_orders(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        order = get_object_or_404(Order, id=order_id)
        
        if action == 'update_status':
            status = request.POST.get('status')

            # Check if status update is valid based on current status
            if order.status == 'Pending' and status in ['Completed', 'Cancelled']:
                order.status = status
                order.save()
                messages.success(request, 'Order status updated successfully.')
            elif order.status == 'Completed' and status == 'Cancelled':
                order.status = status
                order.save()
                messages.success(request, 'Order cancelled successfully.')
            elif status == 'Returned':
                # Increase the product quantity for each order item
                order_items = OrderItem.objects.filter(order=order)
                for item in order_items:
                    item.product.stock += item.quantity  # Increase stock
                    item.product.save()  # Save the updated product

                order.status = status
                order.save()
                messages.success(request, 'Order marked as returned successfully.')
                logger.info(f"Order {order_id} returned successfully by admin.")
            else:
                messages.error(request, 'Invalid status change.')

        elif action == 'cancel':
            if order.status == 'Pending':
                order.status = 'Cancelled'
                order.save()
                messages.success(request, 'Order cancelled successfully.')
            else:
                messages.error(request, 'Cannot cancel this order.')

    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'order_management.html', {'orders': orders})



def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Check if the order can be returned
    if order.status in ['Completed']:
        # Increase the product quantity for each order item
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            item.product.stock += item.quantity  # Increase stock
            item.product.save()  # Save the updated product

        order.status = 'Returned'
        order.save()
        messages.success(request, 'Order marked as returned successfully.')
        logger.info(f"Order {order_id} returned successfully by admin.")
    else:
        messages.error(request, 'Cannot return this order.')

    return redirect('order_history')


def generate_pdf(orders, report_type, start_date=None, end_date=None):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_sales_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph(f"{report_type} Sales Report", styles['Title'])
    elements.append(title)

    # Initialize date_info to an empty paragraph
    date_info = Paragraph(" ", styles['Normal'])

    if report_type == 'Daily':
        date_info = Paragraph(f"Date: {start_date}", styles['Normal'])
    elif report_type == 'Weekly':
        date_info = Paragraph(f"Week: {start_date} to {end_date}", styles['Normal'])
    elif report_type == 'Yearly':
        date_info = Paragraph(f"Year: {start_date.year}", styles['Normal'])
    elif report_type == 'Custom':
        date_info = Paragraph(f"Custom Range: {start_date} to {end_date}", styles['Normal'])

    elements.append(date_info)
    elements.append(Paragraph(" ", styles['Normal']))  # Add a space

    # Table header
    data = [
        ['Order ID', 'User', 'Total Amount', 'Coupon Amount', 'Status', 'Date']
    ]

    # Table content
    for order in orders:
        data.append([
            str(order.id),
            order.user.username,
            f"${order.total_amount}",
            f"${order.coupon_amount}",
            order.status,
            order.created_at.strftime('%Y-%m-%d')
        ])

    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    doc.build(elements)
    return response


def generate_excel_report(orders):
    # Create a DataFrame from the orders queryset.
    data = {
        'Order ID': [order.id for order in orders],
        'User': [order.user.username for order in orders],
        'Total Amount': [float(order.total_amount) for order in orders],
        'Coupon Amount': [float(order.coupon_amount) for order in orders],
        'Status': [order.status for order in orders],
        'Date': [order.created_at.strftime('%Y-%m-%d') for order in orders],
    }
    df = pd.DataFrame(data)

    # Create an in-memory output file for the new workbook.
    output = BytesIO()

    # Use pandas Excel writer to write DataFrame to the output file.
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sales Report')

    # Rewind the buffer.
    output.seek(0)

    # Construct response.
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'

    return response


def sales_report(request):
    report_type = request.GET.get('report_type', 'daily')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    filter_period = request.GET.get('filter_period')
    today = datetime.now().date()

    def aggregate_orders(orders):
        total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_coupon = orders.aggregate(total=Sum('coupon_amount'))['total'] or 0
        total_orders = orders.count()
        return total_sales, total_coupon, total_orders

    if filter_period == '1_day':
        start_date = today - timedelta(days=1)
        end_date = today
    elif filter_period == '1_week':
        start_date = today - timedelta(days=7)
        end_date = today
    elif filter_period == '1_month':
        start_date = today - timedelta(days=30)
        end_date = today

    if report_type == 'daily':
        orders = Order.objects.filter(created_at__date=today, status='Completed')
        total_sales, total_coupon, total_orders = aggregate_orders(orders)
        context = {
            'orders': orders,
            'total_sales': total_sales,
            'total_coupon': total_coupon,
            'total_orders': total_orders,
            'report_type': 'Daily',
            'date': today,
        }
        start_date = today

    elif report_type == 'weekly':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        orders = Order.objects.filter(created_at__date__range=[start_of_week, end_of_week], status='Completed')
        total_sales, total_coupon, total_orders = aggregate_orders(orders)
        context = {
            'orders': orders,
            'total_sales': total_sales,
            'total_coupon': total_coupon,
            'total_orders': total_orders,
            'report_type': 'Weekly',
            'start_date': start_of_week,
            'end_date': end_of_week,
        }
        start_date = start_of_week
        end_date = end_of_week

    elif report_type == 'yearly':
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)
        orders = Order.objects.filter(created_at__date__range=[start_of_year, end_of_year], status='Completed')
        total_sales, total_coupon, total_orders = aggregate_orders(orders)
        context = {
            'orders': orders,
            'total_sales': total_sales,
            'total_coupon': total_coupon,
            'total_orders': total_orders,
            'report_type': 'Yearly',
            'year': today.year,
        }
        start_date = start_of_year
        end_date = end_of_year

    elif report_type == 'custom':
        if start_date and end_date:
            orders = Order.objects.filter(created_at__date__range=[start_date, end_date], status='Completed')
            total_sales, total_coupon, total_orders = aggregate_orders(orders)
            context = {
                'orders': orders,
                'total_sales': total_sales,
                'total_coupon': total_coupon,
                'total_orders': total_orders,
                'report_type': 'Custom',
                'start_date': start_date,
                'end_date': end_date,
            }
        else:
            context = {
                'report_type': 'Custom',
                'error': 'Please provide both start and end dates.'
            }
            return render(request, 'sales_report.html', context)

    else:
        context = {
            'error': 'Invalid report type.'
        }
        return render(request, 'sales_report.html', context)

    if 'generate_pdf' in request.GET:
        return generate_pdf(orders, report_type, start_date, end_date)

    if 'generate_excel' in request.GET:
        return generate_excel_report(orders)

    return render(request, 'sales_report.html', context)


def get_top_selling_products():
    # Aggregate the total quantity sold for each product
    top_products = OrderItem.objects.values('product').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:10]
    
    # Fetch product instances and their total sales
    top_products_details = []
    for item in top_products:
        product = Product.objects.get(id=item['product'])
        top_products_details.append({
            'product': product,
            'total_sold': item['total_sold']
        })
    
    return top_products_details


def get_top_selling_categories():
    # Aggregate the total quantity sold for each category
    top_categories = OrderItem.objects.values('product__category').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:10]
    
    # Fetch category instances and their total sales
    top_categories_details = []
    for item in top_categories:
        category = Category.objects.get(id=item['product__category'])
        top_categories_details.append({
            'category': category,
            'total_sold': item['total_sold']
        })
    
    return top_categories_details


def get_top_selling_brands():
    # Aggregate the total quantity sold for each brand
    top_brands = OrderItem.objects.values('product__brand').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:10]
    
    # Fetch brand instances in bulk to avoid N+1 queries
    brand_ids = [item['product__brand'] for item in top_brands]
    brands = Brand.objects.filter(id__in=brand_ids)  # Assuming you have a Brand model
    brand_dict = {brand.id: brand for brand in brands}

    # Prepare the top brands details
    top_brands_details = []
    for item in top_brands:
        brand = brand_dict.get(item['product__brand'])
        if brand:
            top_brands_details.append({
                'brand': brand,
                'total_sold': item['total_sold']
            })
    
    return top_brands_details


def top_selling_view(request):
    top_products = get_top_selling_products()
    top_categories = get_top_selling_categories()
    top_brands = get_top_selling_brands()


    context = {
        'top_products': top_products,
        'top_categories': top_categories,
        'top_brands': top_brands
    }

    return render(request, 'top_selling.html', context)


def get_monthly_sales_data(start_date, end_date):
    sales_data = Order.objects.filter(created_at__range=[start_date, end_date]).extra(
        {'day': "date(created_at)"}
    ).values('day').annotate(total=Sum('total_amount')).order_by('day')
    
    sales_labels = [entry['day'] for entry in sales_data]
    sales_totals = [entry['total'] for entry in sales_data]
    
    return sales_labels, sales_totals



def get_monthly_orders_data(start_date, end_date):
    orders_data = Order.objects.filter(created_at__range=[start_date, end_date]).extra(
        {'day': "date(created_at)"}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    orders_labels = [entry['day'] for entry in orders_data]
    orders_counts = [entry['count'] for entry in orders_data]
    
    return orders_labels, orders_counts


def get_yearly_sales_data(start_date, end_date):
    sales_data = Order.objects.filter(created_at__range=[start_date, end_date]).extra(
        {'month': "TO_CHAR(created_at, 'YYYY-MM')"}
    ).values('month').annotate(total=Sum('total_amount')).order_by('month')
    
    sales_labels = [entry['month'] for entry in sales_data]
    sales_totals = [entry['total'] for entry in sales_data]
    
    return sales_labels, sales_totals


def get_yearly_orders_data(start_date, end_date):
    orders_data = Order.objects.filter(created_at__range=[start_date, end_date]).extra(
        {'month': "TO_CHAR(created_at, 'YYYY-MM')"}
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    orders_labels = [entry['month'] for entry in orders_data]
    orders_counts = [entry['count'] for entry in orders_data]
    
    return orders_labels, orders_counts


def most_sold_category(request):
    most_sold_category_data = (
        OrderItem.objects.values('product__category__category_name')
        .annotate(total_sold=Count('quantity'))
        .order_by('-total_sold')
    )

    categories = [item['product__category__category_name'] for item in most_sold_category_data]
    quantities = [item['total_sold'] for item in most_sold_category_data]

    return JsonResponse({
        'labels': categories,
        'data': quantities,
    })


def admin_dashboard(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        report_type = request.GET.get('report_type', 'monthly')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Convert date strings to datetime objects
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except (TypeError, ValueError):
            start_date = timezone.now() - timedelta(days=30)
            end_date = timezone.now()

        if report_type == 'monthly':
            sales_labels, sales_data = get_monthly_sales_data(start_date, end_date)
            orders_labels, orders_data = get_monthly_orders_data(start_date, end_date)
        else:
            sales_labels, sales_data = get_yearly_sales_data(start_date, end_date)
            orders_labels, orders_data = get_yearly_orders_data(start_date, end_date)
        
        # Fetch most sold category data
        most_sold_category_data = most_sold_category(request)
        category_data = json.loads(most_sold_category_data.content)  # Parse JSON response

        data = {
            'sales_labels': sales_labels,
            'sales_data': sales_data,
            'orders_labels': orders_labels,
            'orders_data': orders_data,
            'category_labels': category_data['labels'],
            'category_data': category_data['data'],
        }
        return JsonResponse(data)

    total_sales = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_coupon = Order.objects.aggregate(Sum('coupon_discount'))['coupon_discount__sum'] or 0
    total_orders = Order.objects.count()

    context = {
        'total_sales': total_sales,
        'total_coupon': total_coupon,
        'total_orders': total_orders,
    }

    return render(request, 'ahome.html', context)

def generate_ledger_pdf(start_date=None, end_date=None):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ledger_book.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['Title'],
        fontSize=16,
        alignment=1,  # Center
        spaceAfter=12,
        textColor=colors.darkblue
    )
    header_style = ParagraphStyle(
        name='HeaderStyle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=6,
        textColor=colors.black
    )
    normal_style = ParagraphStyle(
        name='NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=12,
        textColor=colors.black
    )
    table_header_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    # Title and Date Range
    elements.append(Paragraph("Ledger Book", title_style))
    elements.append(Paragraph(f"From: {start_date} To: {end_date}", normal_style))

    # Table Header
    data = [
        ['Order ID', 'User', 'Product Name', 'Quantity', 'Total Amount', 'Coupon Amount', 'Order Status', 'Order Date']
    ]

    # Fetch orders
    orders = Order.objects.filter(created_at__date__range=[start_date, end_date], status='Completed')

    if not orders:
        elements.append(Paragraph("No orders found for the given date range.", normal_style))
        
        # Add total summary section
        total_sales = 0
        total_coupon = 0
        total_orders = 0
        
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Summary", header_style))
        elements.append(Paragraph(f"Total Sales Amount: ${total_sales:.2f}", normal_style))
        elements.append(Paragraph(f"Total Coupon Discount: ${total_coupon:.2f}", normal_style))
        elements.append(Paragraph(f"Total Orders: {total_orders}", normal_style))
        
        doc.build(elements)
        buffer.seek(0)
        response.write(buffer.getvalue())
        buffer.close()
        return response

    # Initialize counters
    total_sales = 0
    total_coupon = 0
    total_orders = 0

    # Process each order
    for order in orders:
        total_orders += 1
        total_coupon += order.coupon_amount
        total_sales += order.total_amount

        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            data.append([
                str(order.id),
                order.user.username,
                item.product.product_name,
                item.quantity,
                f"${item.product.price * item.quantity:.2f}",
                f"${order.coupon_amount:.2f}",
                order.status,
                order.created_at.strftime('%Y-%m-%d')
            ])

    # Create Table
    table = Table(data)
    table.setStyle(table_header_style)
    elements.append(table)

    # Add total summary section
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Summary", header_style))
    elements.append(Paragraph(f"Total Sales Amount: ${total_sales:.2f}", normal_style))
    elements.append(Paragraph(f"Total Coupon Discount: ${total_coupon:.2f}", normal_style))
    elements.append(Paragraph(f"Total Orders: {total_orders}", normal_style))

    doc.build(elements)

    buffer.seek(0)
    response.write(buffer.getvalue())
    buffer.close()
    return response

def ledger_book(request):
    form = DateRangeForm(request.GET or None)

    # Check if the form is valid and dates are provided
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        # Check that end_date is after start_date
        if start_date > end_date:
            return HttpResponse("End date must be after start date.", content_type='text/plain')

        # Generate and return the PDF
        return generate_ledger_pdf(start_date, end_date)
    
    # Render the form if no dates are provided or form is invalid
    return render(request, 'ahome.html', {'form': form})


def brand_list(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if 'add_brand' in request.POST:  # Adding a brand
            if form.is_valid():
                form.save()
                messages.success(request, 'Brand added successfully!')
                return redirect('brand_list')
        elif 'edit_brand' in request.POST:  # Editing a brand
            brand_id = request.POST.get('brand_id')
            brand = get_object_or_404(Brand, id=brand_id)
            form = BrandForm(request.POST, request.FILES, instance=brand)
            if form.is_valid():
                form.save()
                messages.success(request, 'Brand updated successfully!')
                return redirect('brand_list')
        elif 'delete_brand' in request.POST:  # Deleting a brand
            brand_id = request.POST.get('brand_id')
            brand = get_object_or_404(Brand, id=brand_id)
            brand.delete()
            messages.success(request, 'Brand deleted successfully!')
            return redirect('brand_list')
    else:
        form = BrandForm()
    
    brands = Brand.objects.all()
    context = {
        'form': form,
        'brands': brands
    }
    return render(request, 'brand_list.html', context)

@require_POST
def delete_gallery_image(request, product_id):
    image_id = request.GET.get('image_id')
    try:
        image = ProductGallery.objects.get(id=image_id, product_id=product_id)
        image.delete()
        return JsonResponse({'success': True})
    except ProductGallery.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Image not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    

def available_dates(request):
    orders = Order.objects.all()
    if not orders:
        return JsonResponse({'min_date': '', 'max_date': ''})

    min_date = orders.order_by('created_at').first().created_at.date()
    max_date = orders.order_by('-created_at').first().created_at.date()

    # Add one day to max_date to allow the end date selection
    max_date += timedelta(days=1)

    return JsonResponse({'min_date': min_date.isoformat(), 'max_date': max_date.isoformat()})


def get_available_order_dates(request):
    min_date = Order.objects.aggregate(min_date=Min('created_at'))['min_date']
    max_date = Order.objects.aggregate(max_date=Max('created_at'))['max_date']

    if min_date and max_date:
        min_date = min_date.date()
        max_date = max_date.date()
    else:
        # Set default values if no orders exist
        today = timezone.now().date()
        min_date = today
        max_date = today

    return JsonResponse({
        'min_date': min_date.isoformat(),
        'max_date': max_date.isoformat()
    })