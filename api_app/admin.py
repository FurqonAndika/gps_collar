from django.contrib import admin

# Register your models here.
from .models import RawSensorDataModel, SensorDataModel, Zoo


# @admin.register(Instancy)
class SensorDataAdmin(admin.ModelAdmin):
    model = SensorDataModel
    list_display = ["zoo__name", "longitude","latitude","time",]
    search_fields = ["zoo__name"]

class RawSensorDataAdmin(admin.ModelAdmin):
    model = RawSensorDataModel
    list_display = ["topic","message","created_at"]
    search_fields = ["topic"]

class ZooaAdmin(admin.ModelAdmin):
    model = Zoo
    list_display = ["name","instancy__balai_name","satelit_serial"]
    search_fields = ["name"]

admin.site.register(RawSensorDataModel,RawSensorDataAdmin)
admin.site.register(SensorDataModel,SensorDataAdmin)
admin.site.register(Zoo,ZooaAdmin)