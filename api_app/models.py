from django.db import models
import uuid 
from django.contrib.auth import get_user_model
from account_app.models import Instancy
User = get_user_model()

# Create your models here.

class Zoo(models.Model):
    serial_id = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, verbose_name='uid')
    name = models.CharField(max_length=100)
    satelit_serial = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,related_name="zoo_model",blank=True,null=True)
    image = models.ImageField(null=True, blank=True, upload_to='zoo')
    instancy = models.ForeignKey(Instancy, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name+"|"+self.satelit_serial
    class Meta:
        db_table = 'collar_zoo'
    
class SensorDataModel(models.Model):
    zoo = models.ForeignKey(Zoo, null=True, on_delete=models.SET_NULL, related_name="sensor_data")
    time = models.DateTimeField()
    created_at = models.DateTimeField()
    latitude = models.DecimalField(max_digits=11, decimal_places=4,null=True)  
    longitude = models.DecimalField(max_digits=11, decimal_places=4, null=True) 
    temperature = models.FloatField(null=True)
    battery = models.FloatField(null=True)
    
    class Meta:
        unique_together = ('zoo', 'time')
        db_table = 'collar_sensor_data'

class RawSensorDataModel(models.Model):
    time = models.DateTimeField()
    created_at = models.DateTimeField()
    topic = models.CharField(max_length=100)
    message = models.CharField(max_length=255)
    class Meta:
        unique_together = ('message',"time")
        db_table = 'collar_raw_sensor_data'
