from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path("top-selling/", views.TopSellingView.as_view(), name="top-selling"),
    path("revenue/", views.RevenueFilterView.as_view(), name="revenue"),
    path("best-employee/", views.BestEmployeeView.as_view(), name="best-employee"),
    path("least-selling/", views.LeastSellingView.as_view(), name="least-selling"),
    path("unsold-wines/", views.UnsoldWineView.as_view(), name="unsold-wines"),
    path("quarter-trend/", views.QuarterTrendSalesView.as_view(), name="quarter-trend"),
    path("low-stock/", views.LowStockView.as_view(), name="low-stock")
]

router = DefaultRouter()
router.register(r"exports", views.ExportViewSet, basename="exports")

urlpatterns += [
    path("", include(router.urls)),
]