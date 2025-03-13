from django.db import models




from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


from django.contrib.auth.models import BaseUserManager



# Create your models here.
class CustomUserManager(BaseUserManager):
    """
    Custom user manager that supports user creation with only email, password, and role.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  # Remove the default username field
    email = models.EmailField(max_length=100, unique=True,default="email@example.com")
    role = models.CharField(
        max_length=20, 
       choices=[
            ('admin', 'Admin'),
            ('volunteer', 'Volunteer'),
            ('charity', 'Charity'),
            # You may still include other roles if needed.
        ],  
        default='admin'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use email as the primary identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Only email is required for user creation

    # Add unique related_name for groups and permissions to avoid conflicts
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Unique related_name to avoid conflicts
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )

    # Override the default related_name for user_permissions to avoid conflicts
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',  
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomUserManager()  # Link to custom manager

    def __str__(self):
        return self.email
    






class Volunteer(models.Model):
    full_name = models.CharField(max_length=100, blank=False, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='volunteer_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=300, blank=True, null=True)
    points = models.IntegerField(default=0) 




class Charity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='charity_profile')
    CATEGORY_CHOICES = [
        ('charity', 'Charity'),
        ('restaurant_rahma', 'Restaurant Rahma'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField ( max_length=300 )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)





class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/')
    created_at = models.DateTimeField(auto_now_add=True) 


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)



class Stock(models.Model):
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)



class Event(models.Model):
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    location = models.CharField ( max_length=300 )
    stock_allocation = models.OneToOneField(Stock, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    


class Task(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tasks")
    task_name = models.CharField(max_length=255)
    description = models.TextField()
    volunteer_limit = models.IntegerField(default=1)  


class ChatGroup(models.Model): 
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, through='ChatGroupMembership')


class ChatGroupMembership(models.Model):
    members = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
   
    chat_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE) 
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)



class CharityAdmin(models.Model):
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, related_name='admins')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='charity_admin_profile')
    assigned_at = models.DateTimeField(auto_now_add=True) 



class Leaderboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='leaderboard')
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"Leaderboard: {self.user.email} - {self.points} points"
    


    
class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    description = models.TextField()
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reward for {self.user.email} ({self.points} points)"


class Forum(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='forums')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Forum for {self.event.name} created at {self.created_at}"