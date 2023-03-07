from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    def __str__(self):
        return f'{self.user.username}-Profile'
class Contact(models.Model):
    name=models.CharField(max_length=200)
    email=models.EmailField()
    number=models.IntegerField()
    subject=models.CharField(max_length=200)
    message=models.TextField()
    
class sp_product(models.Model):
    id = models.AutoField
    name = models.CharField(max_length=100)
    link = models.URLField(max_length=200)
    image = models.ImageField(blank=True,upload_to='dbimg')

    def __str__(self):
        return self.name