from rest_framework import serializers
from .models import Zoo, SensorDataModel,AreaModel

class SensorDataModelSerializer(serializers.ModelSerializer):
    data_sensor = serializers.SerializerMethodField()
    class Meta:
        model = SensorDataModel
        fields = ['time', 'latitude', 'longitude', 'data_sensor']

    def get_data_sensor(self, obj):
        return [
            {
                "sensor_name": "temperature",
                "value": obj.temperature,
                "notation": "Celcius"
            },
            {
                "sensor_name": "battery",
                "value": obj.battery,
                "notation": "Volt"
            }
        ]
class ZooDashboardSerializer(serializers.ModelSerializer):
    last_sensor_data = serializers.SerializerMethodField()
    instancy = serializers.CharField(source='instancy.balai_name', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Zoo
        fields = ['serial_id', 'name', 'satelit_serial', 'image', 'instancy', 'last_sensor_data']

    def get_last_sensor_data(self, obj):
        latest_data = obj.sensor_data.order_by('-time').first()
        if latest_data:
            return SensorDataModelSerializer(latest_data).data
        return None
    
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class Sensor24HourSerializer(serializers.ModelSerializer):
    data_sensor = serializers.SerializerMethodField()

    class Meta:
        model = SensorDataModel
        fields = ['time', 'latitude', 'longitude', 'data_sensor']

    def get_data_sensor(self, obj):
        return [
            {
                "sensor_name": "temperature",
                "value": obj.temperature,
                "notation": "Celcius"
            },
            {
                "sensor_name": "battery",
                "value": obj.battery,
                "notation": "Volt"
            }
        ]

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaModel
        fields = ['longitude', 'latitude', 'radius_km', 'place_name']
