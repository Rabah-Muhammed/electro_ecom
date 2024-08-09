import uuid
from django.db import models
from django.contrib.auth.models import User
from PIL import Image

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    address_line_1 = models.CharField(blank=True,max_length=100)
    address_line_2 = models.CharField(blank=True,max_length=100)
    phone_number = models.CharField(max_length=50,null=True,blank=True)
    profile_picture = models.ImageField(blank=True,null=True,upload_to='photos/userprofile')
    city = models.CharField(blank=True,max_length=20)
    state = models.CharField(blank=True,max_length=20)
    country = models.CharField(blank=True,max_length=20)
    referral_code = models.CharField(max_length=50, unique=True, blank=True,null=True)  # Added field for referral code



    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)
        # Resize profile picture if larger than 200x200
        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            if img.height > 200 or img.width > 200:
                output_size = (200, 200)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)

    def __str__(self):
        return self.user.first_name

    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"

    def generate_referral_code(self):
        code = str(uuid.uuid4())[:8].upper()
        while UserProfile.objects.filter(referral_code=code).exists():
            code = str(uuid.uuid4())[:8].upper()
        return code

    
class Address(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='addresses')
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.address_line_1}, {self.city}"