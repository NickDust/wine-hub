from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE = {
        "admin": "Admin",
        "manager": "Manager",
        "staff": "Staff"
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField( max_length=20, choices=ROLE)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class LogModel(models.Model):
    ACTION_CHOICES = [
        ('sale_created', 'Sale Created'),
        ('user_logged_in', 'User Logged In'),
        ("user_logged_out", "User Logged Out"),
        ('user_registered', 'User Registered'),
        ('wine_deleted', 'Wine Deleted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)
