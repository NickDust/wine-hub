from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("wine-list-api/wines", views.WineView.as_view(), name="wine-list"),
    path("wine-list-api/<int:pk>/", views.WineRetrieveUpdateDestroyView.as_view(), name="wine-update"),
    path("wine-list-api/dashboard/", views.DashBoardApiView.as_view(), name="dashboard"),
    path("wine-list-api/region/", views.RegionView.as_view(), name="wine-region"),
    path("wine-list-api/style/", views.StyleView.as_view(), name="wine-style"),
    path("wine-list-api/type/", views.StyleView.as_view(), name="wine-style"),
    path("wine-list-api/appelation/", views.AppellationView.as_view(), name="wine-appelation"),
    path("wine-list-api/detail/<int:pk>", views.WineRetrieveView.as_view(), name="wine-detail"),
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
    path("wine-list-api/sale/", views.RegisterSaleView.as_view(), name="sale")
]
