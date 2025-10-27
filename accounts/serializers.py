from rest_framework import serializers
from . models import Profile
from django.contrib.auth import password_validation, get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
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
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, default=ROLE_CUSTOMER)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'password', 'confirm_password']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email Already Exists")

        if not email.endswith("@gmail.com"):
            raise serializers.ValidationError("Email must end with @gmail.com")

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        # ✅ Use create_user instead of create
        user = User.objects.create_user(password=password, **validated_data)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("phone", "address", "city", "country", "license_number", "extra")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'is_active', 'date_joined', 'profile']




class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value
    

