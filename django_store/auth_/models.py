from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class MainUserManager(BaseUserManager):

    def customers(self):
        return super().get_queryset().filter(is_seller=False)

    def sellers(self):
        return super().get_queryset().filter(is_seller=True)

    # def _create_user(self, email, password, **extra_fields):
    #     if not email:
    #         raise ValueError('The given email must be set')
    #     email = self.normalize_email(email)
    #     user = self.model(email=email, **extra_fields)
    #     user.set_password(password)
    #     user.save(using=self._db)
    #     return user
    #
    # def create_user(self, email, password=None, **extra_fields):
    #     extra_fields.setdefault('is_staff', False)
    #     extra_fields.setdefault('is_superuser', False)
    #     return self._create_user(email, password, **extra_fields)

    def _create_user(self, username, email, password, is_seller, **extra_fields):
        if not username:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, is_seller=is_seller, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, email=None, password=None, is_seller=False, location="", **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)

        if is_seller:
            user = self._create_user(username, email, password, is_seller=True, **extra_fields )
            seller = Seller.objects.create(user=user, location=location)
        return self._create_user(username, email, password, is_seller=False, **extra_fields)
    #
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)




class User(AbstractUser):
    # user_types = (
    #     (0, 'Customer'),
    #     (1, 'Admin'),
    #     (2, 'Seller'),
    # )
    age = models.IntegerField(default=0, blank=True)
    phone_number = models.IntegerField(blank=True, default=8)
    location = models.CharField(max_length=200, blank=True, null=True)
    # user_type = models.PositiveSmallIntegerField(choices=user_types, default=0)
    is_seller= models.BooleanField(default=False)
    users = MainUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username', ]

    def __str__(self):
        return f"User: {self.username}"

    def fire_seller(self):
        self.users.Seller.status_inactive()
        self.save()

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller')

    location=models.CharField(max_length=200, default='Almaty')
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return f"Seller: {self.user.username}"

    class Meta:
        verbose_name='Seller'
        verbose_name_plural='Sellers'

    def status_active(self):
        self.is_active = True
        self.save()

    def status_inactive(self):
        self.is_active=False
        self.save()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    products = models.ManyToManyField('main.Product', blank=True)

    def __str__(self):
        return f"{self.user.username}"

