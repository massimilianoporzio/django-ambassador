from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_admin = False
        user.is_staff = False
        user.is_ambassador = False  # registro ambassador solo attraverso l'API ambassador
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_admin = True
        user.is_ambassador = False
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# Create your models here.
class User(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    is_ambassador = models.BooleanField(default=True)
    username = None

    USERNAME_FIELD = 'email'  # per dire che il campo 'email' è da usare come username per il login
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def name(self):
        return self.first_name + ' ' + self.last_name

    @property
    def revenue(self):
        orders = Order.objects.filter(user_id=self.pk, complete=True)
        return sum(o.ambassador_revenue for o in orders)

    # def save(self, *args, **kwargs):
    #     super(User, self).save()
    #     if self.password:
    #         self.set_password(self.password)
    #         super(User, self).save() SERVE SE VOGLIO FARE HASH DELLA PWD DA ADMIN


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, null=True)
    image = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def filter_title(self,s):
        return (s.lower() in self.title.lower())

    def filter_description(self,s):
        return (s.lower() in self.description.lower())


class Link(models.Model):
    code = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Order(models.Model):
    transaction_id = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    code = models.CharField(max_length=255)
    ambassador_email = models.CharField(max_length=255)
    # INDIRIZZO DI SPEDIZIONE PER L'ORDINE
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    zip = models.CharField(max_length=255, null=True)
    complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def name(self):
        return self.first_name + ' ' + self.last_name

    @property
    def ambassador_revenue(self):
        items = OrderItem.objects.filter(order_id=self.pk)
        return sum(i.ambassador_revenue for i in items)

    @property
    def admin_revenue(self):
        items = OrderItem.objects.filter(order_id=self.pk)
        return sum(i.admin_revenue for i in items)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product_title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    admin_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    ambassador_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

