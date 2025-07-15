import random, string, os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

# Create your models here.

def user_picture_upload_path(instance, filename):
    # Define the folder structure and file name for uploaded user pictures
    # Here, we are storing pictures in a folder named 'user_pictures' with a filename based on the user's email
    # if instance.email in filename:
    #     return filename
    return f'user_pictures/{instance.email}/{filename}'

class User(AbstractUser):
    email = models.EmailField(unique = True)
    coins = models.IntegerField(validators=[MinValueValidator(0)], null=True, default=0)
    contact_number=models.BigIntegerField(null=True,blank=True,validators=[MinValueValidator(0),MaxValueValidator(999999999999999)])
    spin_left = models.IntegerField(validators=[MinValueValidator(0)], null=True, default=5)
    ref_code = models.CharField(max_length=50, unique=True)
    created_on=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    full_name = models.CharField(max_length=255)
    otp = models.IntegerField(blank=True, null=True)
    failedLoginCount = models.IntegerField(blank=True, null=True,default=0)
    otpgenerationTime = models.DateTimeField(blank=True, null=True)
    scratch = models.IntegerField(validators=[MinValueValidator(0)], null=True, default=5)
    otp_verified = models.BooleanField(default=False)
    picture = models.ImageField(upload_to=user_picture_upload_path, null=True, blank=True)
    

    def save(self, *args, **kwargs):
        # Generate a random 4-digit code
        random_digits = ''.join(random.choices(string.digits, k=4))
        
        # Create the ref_code using the first 3 letters of full_name and the random digits
        if not self.ref_code:
            if self.full_name:
                # Use the first 3 letters of full_name (or fewer if full_name is shorter)
                ref_code_prefix = self.full_name[:3].upper()
            else:
                # Handle cases where full_name is not provided
                ref_code_prefix = 'XXX'  # You can choose any default prefix here
            
            # Combine the prefix and random digits to create the ref_code
            self.ref_code = ref_code_prefix + random_digits


        # if self.picture:
        #     image = Image.open(self.picture)
        #     output_buffer = BytesIO()

        #     # Initialize the quality to achieve the target size of 500KB
        #     target_size = 500 * 1024  # 500 KB in bytes
        #     quality = 70  # Starting quality (adjust as needed)

        #     while True:
        #         # Compress the image with the current quality
        #         image.save(output_buffer, format=image.format, quality=quality)

        #         # Check the current size
        #         image_size = len(output_buffer.getvalue())

        #         # Check if the image size is below the target size
        #         if image_size <= target_size:
        #             break

        #         # Reduce the quality and try again
        #         quality -= 10

        #         # Reset the buffer for the next iteration
        #         output_buffer.seek(0)
        #         output_buffer.truncate()

        #     # Save the compressed image back to the field using ContentFile
        #     self.picture.save(self.picture.name, ContentFile(output_buffer.getvalue()), save=False)

        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Users'
        verbose_name_plural = 'Users'


class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_1 = models.BooleanField(default=False)
    quiz_2 = models.BooleanField(default=False)
    quiz_3 = models.BooleanField(default=False)
    quiz_4 = models.BooleanField(default=False)
    quiz_5 = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quiz'
    
    def save(self, *args, **kwargs):
        # Check the values of quiz_2, quiz_3, quiz_4, and quiz_5
        # Update quiz_1 accordingly
        if self.quiz_5:
            if not self.quiz_1 or not self.quiz_2 or not self.quiz_3 or not self.quiz_4:
                raise ValueError("Complete all previous quizzes before starting quiz 5")
        elif self.quiz_4:
            if not self.quiz_1 or not self.quiz_2 or not self.quiz_3:
                raise ValueError("Complete all previous quizzes before starting quiz 4")
        elif self.quiz_3:
            if not self.quiz_1 or not self.quiz_2:
                raise ValueError("Complete all previous quizzes before starting quiz 3")
        elif self.quiz_2:
            if not self.quiz_1:
                raise ValueError("Complete quiz 1 before starting quiz 2")

        super(Quiz, self).save(*args, **kwargs)


