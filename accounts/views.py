from rest_framework.views import APIView
from .serializers import RegisterSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta
from .models import LogModel
from accounts.permission import IsAdmin, IsManagerOrAdmin
from rest_framework.authentication import TokenAuthentication


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({"message": "User created correctly.",
                             "token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        
        try:
            data = {}
            days: int = int(request.query_params.get("days", 30))
            start_date = datetime.now() - timedelta(days=days)
            logs = LogModel.objects.all()
            if days:
                logs = logs.filter(timestamp__gte=start_date)
            for log in logs:
                user = log.user.username
                entry = {
                    "action": log.action,
                    "timestamp": log.timestamp,
                    "details" : log.details if log.details else None
                }
                if user not in data:
                    data[user] = []
                data[user].append(entry)
            return Response(data, status=status.HTTP_200_OK)
        except (ValueError, TypeError):
            return Response({"message": "Bad request, check the parameter or data format."}, status=status.HTTP_400_BAD_REQUEST)
                