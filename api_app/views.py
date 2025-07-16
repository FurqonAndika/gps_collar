from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated

# model
from .models import SensorDataModel,Zoo,AreaModel

# serializer
from .serializer import ZooDashboardSerializer,Sensor24HourSerializer,AreaSerializer

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]  # atau [AllowAny] jika tidak perlu login

    def get(self, request,serial_id=None):
        if serial_id:
            try:
                zoo = Zoo.objects.get(serial_id=serial_id)
            except Exception as e:
                return Response({"error": "Gajah tidak ditemukan."}, status=404)

            now = timezone.now()
            since = now - timedelta(hours=24)
            sensor_data = SensorDataModel.objects.filter(zoo=zoo, time__gte=since).order_by('-time')

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

