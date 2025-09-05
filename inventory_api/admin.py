from django.contrib import admin
from .models import *

class InventoryAdmin(admin.ModelAdmin):
    list_filter = ["region", "year", "type", "appellation"]
    search_fields = ["name"]
    readonly_fields = ["id"]
    fieldsets = (
        ("Main Information", {
            "fields": ("id", "name", "year", "region", "appellation")
        }),
("Characteristic", {
    "fields": ("type", "style")
}),
("stock",{
    "fields": ("price", "stock", "retail_price", "quantity_sold")
})
)
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)

class SaleAdmin(admin.ModelAdmin):
    list_display = ["id", "wine", "user", "quantity_sold", "timestamp"]
    readonly_fields = ["timestamp"]  

admin.site.register(WineModel, InventoryAdmin)
admin.site.register(RegionModel)
admin.site.register(WineTypeModel)
admin.site.register(WineStyleModel)
admin.site.register(AppellationModel)
admin.site.register(SaleModel, SaleAdmin)


