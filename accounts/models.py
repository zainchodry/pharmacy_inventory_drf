from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone



class UserManager(BaseUserManager):
    def create_user(self, email,password = None,  **extra_fields):
        if not email:
            raise ValueError("Email Must Be Set")
        
        email = self.normalize_email(email)
        user = self.model(email = email,password = password, **extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user
    

    def create_superuser(self, email, password = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Is-Staff Must Be True")
        
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("is_superuser is must be True")
        
        return self.create_user(email, password, **extra_fields)
    


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_ADMIN = "admin"
    ROLE_PHARMACIST = "pharmacist"
    ROLE_SUPPLIER = "supplier"
    ROLE_CUSTOMER = "customer"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_PHARMACIST, "Pharmacist"),
        (ROLE_SUPPLIER, "Supplier"),
        (ROLE_CUSTOMER, "Customer"),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120, blank=True)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email    




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    license_number = models.CharField(max_length=120, blank=True)  
    extra = models.JSONField(default=dict, blank=True)  

    def __str__(self):
        return f"Profile of {self.user.email}"