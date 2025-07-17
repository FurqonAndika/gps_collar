from django.contrib import admin

# Register your models here.
from .models import RawSensorDataModel, SensorDataModel, Zoo,AreaModel, TelegramModel


# @admin.register(Instancy)
class SensorDataAdmin(admin.ModelAdmin):
    model = SensorDataModel
    list_display = ["zoo__name", "longitude","latitude","temperature","battery","time",]
    search_fields = ["zoo__name"]

class RawSensorDataAdmin(admin.ModelAdmin):
    model = RawSensorDataModel
    list_display = ["topic","message","created_at"]
    search_fields = ["topic"]

class ZooAdmin(admin.ModelAdmin):
    model = Zoo
    list_display = ["id","name","instancy__balai_name","satelit_serial"]
    search_fields = ["name"]

class AreaAdmin(admin.ModelAdmin):
    model = AreaModel
    list_display = ["place_name","longitude","latitude","radius_km"]
    search_fields = ["place_name"]

class TelegramAdmin(admin.ModelAdmin):
    model = TelegramModel
    list_display = ["bot_name","link","create_at"]
    search_fields = ["bot_name"]

admin.site.register(RawSensorDataModel,RawSensorDataAdmin)
admin.site.register(SensorDataModel,SensorDataAdmin)
admin.site.register(Zoo,ZooAdmin)
admin.site.register(AreaModel,AreaAdmin)
admin.site.register(TelegramModel, TelegramAdmin)