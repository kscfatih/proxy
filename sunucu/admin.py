from django.contrib import admin
from .models import Server, ServerLog

admin.site.register(Server)
admin.site.register(ServerLog)
