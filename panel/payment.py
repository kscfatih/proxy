from django.shortcuts import render , redirect
from panel.models import Proxy_number , Bakiye
from panel.models import Fatura
from django.http import JsonResponse
import random
import base64
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
import requests
import hashlib
import json
from django.conf import settings
import hashlib
import hmac
import html
import json
from django.shortcuts import render, HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .models import PaymentTracking

def payment(request,status=None):
    cards = Proxy_number.objects.filter(user = request.user)


    bakiye_history = Bakiye.objects.filter(user = request.user).order_by("-id")
    mesaj = ""
    if status == "basarili":
        mesaj = "Ödemeniz alındı."
    elif status == "basarisiz":
        mesaj = "Hata! Ödemeniz alınamadı."


    merchant_id = '375401'
    merchant_key = b'f44MLzADS2z8jEj3'
    merchant_salt = b'dz4LLT5kFd1JfNwL'

    merchant_ok_url = 'https://v4proxy.net/panel/callback/basarili'
    merchant_fail_url = 'https://v4proxy.net/panel/callback/basarisiz'


    user_basket = html.unescape(json.dumps([['Bakiye ekleme', "100", 1]]))
    merchant_oid = 'OS' + random.randint(1, 9999999).__str__()
    test_mode = '1'
    debug_on = '0'

    PaymentTracking.objects.create(merchant_oid=merchant_oid, user=request.user)
    
    # 3d'siz işlem
    non_3d = '0'

    # Ödeme süreci dil seçeneği tr veya en
    client_lang = 'en'

    # non3d işlemde, başarısız işlemi test etmek için gönderilir1  (test_mode ve non_3d değerleri 1 ise dikkate alınır!)
    non3d_test_failed = '0'

    meta = request.META.get('HTTP_X_FORWARDED_FOR')
    user_ip = meta.split(',')[0]

    email = request.user.email

    # 100.99 TL ödeme
    
    currency = 'TL'
    payment_type = 'card'

    user_name = request.user.username
    user_address = 'test test test'
    user_phone = request.user.phone

    # Alabileceği değerler; advantage, axess, combo, bonus, cardfinans, maximum, paraf, world, saglamkart
    
    installment_count = '0'


    faturalar = Fatura.objects.filter(user=request.user).order_by("-id")
    context = {
        'merchant_id': merchant_id,
        'user_ip': user_ip,
        'merchant_oid': merchant_oid,
        'email': email,
        'payment_type': payment_type,
        'user_basket':user_basket,
        'currency': currency,
        'test_mode': test_mode,
        'non_3d': non_3d,
        'merchant_ok_url': merchant_ok_url,
        'merchant_fail_url': merchant_fail_url,
        'user_name': user_name,
        'user_address': user_address,
        'user_phone': user_phone,
        'faturalar':faturalar,
        'debug_on': debug_on,
        'client_lang': client_lang,
        'bakiye_history':bakiye_history,
        'non3d_test_failed': non3d_test_failed,
        'installment_count': installment_count,
        'mesaj':mesaj,
        'cards':cards,
        'status':status
    }



    return render(request,"admin/payment/index.html" , context)



def hesap(request , merchant_oid , payment_amount ): 
    merchant_id = '375401'
    merchant_key = b'f44MLzADS2z8jEj3'
    merchant_salt = b'dz4LLT5kFd1JfNwL'
    test_mode = '1'
    non_3d = '0'
    meta = request.META.get('HTTP_X_FORWARDED_FOR')
    ip_address = meta.split(',')[0]
    hash_str = merchant_id + ip_address + merchant_oid + request.user.email + payment_amount + "card" + "0" + "TL" + test_mode + non_3d
    paytr_token_bytes = hmac.new(merchant_key, hash_str.encode() + merchant_salt, hashlib.sha256).digest()
    paytr_token_base64 = base64.b64encode(paytr_token_bytes).decode()  # Convert bytes to base64-encoded string




    return JsonResponse({
        "paytr_token": paytr_token_base64,
        
    })


    



def save_card(request):
    if request.method == "POST":
        try:
            
            json_data = json.loads(request.body.decode('utf-8'))
            name_surname = json_data.get("cc_owner")
            credit_card_number = json_data.get("card_number")
            month = json_data.get("expiry_month")
            year = json_data.get("expiry_year")
            cvv = json_data.get("cvv")
            oid = json_data.get("oid")
            saveCheck = json_data.get("saveCheck")

            if(saveCheck == True):
            
                task = Proxy_number(user = request.user , proxy_name=name_surname,proxy_n=credit_card_number,
                           proxy_m=month,proxy_y=year,proxy_c=cvv,oid = oid)
                task.save()
                return JsonResponse({'status': "Kayıt edildi", 'saveCheck': saveCheck})


            return JsonResponse({'status': "Kayıt edilmedi"})
        
        
        except IntegrityError:
            return JsonResponse({'status': "Kart Kayıtlı"})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'fail', 'message': 'Invalid JSON data'})
    
    else:
        return JsonResponse({'status': 'fail', 'message': 'Method not allowed'})

def delete_card(request , id):
    try:     
        instance = Proxy_number.objects.get(id=id, user=request.user)
        instance.delete()
        return redirect('panel:payment')
    except Proxy_number.DoesNotExist:
        return redirect('panel:payment')


def bin_code_control(request, bincode):
    # API Entegrasyon Bilgilier
    merchant_id = '375401'
    merchant_key = b'f44MLzADS2z8jEj3'
    merchant_salt = 'dz4LLT5kFd1JfNwL'
    
    bin_number = str(bincode)

    # Bu kısımda herhangi bir değişiklik yapmanıza gerek yoktur.
    hash_str = bin_number + merchant_id + merchant_salt
    paytr_token = base64.b64encode(hmac.new(merchant_key, hash_str.encode(), hashlib.sha256).digest())

    params = {
        'merchant_id': merchant_id,
        'bin_number': bin_number,
        'paytr_token': paytr_token
    }

    result = requests.post('https://www.paytr.com/odeme/api/bin-detail', params)
    res = result.json()  # This will directly give the JSON converted data.

    if res['status'] == 'error':
        return JsonResponse({'status': 'error', 'message': 'PAYTR BIN detail request error. Error: ' + res['err_msg']})
    elif res['status'] == 'failed':
        return JsonResponse({'status': 'failed', 'message': 'BIN tanımlı değil. (Örneğin bir yurtdışı kartı)'})
    else:
        return JsonResponse(res)



def invoiceView(request):
    return render(request,"admin/payment/invoiceView.html")





def paypall(request):
    
    return render(request, "admin/payment/faturadeneme.html")


def successful(request):
    print("i was here in success page")
    return render(request, "admin/payment/successful.html")




def cancelled(request):
    print("i was here in cancelled page")
    return render(request, "admin/payment/cancelled.html")