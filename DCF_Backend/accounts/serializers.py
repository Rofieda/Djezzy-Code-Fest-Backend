from rest_framework import serializers

from .models import User 

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import User , Volunteer , Charity

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model





class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role  # Add custom claims
        return token


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        attrs['user'] = user  # Add user to validated data
        return attrs

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        # Initialize an error dictionary
        errors = {}

        # Check if email is missing
        if not attrs.get('email'):
            errors['email'] = ['This field is required.']

        # Check if password is missing
        if not attrs.get('password'):
            errors['password'] = ['This field is required.']

        # Raise ValidationError if there are errors
        if errors:
            raise serializers.ValidationError(errors)

        return attrs  # Return validated attributes

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


   


# Serializer for logging out the user

class LogoutUserSerializer(serializers.Serializer):
    refresh = serializers.CharField()  # Expecting refresh token in the request body

    default_error_messages = {
        'bad_token': 'Token is expired or invalid.'
    }

    def validate(self, attrs):
        refresh = attrs.get('refresh')
        if not refresh:
            raise ValidationError({"refresh": "This field is required."})
        self.token = refresh
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()  # Blacklist the token (requires blacklisting enabled in SimpleJWT)
        except TokenError:
            raise ValidationError(self.default_error_messages['bad_token'])





class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},  #  password is write-only
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'patient')  
        )
        return user
    



#############################################################################################" 



class VolunteerRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Volunteer
        # Fields for volunteer registration including volunteer-specific fields and user fields
        fields = ('full_name', 'phone', 'address', 'email', 'password')

    def validate_email(self, value):
        # Check if a user with this email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value
    


    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        # Create the User instance with role set to 'volunteer'
        user = User.objects.create(email=email, role='volunteer')
        user.set_password(password)
        user.save()
        # Create the Volunteer profile and associate it with the user
        volunteer = Volunteer.objects.create(user=user, **validated_data)
        return volunteer




class CharityRegistrationSerializer(serializers.ModelSerializer):
    # Include email and password for the user
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Charity
        # Fields for charity registration including charity-specific fields and user fields
        fields = ('name', 'description', 'category', 'location', 'email', 'password')
    
    def validate_email(self, value):
        # Check if a user with this email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        print("Creating user with email:", email)  # Debug statement
        # Create the User instance with role set to 'charity'
        user = User.objects.create(email=email, role='charity')
        user.set_password(password)
        user.save()
        # Create the Charity profile and associate it with the user
        charity = Charity.objects.create(user=user, **validated_data)
        print ("created charity : ", charity)
        return charity 