from celery import shared_task
from .models import Proxies , Server
from django.utils import timezone

@shared_task
def delete_expired_proxies():
    now = timezone.now()
    expired_proxies = Proxies.objects.filter(end_date__lte=now)
    
    for proxy in expired_proxies:
        quantity = proxy.quantity
        server_id = proxy.server_id
        server = Server.objects.get(id = server_id)
        server.usage = int(server.usage) - int(quantity)
        server.save()
        proxy.delete()