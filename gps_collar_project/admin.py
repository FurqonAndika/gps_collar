from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as set_text

class MyAdminSite(AdminSite):
    site_title = set_text("TELKOM Site Superadmin")

    site_header = set_text("TELKOM Administration")

    index_title = set_text("TELKOM")


admin_site = MyAdminSite()