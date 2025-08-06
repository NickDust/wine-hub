from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import *
from rest_framework.authentication import TokenAuthentication
from accounts.permission import *



class WineView(generics.ListCreateAPIView):
    queryset = WineModel.objects.all()
    serializer_class = WineSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]
    
class RegionView(generics.ListCreateAPIView):
    queryset = RegionModel.objects.all()
    serializer_class = RegionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

class StyleView(generics.ListCreateAPIView):
    queryset = WineStyleModel.objects.all()
    serializer_class = StyleSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

class TypeView(generics.ListCreateAPIView):
    queryset = WineTypeModel.objects.all()
    serializer_class = TypeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

class AppellationView(generics.ListCreateAPIView):
    queryset = AppellationModel.objects.all()
    serializer_class = AppellationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

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
    queryset = WineModel.objects.all()
    serializer_class = WineSerializer
    lookup_field ="pk"
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

class WineRetrieveView(generics.RetrieveAPIView):
    queryset = WineModel.objects.all()
    serializer_class = WineSerializer
    lookup_field = "pk"

class RegisterSaleView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrManagerOrAdmin]

    def post(self, request):
        serializer = RegisterSaleSerializer(data=request.data)
        if serializer.is_valid():
            try:
                wine_id = serializer.validated_data["wine_id"]
                wine = WineModel.objects.get(id=wine_id)
                quantity = serializer.validated_data["quantity"]
                if quantity > wine.stock:
                    return Response({"message": f"Not enough bottles of {wine.name}, available: {wine.stock}"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    wine.quantity_sold += quantity
                    wine.stock -= quantity
                    wine.save()
                    SaleModel.objects.create(wine=wine, user=request.user, quantity_sold=quantity)
                    bottle_word = "bottle" if quantity == 1 else "bottles"
                    return Response({"message": f"{quantity} {bottle_word} of {wine.name} sold."}, status=status.HTTP_202_ACCEPTED)
            except WineModel.DoesNotExist:
                return Response({"message": "The wine does not exist"}, status=status.HTTP_404_NOT_FOUND)
    