class Pred(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pred_1 = models.BooleanField(default=False)
    pred_2 = models.BooleanField(default=False)
    pred_3 = models.BooleanField(default=False)
    pred_4 = models.BooleanField(default=False)
    pred_5 = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Prediction'
        verbose_name_plural = 'Prediction'
    
    def save(self, *args, **kwargs):
        # Check the values of pred_2, pred_3, pred_4, and pred_5
        # Update pred_1 accordingly
        if self.pred_5:
            if not self.pred_1 or not self.pred_2 or not self.pred_3 or not self.pred_4:
                raise ValueError("Complete all previous predictions before starting pred 5")
        elif self.pred_4:
            if not self.pred_1 or not self.pred_2 or not self.pred_3:
                raise ValueError("Complete all previous predictions before starting pred 4")
        elif self.pred_3:
            if not self.pred_1 or not self.pred_2:
                raise ValueError("Complete all previous predictions before starting pred 3")
        elif self.pred_2:
            if not self.pred_1:
                raise ValueError("Complete pred 1 before starting pred 2")

        super(Pred, self).save(*args, **kwargs)


class AccessTokensBlackList(models.Model):
    user = models.ForeignKey(User, on_delete = models.SET_NULL, null = True, blank = False)
    jti = models.CharField(unique = True, max_length=255)
    token = models.TextField()
    expires_at = models.DateTimeField()
    class Meta:
        db_table = "AccessTokensBlacklist"

    def __str__(self):
        return self.token



transaction_status = (
   ("Pending" ,"Pending"),
   ("Successful" ,"Successful"),
   ("Failed" ,"Failed"),
   ("Refunded","Refunded")
)

payment_type = (
    ("Paytm","Paytm"),
    ("Gpay","Gpay"),
    ("Phonepe","Phonepe"))

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_number=models.BigIntegerField(null=True,blank=True,validators=[MinValueValidator(0),MaxValueValidator(999999999999999)])
    amount = models.IntegerField()
    status = models.CharField(max_length=255, choices = transaction_status, default = "Pending")
    payment_type = models.CharField(max_length = 255, choices = payment_type)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now = True, null = True, blank = True)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def save(self, *args, **kwargs):
        # Set the phone_number to the user's contact_number before saving
        self.contact_number = self.user.contact_number
        super(Transaction, self).save(*args, **kwargs)

class DynamicCoins(models.Model):
    name = models.CharField(max_length=255)
    coins = models.IntegerField(validators=[MinValueValidator(0)])
    time_in_seconds = models.IntegerField(validators=[MinValueValidator(0)])
    type = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now = True, null = True, blank = True)

    class Meta:
        verbose_name = 'Dynamic Coins'
        verbose_name_plural = 'Dynamic Coins'


class DynamicLinks(models.Model):
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Dynamic Links'
        verbose_name_plural = 'Dynamic Links'


class CoinsPayment(models.Model):
    coins = models.IntegerField(validators=[MinValueValidator(0)])
    funds = models.IntegerField(validators=[MinValueValidator(0)])
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now = True, null = True, blank = True)

    class Meta:
        verbose_name  = 'Coins Payment'
        verbose_name_plural = 'Coins Payment'


def banner_picture_upload_path(instance, filename):
    # Define the folder structure and file name for uploaded user pictures
    # Here, we are storing pictures in a folder named 'banners_picture' with a filename based on the user's email
    # if instance.name in filename:
    #     return filename
    return f'banner_pictures/{instance.name}/{filename}'


class Banners(models.Model):
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    picture = models.ImageField(upload_to=banner_picture_upload_path, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now = True, null = True, blank = True)

    def save(self, *args, **kwargs):
        # Check if a new picture has been uploaded
        if self.pk:
            try:
                old_banner = Banners.objects.get(pk=self.pk)
                if self.picture and old_banner.picture and self.picture != old_banner.picture:
                    # A new picture has been uploaded, and an old picture exists
                    # Delete the old picture
                    if os.path.isfile(old_banner.picture.path):
                        os.remove(old_banner.picture.path)
            except Banners.DoesNotExist:
                pass

        super(Banners, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'