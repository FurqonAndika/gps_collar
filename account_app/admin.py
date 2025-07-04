# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Instancy
from .forms import CustomUserChangeForm, CustomUserCreationForm

from gps_collar_project.admin import admin_site

class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('id','username', 'email', "get_instancy",'first_name', 'last_name', 'role', 'is_staff',"is_superuser","created_by","last_login")
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email',"get_instancy","instancy")}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role','instancy', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')

    readonly_fields = ('get_instancy',)

    def get_instancy(self, obj):
        return obj.instancy.balai_name if obj.instancy else None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'instancy':
            kwargs['queryset'] = Instancy.objects.all()
            kwargs['label'] = 'instancy'
            kwargs['empty_label'] = 'Select an instancy'
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    
# @admin.register(Instancy)
class InstancyAdmin(admin.ModelAdmin):
    model = Instancy
    list_display = ["id", "balai_name","created_at",]
    search_fields = ["balai_name"]


admin.site.register(Instancy,InstancyAdmin)
admin.site.register(User, UserAdmin)
