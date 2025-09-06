from django.test import TestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from inventory_api.models import (
    RegionModel, WineTypeModel, WineStyleModel, AppellationModel, WineModel, SaleModel
)
from rest_framework.test import APIClient
from rest_framework import status

class RegisterSale_Restock_Test(TestCase):

    def setUp(self):

        # Url
        self.client = APIClient()
        self.url = "/wine-list-api/sale/"

        # User Token
        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        # Foreign key
        self.region = RegionModel.objects.create(country="Italy", region="Tuscany")
        self.wtype = WineTypeModel.objects.create(type="red")
        self.wstyle = WineStyleModel.objects.create(style="dry", body="full")
        self.appellation = AppellationModel.objects.create(name="DOC")

        # Wine
        self.wine = WineModel.objects.create(
            name="Chianti",
            year=2024,
            region=self.region,
            type=self.wtype,
            style=self.wstyle,
            appellation=self.appellation,
            price=5,
            retail_price=12.5,
            stock=20,
            quantity_sold=0,
            added_by=self.user,
        )

        # Data
        self.data_ok = {
            "wine_id": self.wine.id,
            "quantity": 2
        }

        self.data_not_ok = {
            "wine_id": self.wine.id,
            "quantity": 30
        }

    def test_sale_ok(self):

        # Url
        response = self.client.post(self.url, self.data_ok, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Sale created
        sale = SaleModel.objects.first()
        self.assertEqual(sale.quantity_sold, 2)
        self.assertEqual(sale.wine.name, "Chianti")
        self.assertEqual(sale.user.username, "tester")

        # Revenue created
        self.wine.refresh_from_db()
        self.assertEqual(self.wine.revenue(), 25)

        # Stock decreased
        self.assertEqual(self.wine.quantity_sold, sale.quantity_sold)
        self.assertEqual(self.wine.stock, 18)

    def test_sale_not_ok(self):

        # Sell more wine than the stock
        response = self.client.post(self.url, self.data_not_ok, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Stock control
        self.assertEqual(self.wine.stock, 20)

        # Sale not created
        self.assertEqual(SaleModel.objects.count(), 0)

        # Revenue check
        self.wine.refresh_from_db()
        self.assertEqual(self.wine.revenue(), 0)

    def test_refund(self):
        # refund
        data = {
            "refund_qty": 1,

        }

        # Making the sale
        response = self.client.post(self.url, self.data_ok, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        sale = SaleModel.objects.first()

        # Role changing for Authentication
        profile = self.user.userprofile
        profile.role = "admin"
        profile.save()
        self.assertEqual(profile.role, "admin")

        # Refund
        r_response = self.client.post(f"/wine-list-api/{sale.id}/sales/refund", data, format="json")
        self.assertEqual(r_response.status_code, status.HTTP_200_OK)

        # Stock control
        self.wine.refresh_from_db()
        self.assertEqual(self.wine.stock, 18)

    def test_refund_restock(self):
        # Refund and restock
        data = {
            "refund_qty": 1,
            "return_to_stock": True
        }

        # Making the sale
        response = self.client.post(self.url, self.data_ok, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        sale = SaleModel.objects.first()

        # Role changing for Authentication
        profile = self.user.userprofile
        profile.role = "admin"
        profile.save()
        self.assertEqual(profile.role, "admin")

        # Refund
        r_response = self.client.post(f"/wine-list-api/{sale.id}/sales/refund", data, format="json")
        self.assertEqual(r_response.status_code, status.HTTP_200_OK)

        # Stock control with return to stock
        self.wine.refresh_from_db()
        self.assertEqual(self.wine.stock, 19)
        
