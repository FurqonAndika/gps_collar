from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied

# model
from .models import SensorDataModel,Zoo,AreaModel,TelegramModel
from account_app.models import Instancy

# serializer
from .serializer import (ZooDashboardSerializer,Sensor24HourSerializer,
                                    AreaSerializer, ZooSerializer,
                                   TelegramSerializer)

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]  # atau [AllowAny] jika tidak perlu login

    def get(self, request,serial_id=None):
        if serial_id:
            if request.user.role!=1:
                return Response({"message":"You dont have permission"},status.HTTP_401_UNAUTHORIZED)
            try:
                zoo = Zoo.objects.get(serial_id=serial_id)
            except Exception as e:
                return Response({"error": "Gajah tidak ditemukan."}, status=404)

            now = timezone.now()
            since = now - timedelta(hours=24)
            sensor_data = SensorDataModel.objects.filter(zoo=zoo, time__gte=since).order_by('-time')[:20]

            zoo_data = ZooDashboardSerializer(zoo, context={'request': request}).data
            zoo_data['last_sensor_data'] = Sensor24HourSerializer(sensor_data, many=True).data

            area_data = AreaModel.objects.all()
            zoo_data['area'] = AreaSerializer(area_data, many=True).data

            return Response(zoo_data)

        zoos = Zoo.objects.all()
        serializer = ZooDashboardSerializer(zoos, many=True,context={'request': request})
        area_data = AreaModel.objects.all()
        area_serialized = AreaSerializer(area_data, many=True).data
        return Response(
            {
            'zoo': serializer.data,
            'area': area_serialized
            }
        )

class ZooView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        user = request.user
        if user.role == user.SUPERADMIN:
            return Zoo.objects.all()
        elif user.role == user.ADMIN:
            return Zoo.objects.filter(instancy=user.instancy)
        elif user.role == user.GUEST:
            return Zoo.objects.filter(instancy=user.instancy)
        return Zoo.objects.none()

    def get(self, request):
        queryset = self.get_queryset(request)
        serializer = ZooSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        user = request.user
        if user.role == user.GUEST:
            return Response({'message': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['created_by'] = user.id

        # Set atau validasi instansi
        if user.role == user.ADMIN:
            data['instancy'] = user.instancy.id
        elif user.role == user.SUPERADMIN:
            instancy_id = data.get('instancy')
            if not instancy_id:
                return Response({'message': 'Instancy is required for SUPERADMIN.'}, status=status.HTTP_400_BAD_REQUEST)
            if not Instancy.objects.filter(id=instancy_id).exists():
                return Response({'message': 'Invalid instancy ID.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ZooSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save()
            response_data = {
                "message": "success",
                "data": ZooSerializer(instance, context={'request': request}).data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = request.user
        zoo_id = request.data.get('id')
        if not zoo_id:
            return Response({'detail': 'Zoo ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            zoo = Zoo.objects.get(id=zoo_id)
        except Zoo.DoesNotExist:
            return Response({'detail': 'Zoo not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.role == user.GUEST:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        if user.role == user.ADMIN and zoo.instancy != user.instancy:
            return Response({'detail': 'You do not have permission to edit this item.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ZooSerializer(zoo, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            response = {
                "message":"success",
                "data" : ZooSerializer(instance, context={'request': request}).data
            }
            return Response(response, status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        zoo_id = request.data.get('id')
        if not zoo_id:
            return Response({'message': 'Zoo ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            zoo_id = int(zoo_id)
        except Exception as e:
            return Response({"message":"invalid ID"})
        try:
            zoo = Zoo.objects.get(id=zoo_id)
        except Zoo.DoesNotExist:
            return Response({'message': 'Zoo not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.role == user.GUEST:
            return Response({'message': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        if user.role == user.ADMIN and zoo.instancy != user.instancy:
            return Response({'message': 'You do not have permission to delete this item.'}, status=status.HTTP_403_FORBIDDEN)

        zoo.delete()
        return Response({'message': 'Deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class AreaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = AreaModel.objects.all()
        serializer = AreaSerializer(queryset, many=True)
        return Response({"message": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.role != request.user.SUPERADMIN:
            raise PermissionDenied("Only SuperAdmin can create area.")
        serializer = AreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Area created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if request.user.role != request.user.SUPERADMIN:
            raise PermissionDenied("Only SuperAdmin can update area.")
        area_id = request.data.get("id")
        if not area_id:
            return Response({"message": "Area ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            area = AreaModel.objects.get(id=area_id)
        except AreaModel.DoesNotExist:
            return Response({"message": "Area not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AreaSerializer(area, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Area updated", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if request.user.role != request.user.SUPERADMIN:
            raise PermissionDenied("Only SuperAdmin can delete area.")
        area_id = request.data.get("id")
        if not area_id:
            return Response({"message": "Area ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            area = AreaModel.objects.get(id=area_id)
            area.delete()
            return Response({"message": "Area deleted successfully"}, status=status.HTTP_200_OK)
        except AreaModel.DoesNotExist:
            return Response({"message": "Area not found"}, status=status.HTTP_404_NOT_FOUND)

class TelegramView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = TelegramModel.objects.all()
        serializer = TelegramSerializer(queryset, many=True)
        return Response({"message": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.role != request.user.SUPERADMIN:
            raise PermissionDenied("Only SuperAdmin can create telegram bot.")
        serializer = TelegramSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Telegram bot created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if request.user.role != request.user.SUPERADMIN:
            raise PermissionDenied("Only SuperAdmin can update telegram bot.")
        bot_id = request.data.get("id")
        if not bot_id:
            return Response({"message": "Bot ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            bot = TelegramModel.objects.get(id=bot_id)
        except TelegramModel.DoesNotExist:
            return Response({"message": "Bot not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TelegramSerializer(bot, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Telegram bot updated", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if request.user.role != request.user.SUPERADMIN:
            raise PermissionDenied("Only SuperAdmin can delete telegram bot.")
        bot_id = request.data.get("id")
        if not bot_id:
            return Response({"message": "Bot ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            bot = TelegramModel.objects.get(id=bot_id)
            bot.delete()
            return Response({"message": "Telegram bot deleted"}, status=status.HTTP_200_OK)
        except TelegramModel.DoesNotExist:
            return Response({"message": "Bot not found"}, status=status.HTTP_404_NOT_FOUND)
