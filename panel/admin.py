from django.contrib import admin
from .models import Ticket, Ticket_report , Proxies
from .models import Fatura
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import user



class ProxiesAdmin(admin.ModelAdmin):
    # Burada, admin panelinde göstermek istediğiniz alanları belirtin
    list_display = ('unique_id','user',  'quantity' , 'date_created')

# Modelinizi özelleştirilmiş admin sınıfıyla kaydedin
admin.site.register(Proxies, ProxiesAdmin)



admin.site.register(Fatura)

class TicketReportInline(admin.TabularInline):
    model = Ticket_report
    extra = 1
    fields = ['description', 'ticket']  

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    inlines = [TicketReportInline]

@admin.register(Ticket_report)
class TicketReportAdmin(admin.ModelAdmin):
    list_display = ('description', 'processed_by', 'created_at', 'ticket')
    list_filter = ('processed_by', 'created_at')
    search_fields = ('description',)
    raw_id_fields = ('ticket',)


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = user

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = user

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
   
    list_display = ('username', 'email', 'phone', 'bakiye_miktari', 'is_staff')
    
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone', 'bakiye_miktari')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone', 'bakiye_miktari')}),
    )

admin.site.register(user, CustomUserAdmin)