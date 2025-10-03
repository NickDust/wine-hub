from inventory_api.models import WineModel, SaleModel
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from inventory_api.serializers import WineSerializer
from datetime import datetime, timedelta
from collections import defaultdict
from accounts.permission import IsAdmin, IsManagerOrAdmin, IsStaffOrManagerOrAdmin
from rest_framework.authentication import TokenAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import csv
from django.http import HttpResponse
from rest_framework.response import Response
from accounts.models import LogModel

class TopSellingView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        data = WineModel.objects.all().order_by("-quantity_sold")
        if not data:
            return Response({"detail": "No wines found."}, status=status.HTTP_404_NOT_FOUND)
        top_selling = data[0]
        serializer = WineSerializer(top_selling)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class LeastSellingView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        try:
            data = WineModel.objects.all().order_by("quantity_sold") 
            limit = int(request.query_params.get("limit", 5))
            if limit:
                data = data[:limit]
            serializer = WineSerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except(TypeError, ValueError):
            return Response({"detail": "No wines found."}, status=status.HTTP_404_NOT_FOUND)
        
class UnsoldWineView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        wines_unsold = WineModel.objects.filter(quantity_sold=0)
        if not wines_unsold:
            return Response({"message": "No wine found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = WineSerializer(wines_unsold, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

days_param = openapi.Parameter(
    name="days",
    in_=openapi.IN_QUERY,
    description="Filtered for amount of days (default 30).",
    type=openapi.TYPE_INTEGER,
    required=False,
    default=30,
)

wine_id_param = openapi.Parameter(
    name="wine_id",
    in_=openapi.IN_QUERY,
    description="Filtered the revenue just for a specific wine (ID).",
    type=openapi.TYPE_INTEGER,
    required=False,
)

class RevenueFilterView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        operation_description="""
        Get the amount of revenue for a given period of time (Default 30 days).
        **Access:** Admin only.
        if wine_id given, the result will be the revenue for that wine only.""",
        operation_summary= "Filtered Revenue.",
        manual_parameters=[days_param, wine_id_param],
        responses={
            200: "OK",
            404: "Parameters not valid.",
            401: "Unauthorized"
        })
    def get(self, request):
        try:
            wine_id = request.query_params.get("wine_id")
            days: int = int(request.query_params.get("days", 30))
            sales = SaleModel.objects.all()
            if wine_id:
                sales = sales.filter(wine__id=wine_id)
            if days:
                start_date = datetime.now() - timedelta(days=days)
                sales = sales.filter(timestamp__gte=start_date)
            total_revenue = 0
            wine_sold = 0
            for sale in sales:
                if sale.wine.retail_price:
                    price = sale.wine.retail_price 
                    quantity_sold = sale.quantity_sold
                    total = price * quantity_sold
                    total_revenue += total
                    wine_sold += quantity_sold
                else:
                    continue
            return Response({"message": f"The total revenue for this period of time({days} days) is: {total_revenue}£ with a total of {wine_sold} bottles sold"}, status=status.HTTP_200_OK)
        except (ValueError, TypeError):
            return Response({"message": "Bad request, check parameters or data format."}, status=status.HTTP_400_BAD_REQUEST)

class QuarterTrendSalesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        sales = SaleModel.objects.all()

        try:
            trend_by_quarter = defaultdict(float)
            current_year = datetime.now().year
            years = [current_year - 1, current_year]  

            for year in years:
                for q in range(1, 5):
                    key = f"{year}-Q{q}"
                    trend_by_quarter[key] = 0

            for sale in sales:
                year = sale.timestamp.year
                month = sale.timestamp.month
                quarter = (month - 1) // 3 + 1
                key = f"{year}-Q{quarter}"
                trend_by_quarter[key] += sale.quantity_sold * sale.wine.retail_price
                
            return Response(trend_by_quarter, status=status.HTTP_200_OK)   
        except(ValueError, TypeError):
            return Response({"Message": "Bad request, check parameters or data format."}, status=status.HTTP_400_BAD_REQUEST)

class BestEmployeeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        try:
            revenue_per_user = {}
            days: int = int(request.query_params.get("days", 30))
            start_date = datetime.now() - timedelta(days=days)
            sales = SaleModel.objects.all()
            if days:
                sales = sales.filter(timestamp__gte=start_date)
            for sale in sales:
                user = sale.user.username
                tot_revenue = sale.quantity_sold * sale.wine.retail_price
                revenue_per_user[user] = revenue_per_user.get(user, 0) + tot_revenue
            sorted_revenue = sorted(revenue_per_user.items(), key=lambda x: x[1], reverse=True)
            top_staff = [{"user": name, "revenue": revenue} for name, revenue in sorted_revenue]
            return Response({"Top employees": top_staff}, status=status.HTTP_200_OK)
        except (ValueError, TypeError):
            return Response({"message": "Bad request, check the parameter or data format."}, status=status.HTTP_400_BAD_REQUEST)

class LowStockView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrManagerOrAdmin]

    def get(self, request):
        low_stock = {}
        wines = WineModel.objects.all()
        for wine in wines:
            if wine.stock <= 10:
                low_stock[wine.name] = wine.stock

        if not low_stock: 
                return Response({"message": "No low stock wines found"}, status=status.HTTP_200_OK)
        
        return Response({"message": f"Low stock wines: {low_stock}"}, status=status.HTTP_200_OK)
    
class BaseExportView(viewsets.ViewSet):

    def export(self, filename, headers, rows):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename='{filename}.csv'"

        writer = csv.writer(response)
        writer.writerow(headers)

        for row in rows:
            writer.writerow(row)
        return response

class ExportViewSet(BaseExportView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdmin]

    @action(detail=False, methods=["get"], url_path="wine-list")
    def wine_list(self, request):
        wines = WineModel.objects.all()
        rows = [
            [wine.name, wine.stock, wine.price, wine.retail_price, wine.revenue()]
            for wine in wines
        ]
        return self.export(filename="wines", headers=["Wine", "Quantity", "Price", "Retail Price", "Revenue"], rows=rows)

    @action(detail=False, methods=["get"], url_path="sales")
    def sales(self,request):
        sales = SaleModel.objects.all()
        rows = [
            [sale.timestamp.date(), sale.wine.name, sale.user.username, sale.quantity_sold, sale.quantity_sold * sale.wine.retail_price]
            for sale in sales
            ]
        return self.export(filename="sales", headers=["Date","Wine","User","Quantity","Revenue"], rows=rows)

    @action(detail=False, methods=["get"], url_path="logs")
    def logs(self,request):

        logs = LogModel.objects.all()
        rows =[[log.timestamp.date(), log.action, log.user.username, log.details]
               for log in logs
               ]
        return self.export(filename="logs", headers=["Date","Action","User","Details"], rows=rows)