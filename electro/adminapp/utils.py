from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_ledger_pdf(start_date, end_date):
    # Create a byte stream buffer
    buffer = BytesIO()

    # Create a PDF object
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Write some content
    p.drawString(100, height - 100, f"Ledger Book from {start_date} to {end_date}")

    # Save the PDF file
    p.showPage()
    p.save()

    # Rewind the buffer
    buffer.seek(0)

    # Create an HTTP response with the PDF file
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ledger_book_{start_date}_to_{end_date}.pdf"'
    
    return response
