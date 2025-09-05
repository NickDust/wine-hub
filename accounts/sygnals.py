from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserProfile, LogModel
from inventory_api.models import SaleModel, WineModel
from django.contrib.auth.signals import user_logged_in, user_logged_out


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def user_role(sender, instance=None, created=False, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def log_user_registeration(sender, instance=None, created=False, **kwargs):
    if created:
        LogModel.objects.create(user=instance, action="user_registered")

@receiver(post_save, sender=SaleModel)
def log_sale_created(sender, instance=None, created=False, **kwargs):
    if created:
        LogModel.objects.create(user=instance.user, action="sale_created")

@receiver(post_delete, sender=WineModel)
def log_wine_deleted(sender, instance=None, created=False, **kwargs):
    if instance.added_by:
        LogModel.objects.create(user=instance.added_by, action="wine_deleted", details=f"deleted wine: {instance.name}")

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    LogModel.objects.create(user=user, action="user_logged_in", details=f"{user.username} Logged in.")

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    LogModel.objects.create(user=user, action="out", details=f"{user.username} Logged out.")
