from django.db import models
from django.core.validators import MaxValueValidator
from datetime import datetime
from django.contrib.auth.models import User

class RegionModel(models.Model):
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.country}-{self.region}"
    
    class Meta:
         constraints = [
            models.UniqueConstraint(fields=["country", "region"], name="unique-country-region")
        ]

class WineTypeModel(models.Model):
    TYPE_ = {
        "sparkling": "sparkling",
        "fortified": "Fortified",
        "dessert": "Dessert",
        "red": "Red",
        "white": "White",
        "rose'": "Rose'"
    }

    type = models.CharField(max_length=50, choices= TYPE_, unique=True)

    def __str__(self):
        return self.type

class WineStyleModel(models.Model):
    SWETTNESS = {
        "dry": "Dry",
        "off-dry": "Off-dry",
        "sweet": "Sweet"
    }

    BODY = {
        "light": "Ligh-Bodied",
        "medium": "Medium-Bodied",
        "full": "Full-Bodied"
    }

    style = models.CharField(max_length=50, choices= SWETTNESS)
    body = models.CharField( max_length=50, choices= BODY)

    def __str__(self):
        return f"{self.style}-{self.body}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["style", "body"], name="unique-style-body")
        ]
    
class AppellationModel(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class WineModel(models.Model):
    name = models.CharField(max_length=150)
    year = models.PositiveIntegerField(validators=[MaxValueValidator(datetime.now().year)], verbose_name ="Year of Production")
    region = models.ForeignKey(RegionModel, on_delete=models.PROTECT)
    type = models.ForeignKey(WineTypeModel, on_delete=models.PROTECT, verbose_name = "Wine Type")
    style = models.ForeignKey(WineStyleModel, on_delete=models.PROTECT, verbose_name = "Style & Body")
    appellation = models.ForeignKey(AppellationModel, on_delete=models.PROTECT, verbose_name= "Appelation")
    added_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name= "added by")
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0, verbose_name="quantity")
    retail_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name= "retail price")
    quantity_sold = models.PositiveIntegerField(default=0, verbose_name="quantity sold")

    def revenue(self):
        if self.retail_price is not None:
            return self.retail_price * self.quantity_sold
        else:
            return 0

    def __str__(self):
        return f"{self.name}({self.year})-{self.price}£"
    
class SaleModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    wine = models.ForeignKey(WineModel, on_delete=models.PROTECT, verbose_name="Wine")
    quantity_sold = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}"
