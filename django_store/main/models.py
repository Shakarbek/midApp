from django.db import models

# Create your models here.
from auth_.models import Seller, User


class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name='Category'
        verbose_name_plural='Categories'
        ordering=['name']


class MainProductManager(models.Manager):
    def sort_by_category(self):
        return self.get_queryset().order_by('category')

    def produce(self):
        return self.get_queryset().filter(produced=True)


class Product(models.Model):
    name=models.CharField(max_length=200, null=True)
    price=models.IntegerField(null=True)
    category=models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    description=models.CharField(max_length=255, null=True)
    quantity=models.IntegerField(default=-1)
    produced=models.BooleanField(default=True)
    location=models.CharField(max_length=200, default="Almaty")
    seller=models.ForeignKey(Seller, on_delete=models.DO_NOTHING, related_name='sellers_products', default=1)
    objects = MainProductManager()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name='Product'
        verbose_name_plural='Products'
        ordering=['name']

class MainOrderManager(models.Manager):
    def create(self, customer, *args, **kwargs):
        if customer:
            order = self.model(customer=customer)
            order.save()
            return order
        else:
            raise ValueError('Some fields are not full')

    def add_product(self, product):
        if product:
            order=self.model
            order.products.add(product)
            order.save()
            return order
        else:
            raise ValueError('Some fields are not full')

class Order(models.Model):
    STATUS =(
        ('Pending', 'Pending'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered')
    )
    status=models.CharField(max_length=200, null=True, choices=STATUS)
    customer=models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='customer_order')
    products=models.ManyToManyField(Product, related_name='orders_products', blank=True)

    orders=MainOrderManager()

    def __str__(self):
        return f"Order: {self.pk}"

    class Meta:
        verbose_name='Order'
        verbose_name_plural='Orders'


