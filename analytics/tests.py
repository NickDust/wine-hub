from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from inventory_api.models import (
    RegionModel, WineTypeModel, WineStyleModel, AppellationModel, WineModel, SaleModel
)
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

class AnalyticsTest(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.client = APIClient()

        cls.data_users = [{
            "username": "Giorgio",
            "password": "Password123",
            "password2": "Password123"
            },{
            "username": "Marco",
            "password": "Password12",
            "password2": "Password12"
            },{
            "username": "Sasha",
            "password": "Password1",
            "password2": "Password1"
            }]
        

        # Users
        cls.client.post("/accounts/register/", data= cls.data_users[0], format="json")
        cls.user1 = User.objects.get(username="Giorgio")
        profile = cls.user1.userprofile
        profile.role = "admin"
        profile.save()
        cls.client.post("/accounts/register/", data= cls.data_users[1], format="json")
        cls.user2 = User.objects.get(username="Marco")
        profile1 = cls.user2.userprofile
        profile1.role = "manager"
        profile1.save()
        cls.client.post("/accounts/register/", data= cls.data_users[2], format="json") 
        cls.user3 = User.objects.get(username="Sasha") # default "staff"
        
        
        #Tokens
        cls.tokens = {}
        for user in User.objects.all():
            token = Token.objects.get(user=user)
            cls.tokens[user.username] = token.key

        # Foreign keys 
        cls.region = RegionModel.objects.create(country="Italy", region="Tuscany")
        cls.wtype = WineTypeModel.objects.create(type="red")
        cls.wstyle = WineStyleModel.objects.create(style="dry", body="full")
        cls.appellation = AppellationModel.objects.create(name="DOC")

        # Wines
        cls.wine1 = WineModel.objects.create(
            name="Chianti Classico",
            year=2020,
            region=cls.region,
            type=cls.wtype,
            style=cls.wstyle,
            appellation=cls.appellation,
            price=8,
            retail_price=15,
            stock=5,
            quantity_sold=0,
            added_by=cls.user1
        )

        cls.wine2 = WineModel.objects.create(
            name="Barolo",
            year=2019,
            region=cls.region,
            type=cls.wtype,
            style=cls.wstyle,
            appellation=cls.appellation,
            price=20,
            retail_price=40,
            stock=10,
            quantity_sold=0,
            added_by=cls.user2
        )

        cls.wine3 = WineModel.objects.create(
            name="Montepulciano d'Abruzzo",
            year=2021,
            region=cls.region,
            type=cls.wtype,
            style=cls.wstyle,
            appellation=cls.appellation,
            price=6,
            retail_price=12,
            stock=45,
            quantity_sold=0,
            added_by=cls.user3
        )

        cls.wine4 = WineModel.objects.create(
            name="Brunello di Montalcino",
            year=2018,
            region=cls.region,
            type=cls.wtype,
            style=cls.wstyle,
            appellation=cls.appellation,
            price=25,
            retail_price=60,
            stock=20,
            quantity_sold=0,
            added_by=cls.user1
        )

        # Sales
        
        cls.client.credentials(HTTP_AUTHORIZATION=f"Token {cls.tokens['Giorgio']}")
        cls.client.post("/wine-list-api/sale/", {"wine_id": cls.wine1.id, "quantity": 3}, format="json")
        cls.client.credentials(HTTP_AUTHORIZATION=f"Token {cls.tokens['Giorgio']}")
        cls.client.post("/wine-list-api/sale/", {"wine_id": cls.wine2.id, "quantity": 3}, format="json")
        cls.client.credentials(HTTP_AUTHORIZATION=f"Token {cls.tokens['Sasha']}")
        cls.client.post("/wine-list-api/sale/", {"wine_id": cls.wine2.id, "quantity": 5}, format="json")
        cls.client.credentials(HTTP_AUTHORIZATION=f"Token {cls.tokens['Marco']}")
        cls.client.post("/wine-list-api/sale/", {"wine_id": cls.wine3.id, "quantity": 15}, format="json")

        now = timezone.now()
        SaleModel.objects.create(wine=cls.wine1 , user=cls.user1, quantity_sold=3, timestamp=now - timedelta(days=5))
        SaleModel.objects.create(wine=cls.wine1 , user=cls.user2, quantity_sold=2, timestamp=now)  
        SaleModel.objects.create(wine=cls.wine2 , user=cls.user3, quantity_sold=1, timestamp=now - timedelta(days=40))  
        SaleModel.objects.create(wine=cls.wine3 , user=cls.user1, quantity_sold=4, timestamp=now - timedelta(days=2))

    def test_unsold_wines(self):
        
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.tokens["Giorgio"]}")
        response = self.client.get("/analytics/unsold-wines/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Brunello di Montalcino", [wine["name"] for wine in response.data])

        # sold wine not in list
        self.assertNotIn("Chianti Classico", [wine["name"] for wine in response.data])
    
    def test_top_selling(self):

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.tokens["Giorgio"]}")
        response = self.client.get("/analytics/top-selling/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual("Montepulciano d'Abruzzo", data["name"])

        # not top selling
        self.assertNotEqual("Chianti Classico", data["name"])

    def test_revenue_filter(self):

        # No filters (30 days default)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.tokens["Giorgio"]}")
        response = self.client.get("/analytics/revenue/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("30", response.data["message"])
        
        # filter days 
        response = self.client.get("/analytics/revenue/?days=45")
        self.assertIn("45", response.data["message"])

        #filter wine id 
        response = self.client.get("/analytics/revenue/?wine_id=4")
        # bottole of the specific wine sold
        self.assertIn("0", response.data["message"])

        #filters wine id and days
        response = self.client.get("/analytics/revenue/?days=20&wine_id=4")
        self.assertIn("20", response.data["message"])
        # bottles of the wine id 4 sold
        self.assertIn("0", response.data["message"])

    