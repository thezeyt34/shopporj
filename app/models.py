import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# ================= USER =================
class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

    def get_by_natural_key(self, phone_number):
        return self.get(phone_number=phone_number)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number


# ================= CATEGORY =================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.IntegerField(default=0)  # 🔥 новое поле

    def __str__(self):
        return self.name


# ================= PRODUCT =================
# ================= PRODUCT =================
class Product(models.Model):
    TYPE = (
        ('dona', 'Dona'),
        ('kg', 'Kg'),
    )

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # 🔥 ФАЙЛ (если загружаешь)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    # 🔥 URL (если вставляешь ссылку)
    image_url = models.URLField(blank=True, null=True)

    quantity = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)

    type = models.CharField(max_length=10, choices=TYPE, default='dona')

    created_at = models.DateTimeField(auto_now_add=True)

    def get_image(self):
        """
        Универсально возвращает картинку:
        сначала файл, потом URL
        """
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return None

    def __str__(self):
        return self.name

# ================= CART =================
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.phone_number} - {self.product.name}"


# ================= ORDER =================
class Order(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Tayyorlanmoqda'),
        ('ready', 'Tayyor'),
        ('delivered', 'Yetkazildi'),
        ('cancelled', 'Bekor qilingan'),
    )

    order_code = models.CharField(max_length=50, unique=True, blank=True)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    comment = models.TextField(blank=True)

    total_price = models.IntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = f"XOZ-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_code


# ================= ORDER ITEM =================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)
    total_price = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"