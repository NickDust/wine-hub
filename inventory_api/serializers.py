from rest_framework import serializers
from .models import WineModel, RegionModel, WineTypeModel, WineStyleModel, AppellationModel, SaleModel
from django.contrib.auth.models import User
from accounts.models import UserProfile


class WineSerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField()
    type = serializers.StringRelatedField()
    style = serializers.StringRelatedField()
    appelation = serializers.StringRelatedField()
    added_by = serializers.StringRelatedField()
    revenue = serializers.SerializerMethodField()
    
    def get_revenue(self, obj: WineModel):
        return obj.revenue()
    
    class Meta:
        model = WineModel
        fields = "__all__"
        read_only_fields = ["revenue"]
    
class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionModel
        fields = "__all__"

class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WineTypeModel
        fields = "__all__"

class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WineStyleModel
        fields = "__all__"

class AppellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppellationModel
        fields = "__all__"

class RegisterSaleSerializer(serializers.Serializer):
    wine_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class SaleSerializer(serializers.ModelSerializer):
    return_to_stock = serializers.BooleanField(default=False, write_only=True)
    class Meta:
        model = SaleModel
        read_only_fields = ["timestamp", "user"]
        fields = "__all__"
        depth = 1

class RestockSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, required=True)
    note = serializers.CharField(required=False, allow_blank=True)
