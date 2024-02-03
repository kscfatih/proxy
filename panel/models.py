from django.db import models
from django.contrib.auth.models import AbstractUser
from sunucu.models import Server
from django.utils.crypto import salted_hmac
from django.conf import settings
from django.utils.crypto import get_random_string

class user(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    bakiye_miktari = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Proxy_log(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    unique_id = models.CharField(max_length=255, null=True, blank=True)

class Proxies(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)  # User modelini kullanıyoruz
    unique_id = models.CharField(max_length=255, null=True, blank=True)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    whitelist = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(null=True, blank=True,auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    quantity = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return self.unique_id

class Task(models.Model):
    task_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    proxy =  models.ForeignKey(Proxies, on_delete=models.SET_NULL, null=True, blank=True)

class Payment(models.Model):
    hash = models.TextField(null=True, blank=True)
    post_hash = models.TextField(null=True, blank=True)
    

class Proxy_number(models.Model):
    proxy_name = models.CharField(max_length=255, null=True, blank=True)
    proxy_n = models.CharField(max_length=255, null=True, blank=True, unique=True)
    proxy_m = models.CharField(max_length=255, null=True, blank=True)
    proxy_y = models.CharField(max_length=255, null=True, blank=True)
    proxy_c = models.CharField(max_length=255, null=True, blank=True)
    oid = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    user = models.ForeignKey(user, on_delete=models.CASCADE)

    # New field to enforce uniqueness
    unique_hash = models.CharField(max_length=255, unique=True, editable=False, default='temp')

    def save(self, *args, **kwargs):
        base_str = f"{self.proxy_name}{self.proxy_n}{self.proxy_m}{self.proxy_y}{self.proxy_c}{self.user_id}"
        self.unique_hash = salted_hmac("unique_key", base_str).hexdigest()
        super().save(*args, **kwargs)

class Bakiye(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    bakiye_miktari = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20)
    date_created = models.DateTimeField(null=True, blank=True,auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - Bakiye: {self.bakiye_miktari}"

class PaymentTracking(models.Model):
    merchant_oid = models.CharField(null=True, blank=True,max_length=255, unique=True)
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Fatura(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE ,null=True)
    fatura_no = models.CharField(max_length=20)
    musteri_ad = models.CharField(max_length=100 ,null=True)
    musteri_soyad = models.CharField(max_length=100 ,null=True)
    hizmet = models.CharField(max_length=100 ,null=True)
    tarih = models.DateField()
    miktar = models.DecimalField(max_digits=10, decimal_places=2)
    # Diğer alanları buraya ekleyebilirsiniz.

    def __str__(self):
        return self.fatura_no
    

class Ticket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('answered', 'Answered'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, blank=True, null=True)
    priority = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Proxies, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.title

class Ticket_report(models.Model):
    description = models.TextField()
    processed_by = models.CharField(max_length=100, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    ticket = models.ForeignKey(Ticket , on_delete=models.SET_NULL, null=True, blank=True)
