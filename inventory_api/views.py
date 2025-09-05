from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import *
from rest_framework.authentication import TokenAuthentication
from accounts.permission import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import F
from accounts.models import LogModel



class WineView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]
    
    queryset = WineModel.objects.all()
    serializer_class = WineSerializer
    
class RegionView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

    queryset = RegionModel.objects.all()
    serializer_class = RegionSerializer
    

class StyleView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

    queryset = WineStyleModel.objects.all()
    serializer_class = StyleSerializer
    
class TypeView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

    queryset = WineTypeModel.objects.all()
    serializer_class = TypeSerializer
    

class AppellationView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

    queryset = AppellationModel.objects.all()
    serializer_class = AppellationSerializer
    

class DashBoardApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrManagerOrAdmin]

    def get(self, request):
        regions = RegionSerializer(RegionModel.objects.all(), many=True).data
        types = TypeSerializer(WineTypeModel.objects.all(), many=True).data
        styles = StyleSerializer(WineStyleModel.objects.all(), many=True).data
        appelations = AppellationSerializer(AppellationModel.objects.all(), many=True).data

        return Response({
            "regions": regions,
            "wine_types": types,
            "wine_styles": styles,
            "Appelation": appelations
        })

class WineRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]
    
    queryset = WineModel.objects.all()
    serializer_class = WineSerializer
    lookup_field ="pk"
    

class WineRetrieveView(generics.RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrManagerOrAdmin]

    queryset = WineModel.objects.all()
    serializer_class = WineSerializer
    lookup_field = "pk"

class RegisterSaleView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrManagerOrAdmin]

    @swagger_auto_schema(
        operation_description=""" \
        "Register a new sale." \
        "**Access:** Staff, Manager, Admin." \
        "**Required:**" \
        "- wine_id (int)," \
        "- quantity (int)." \
        "**Results:**" \
        "- If the stock of the wine sold is sufficient, is gonna register the sale and updating the quantity in stock""",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "wine_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Wine ID"),
                "quantity": openapi.Schema(type=openapi.TYPE_INTEGER, description="Quantity of the wine sold"),
            },
            required=["wine_id", "quantity"]
            
        ),
        responses={
            202: "Sale registered.",
            404: "Data not valid.",
            401: "Unauthorized."
        })
    
    def post(self, request):
        serializer = RegisterSaleSerializer(data=request.data)
        if serializer.is_valid():
            try:
                wine_id = serializer.validated_data["wine_id"]
                wine = WineModel.objects.select_for_update().get(id=wine_id)
                quantity = serializer.validated_data["quantity"]
                if quantity > wine.stock:
                    return Response({"message": f"Not enough bottles of {wine.name}, available: {wine.stock}"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    with transaction.atomic():
                        wine.quantity_sold = F("quantity_sold") + quantity
                        wine.stock = F("stock") - quantity
                        wine.save()
                        wine.refresh_from_db()
                        SaleModel.objects.create(wine=wine, user=request.user, quantity_sold=quantity)
                        bottle_word = "bottle" if quantity == 1 else "bottles"
                    return Response({"message": f"{quantity} {bottle_word} of {wine.name} sold."}, status=status.HTTP_202_ACCEPTED)
            except WineModel.DoesNotExist:
                return Response({"message": "The wine does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
class RestockView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

    @swagger_auto_schema(request_body=RestockSerializer)
    def post(self, request, pk):
        serializer = RestockSerializer(data=request.data)
        if serializer.is_valid():
            qty = serializer.validated_data["quantity"]
            wine = get_object_or_404(WineModel, pk=pk)
            with transaction.atomic():
                wine.stock = F("stock") + qty
                wine.save()
                wine.refresh_from_db()
                LogModel.objects.create(
                    user = request.user,
                    action = "restock",
                    details = f"{wine.name}: + {qty}"
                )
        return Response({"wine": wine.name, "added": qty, "stock": wine.stock}, status=status.HTTP_200_OK)

class RefundView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

    @swagger_auto_schema(
            operation_summary= "Refund a sale",
            request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refund_qty": openapi.Schema(type=openapi.TYPE_INTEGER, minimum=1, description="Quantity of the wine refunded"),
                "return_to_stock": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False, description= "If true bottles returned to stock")
            },
        )
        )
    def post(self, request, pk):
        serializer = SaleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            qty = serializer.validated_data["refund_qty"]
            return_to_stock = serializer.validated_data["return_to_stock"]
            sale = get_object_or_404(SaleModel, pk=pk)
            if qty <= 0 or qty > sale.quantity_sold:
                return Response({"message": "Bad Request, check parameters."}, status=status.HTTP_400_BAD_REQUEST)
            with transaction.atomic():
                sale.refund_qty= F("refund_qty") + qty
                sale.quantity_sold = F("quantity_sold") - qty
                sale.save()
                sale.refresh_from_db()
                sale.wine.quantity_sold = F("quantity_sold") - qty
                if return_to_stock:
                    sale.wine.stock = F("stock") + qty
                sale.wine.save()
                sale.wine.refresh_from_db()
            LogModel.objects.create(
                user=request.user,
                action="refund",
                details=f"{qty} bottles of {sale.wine.name} refunded"
            )
        return Response({"message": f"{qty} bottles of {sale.wine.name} refunded" + (" (returned to stock)" if return_to_stock else "")}, status=status.HTTP_200_OK)
            
            