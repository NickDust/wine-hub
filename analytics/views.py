from inventory_api.models import WineModel, SaleModel
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from inventory_api.serializers import WineSerializer
from datetime import datetime, timedelta
from collections import defaultdict
from accounts.permission import IsAdmin, IsManagerOrAdmin
from rest_framework.authentication import TokenAuthentication

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
            
class RevenueFilterView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdmin]

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
  
        
        