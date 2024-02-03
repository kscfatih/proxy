from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from panel.models import user, Proxy_log
from panel.models import Task , PaymentTracking
from panel.models import Bakiye
from panel.models import Payment
from sunucu.models import Server
from panel.models import Ticket
from io import BytesIO
from django.core.paginator import Paginator
from panel.models import Fatura
from ipaddress import IPv6Network, IPv6Address
from random import getrandbits, seed
import subprocess
import paramiko
import random
import string
from django.contrib import messages
from urllib.parse import urlparse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls.base import resolve, reverse
from django.urls.exceptions import Resolver404
from django.utils import translation
from django.utils.translation import activate
from django.http import HttpResponse
from panel.models import Proxies
import uuid
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import base64
import hashlib
import hmac
import html
import json
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from panel.models import Proxy_number
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.template.loader import get_template
from datetime import datetime, timedelta
from xhtml2pdf import pisa
from django.db.models import Sum
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import user as CustomUser
from .tokens import account_activation_token
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from sib_api_v3_sdk import TransactionalEmailsApi, SendSmtpEmail
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

@login_required(login_url='/panel/login')
def index(request):
    user = request.user
    proxies = Proxies.objects.filter(user=user).order_by('-date_created')
    total_proxies = proxies.aggregate(total=Sum('quantity'))['total']
    balance = request.user.bakiye_miktari
    if total_proxies is not None:
        total_proxies = int(total_proxies)
    tickets = Ticket.objects.filter(user=user).order_by('-created_at')
    return render(request,"admin/dashboard/index.html", {'ticket_context': tickets , 'proxies_context': proxies , 'proxies_context_total':total_proxies , 'balance_context':balance , 'user':user,'user_id':user.id})

def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        paramatere = user.objects.get(email=email)
        username = paramatere.username
        usercontrol = authenticate(request, username=username, password=password)
        if usercontrol is not None:
            login(request, usercontrol)
            return redirect('panel:home')
        else:
            messages.error(request, "There was an error logging in, try again...")
            return redirect('panel:login')
        
    elif request.user.is_authenticated:
            return redirect('panel:home')    
    else:
        return render(request,"admin/login/index.html")
User = get_user_model()
def register(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        username = firstname.lower() + lastname.lower() + str(random.randint(1000, 9999))
        email = request.POST.get("email")
        pw1 = request.POST.get("pw1")
        pw2 = request.POST.get("pw2")
        if User.objects.filter(email=email).exists():
           messages.error(request, "This email is already in use!")
           return redirect('panel:register')
        if pw1 == pw2:
            user_kayit = user.objects.create_user(username=username, is_active=False, email=email, password=pw1, first_name=firstname, last_name=lastname,bakiye_miktari=0)
            task = Bakiye(user_id = user_kayit.id ,bakiye_miktari=0)
            task.save()
            send_activation_email(user_kayit, request)

            messages.success(request, "Please confirm your email to complete registration.")
            return redirect('panel:login' )
        else:
            messages.error(request, "Passwords did not match!")
            return redirect('panel:register' )
    else:
        return render(request,"admin/login/register.html")

def logout_user(request):
    logout(request)
    return redirect('panel:login')

def set_language(request, language):
    for lang, _ in settings.LANGUAGES:
        translation.activate(lang)
        try:
            view = resolve(urlparse(request.META.get("HTTP_REFERER")).path)
        except Resolver404:
            view = None
        if view:
            break
    if view:
        translation.activate(language)
        next_url = reverse(view.url_name, args=view.args, kwargs=view.kwargs)
        response = HttpResponseRedirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
    else:
        response = HttpResponseRedirect("/")
    return response

def account_settings(request):
    id=request.user.id
    User = get_user_model()
    user = get_object_or_404(User, id=id)

    if request.method == "POST":
        firstname = request.POST.get("first_name")
        lastname = request.POST.get("last_name")
        user.first_name = firstname
        user.last_name = lastname
        user.save()

    return render(request,"admin/panel/account/index.html",{"user":user})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # ... Başarılı aktivasyon işlemleri ...
        return redirect('panel:login')  # veya uygun bir URL'ye yönlendirin
    else:
        # ... Hatalı veya geçersiz link durumu ...
        return redirect('panel:login')


def send_activation_email(user, request):
    subject = 'Activate Your Account'
    activation_url = request.build_absolute_uri(reverse('panel:activate', kwargs={
        'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user)
    }))
    message = 'Hi {},\n\nPlease click on the link below to activate your account:\n\n{}'.format(
        user.first_name,
        activation_url
    )
    email_from = 'support@v4proxy.net'
    recipient_list = [user.email]

    # SendinBlue API konfigürasyonu
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = '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'  # SendinBlue API anahtarınız

    # E-posta gönderimi için API istemcisi oluşturun
    api_instance = TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    send_smtp_email = SendSmtpEmail(to=[{"email": recipient_list[0]}],
                                    html_content=message,
                                    subject=subject,
                                    sender={"email": email_from})

    try:
        # E-posta gönder
        api_response = api_instance.send_transac_email(send_smtp_email)
        
        print(api_response)
    except ApiException as e:
        print("Exception when calling TransactionalEmailsApi->send_transac_email: %s\n" % e)


def change_language(request, language_code):
    if language_code in [lang_code for lang_code, _ in settings.LANGUAGES]:
        request.session[translation.LANGUAGE_SESSION_KEY] = language_code
        activate(language_code)
    return redirect('panel:index')

def rastgele(request):
    return render(request,"admin/rastgele.html")


def update_proxy_user(ip, username, password, cfg, proxy_cfg, p_username, p_password, new_username, new_password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username, password=password)
    
    stdin, stdout, stderr = ssh.exec_command(f'cat /etc/3proxy/conf/{cfg}')
    passwd_content = stdout.read().decode()
    
    updated_content = passwd_content.replace(f'{p_username}:CL:{p_password}', f'{new_username}:CL:{new_password}')
    
    with open('updated_passwd', 'w') as file:
        file.write(updated_content)
    
    sftp = ssh.open_sftp()
    sftp.put('updated_passwd', f'/etc/3proxy/conf/{cfg}')

    stdin, stdout, stderr = ssh.exec_command(f'cat /etc/3proxy/conf/{proxy_cfg}')
    proxy_content = stdout.read().decode()
    updated_proxy_content = proxy_content.replace(f'allow {p_username}', f'allow {new_username}')
    with open('updated_proxy_cfg', 'w') as file:
        file.write(updated_proxy_content)
    sftp.put('updated_proxy_cfg', f'/etc/3proxy/conf/{proxy_cfg}')

    sftp.close()

    ssh.exec_command('sudo systemctl restart 3proxy')

    ssh.close()


@login_required
def view_proxy(request , id):  
    proxy = Proxies.objects.get(id=id)
    username = proxy.server.username 
    password  = proxy.server.password
    p_username = proxy.username
    p_password = proxy.password
    ip = proxy.server.ip_address
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username, password=password)
    cfg = proxy.unique_id
    stdin, stdout, stderr = ssh.exec_command(f'cat /etc/3proxy/conf/{cfg}')
    file_content = stdout.read().decode()
    ssh.close()

    formatted_proxy_list = ""
    for line in file_content.splitlines():
        if line.startswith(('proxy', 'socks')):
            parts = line.split()
            port = parts[2][2:]
            formatted_proxy = f"{ip}:{port}:{p_username}:{p_password}\n"
            formatted_proxy_list += formatted_proxy

    if request.method == "POST":
        p_user = request.POST.get("username")
        p_pass = request.POST.get("password")
        update_proxy_user(ip, username, password, 'passwd',cfg, p_username, p_password, p_user, p_pass)
        proxy.username = p_user
        proxy.password = p_pass
        proxy.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    
    return render(request, 'admin/panel/proxy/detail.html', {
        'file_content': formatted_proxy_list,
        'username':p_username,
        'password':p_password
        })

@login_required
def proxies(request):
    user_proxies = Proxies.objects.filter(user_id=request.user.id).order_by("-date_created")
    task_ids = Task.objects.all()
    paginator = Paginator(user_proxies, 7) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"admin/panel/proxy/index.html", {"task_ids":task_ids , "user_proxies": page_obj})


@login_required
def create_48(request):
    if request.method == "POST":
        balance = request.user.bakiye_miktari
        totalprice = Decimal(request.POST.get("totalprice", "0"))
        if balance >= totalprice : 
            user = request.user
            unique_id = uuid.uuid4()
            proxy_cfg_path = f"/etc/3proxy/conf/{unique_id}"
            server_id = int(request.POST.get("server_id"))
            server = Server.objects.get(id=server_id)
            quantity = int(request.POST.get("quantity"))
    ##########
            used_ports = list(map(int, server.used_port.split(',')))

            # Eğer used_port listesi boş değilse, en son sayıyı buluyoruz.
            if used_ports:
                last_port = max(used_ports)
            else:
                last_port = 2002  # used_port listesi boşsa varsayılan olarak 2002 alalım.

            # Yeni portu belirleyip, new_port ve used_port alanlarını güncelliyoruz.
            ilk = last_port + 1
            
    #########
            cmds = []

            if "userName" in request.POST:
                username = request.POST.get("userName")
                password = request.POST.get("password")
                start_text = f'echo "\nauth strong\nallow {username}" >> {proxy_cfg_path}'
                passwd_text  = f'echo "\n{username}:CL:{password}" >> /etc/3proxy/conf/passwd'
                cmds.append(start_text)
                cmds.append(passwd_text)
                proxy = Proxies.objects.create(user=user, unique_id=unique_id, server=server, username=username, password=password, whitelist='', quantity=quantity , type="IPV6")
                proxy.save()

            if 'userName' not in request.POST and 'password' not in request.POST and 'whitelist' not in request.POST:
                length = 6
                username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
                start_text = f'echo "\nauth strong\nallow {username}" >> {proxy_cfg_path}'
                passwd_text  = f'echo "\n{username}:CL:{password}" >> /etc/3proxy/conf/passwd'
                cmds.append(start_text)
                cmds.append(passwd_text)
                proxy = Proxies.objects.create(user=user, unique_id=unique_id, server=server, username=username, password=password, whitelist='', quantity=quantity, type="IPV6")
                proxy.save()

            if "whitelist" in request.POST:
                whitelist = request.POST.get("whitelist")
                start_text = f'echo "\nauth iponly \nallow * {whitelist}" >> {proxy_cfg_path}'
                cmds.append(start_text)
                proxy = Proxies.objects.create(user=user, unique_id=unique_id, server=server, username='', password='', whitelist=whitelist, quantity=quantity , type="IPV6")
                proxy.save()

            proxy_type = request.POST.get('proxy_type')
            if proxy_type in ['SOCKS5', 'HTTPs']:
                proxy_cmd = 'socks' if proxy_type == 'SOCKS5' else 'proxy'
                
                for x in range(quantity):
                    subnet = server.ipv6
                    seed()
                    network = IPv6Network(subnet)
                    address = IPv6Address(network.network_address + getrandbits(network.max_prefixlen - network.prefixlen))
                    b = str(address)
                    port_number = str(ilk)

                    c = " -e"
                    d = c + b
                    e = "-p"
                    f = str(ilk)
                    g = e + f

                    eth_card = server.eth_card
                    add_ip = f'/sbin/ip -6 addr add {b}/48 dev {eth_card}'
                    cmds.append(add_ip)

                    add_port_udp = f'iptables -A INPUT -p udp --dport {port_number} -j ACCEPT'
                    cmds.append(add_port_udp)

                    add_port_tcp = f'iptables -A INPUT -p tcp --dport {port_number} -j ACCEPT'
                    cmds.append(add_port_tcp)

                    server_proxy_adress = server.ip_address
                    command = f'echo "\n{proxy_cmd} -6 {g} -a -i{server_proxy_adress}{d}" >> {proxy_cfg_path}'
                    cmds.append(command)
                    
                    used_ports.append(ilk)
                    ilk += 1

                Server.objects.filter(id=server_id).update(
                used_port=','.join(map(str, used_ports))
                )    

                cmds.append(f'echo "\nflush" >> {proxy_cfg_path}')

                proxy_cfg_add  = f'echo "\ninclude /conf/{unique_id} " >> /etc/3proxy/3proxy.cfg'
                cmds.append(proxy_cfg_add)
                restart_3proxy = "service 3proxy restart"
                cmds.append(restart_3proxy)
                # Open SSH connection and execute all commands
                
                task_id = str(uuid.uuid4())  # Generate a unique task identifier
                task = Task(task_id=task_id, status='running' , proxy_id = proxy.id)
                task.save()
                
                new_balance = balance - totalprice
                # Yeni bakiyeyi kullanıcı modeline kaydet
                request.user.bakiye_miktari = new_balance
                request.user.save()

                fatura = Fatura()
                fatura.user = request.user
                
                try:
                    # En son eklenen fatura nesnesini alın
                    last_fatura = Fatura.objects.latest('id')
                    new_fatura_no = int(last_fatura.fatura_no) + 1
                except Fatura.DoesNotExist:
                    # Eğer hiç fatura nesnesi yoksa başlangıç değeri olarak 1000 kullanın
                    new_fatura_no = 1000

                fatura.fatura_no = str(new_fatura_no)
                
                 # Eğer otomatik artan bir numara sistemi isterseniz bu kısmı değiştirmeniz gerekmektedir.
                fatura.musteri_ad = request.user.first_name
                fatura.tarih = datetime.now().date()
                fatura.miktar = totalprice
                fatura.hizmet = f"IPV6 Proxy ({quantity})"
                fatura.musteri_soyad = request.user.last_name
                fatura.save()
  
                import threading
                task_thread = threading.Thread(target=execute_commands, args=(task_id, server.ip_address, server.username, server.password, cmds))
                task_thread.start()
                
                return redirect('panel:my-proxies')

            else:
                servers = Server.objects.all()
                messages.error(request, "Please select a proxy type!")
                return render(request, "admin/panel/proxy/create.html", {'servers': servers})
        else:
            servers = Server.objects.all()
            messages.error(request, "Insufficient Balance!")
            return render(request, "admin/panel/proxy/create.html", {'servers': servers})
    else:
        user = request.user
        servers = Server.objects.all()
        return render(request, "admin/panel/proxy/create.html", {'servers': servers, 'user':user})



def privacy_policy(request):
    return render(request,"admin/dashboard/privacy-policy.html")


def terms_of_services(request):
    return render(request,"admin/dashboard/terms-of-service.html")

@login_required
def change_password(request, user_id):
    if request.user.id != user_id and not request.user.is_superuser:
        return redirect('some_error_page')  

    user = get_user_model().objects.get(id=user_id)
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password and check_password(current_password, user.password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user) 
            return redirect('panel:login') 
        else:
           
            pass

    return render(request, 'admin/login/change-password.html', {'user_id': user_id})


@login_required
def create(request):
    if request.method == "POST":
        balance = request.user.bakiye_miktari
        totalprice = Decimal(request.POST.get("totalprice", "0"))
        if balance >= totalprice : 
            cmds = []
            user = request.user
            unique_id = uuid.uuid4()
            proxy_cfg_path = f"/etc/3proxy/conf/{unique_id}"
            file_path = f"/etc/systemd/system/{unique_id}.service"
            
            file_cmd = f'echo "[Unit]" >> {file_path}'
            file_cmd1 = f'echo "Description=Add multiple IPv6 addresses to ens160" >> {file_path}'
            file_cmd0 = f'sudo echo "" >> {file_path}'
            file_cmd2 = f'sudo echo "[Service]" >> {file_path}'
            file_cmd3 = f'sudo echo "Type=oneshot" >> {file_path}'
            cmds.append(file_cmd)
            cmds.append(file_cmd1)
            cmds.append(file_cmd2)
            cmds.append(file_cmd3)
            cmds.append(file_cmd0)

            server_id = int(request.POST.get("server_id"))
            server = Server.objects.get(id=server_id)
            
            quantity = int(request.POST.get("quantity"))
            server.usage = int(server.usage) + quantity
            server.save()

            current_date = datetime.now()
            end_date_str = request.POST.get("time_period")
            current_date = datetime.now()

            # Yeni tarihi hesapla
            if end_date_str == "7":
                new_date = current_date + timedelta(days=7)
            elif end_date_str == "14":
                new_date = current_date + timedelta(days=14)
            elif end_date_str == "30":
                new_date = current_date + timedelta(days=30)
            else:
                # Varsayılan bir değer veya hata işleme
                new_date = current_date  # veya hata mesajı göster


            used_ports = list(map(int, server.used_port.split(',')))

            # Eğer used_port listesi boş değilse, en son sayıyı buluyoruz.
            if used_ports:
                last_port = max(used_ports)
            else:
                last_port = 2002  # used_port listesi boşsa varsayılan olarak 2002 alalım.

            # Yeni portu belirleyip, new_port ve used_port alanlarını güncelliyoruz.
            ilk = last_port + 1
            
    #########
            

            if "userName" in request.POST:
                username = request.POST.get("userName")
                password = request.POST.get("password")
                start_text = f'echo "\nauth strong\nallow {username}" >> {proxy_cfg_path}'
                passwd_text  = f'echo "\n{username}:CL:{password}" >> /etc/3proxy/conf/passwd'
                cmds.append(start_text)
                cmds.append(passwd_text)
                proxy = Proxies.objects.create(user=user, unique_id=unique_id, server=server, username=username, password=password, whitelist='', quantity=quantity , type="IPV6" , end_date = new_date)
                proxy.save()
                log = Proxy_log.objects.create(user=user, unique_id=unique_id)
                log.save()
            if 'userName' not in request.POST and 'password' not in request.POST and 'whitelist' not in request.POST:
                length = 6
                username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
                start_text = f'echo "\nauth strong\nallow {username}" >> {proxy_cfg_path}'
                passwd_text  = f'echo "\n{username}:CL:{password}" >> /etc/3proxy/conf/passwd'
                cmds.append(start_text)
                cmds.append(passwd_text)
                proxy = Proxies.objects.create(user=user, unique_id=unique_id, server=server, username=username, password=password, whitelist='', quantity=quantity, type="IPV6", end_date = new_date)
                proxy.save()
                log = Proxy_log.objects.create(user=user, unique_id=unique_id)
                log.save()
            if "whitelist" in request.POST:
                whitelist = request.POST.get("whitelist")
                start_text = f'echo "\nauth iponly \nallow * {whitelist}" >> {proxy_cfg_path}'
                cmds.append(start_text)
                proxy = Proxies.objects.create(user=user, unique_id=unique_id, server=server, username='', password='', whitelist=whitelist, quantity=quantity , type="IPV6", end_date = new_date)
                proxy.save()
                log = Proxy_log.objects.create(user=user, unique_id=unique_id)
                log.save()
            proxy_type = request.POST.get('proxy_type')
            if proxy_type in ['SOCKS5', 'HTTPs']:
                proxy_cmd = 'socks' if proxy_type == 'SOCKS5' else 'proxy'
                
                for x in range(quantity):
                    subnet = server.ipv6
                    seed()
                    network = IPv6Network(subnet)
                    address = IPv6Address(network.network_address + getrandbits(network.max_prefixlen - network.prefixlen))
                    b = str(address)
                    port_number = str(ilk)

                    c = " -e"
                    d = c + b
                    e = "-p"
                    f = str(ilk)
                    g = e + f

                    eth_card = server.eth_card
                    add_ip = f'/sbin/ip -6 addr add {b}/64 dev {eth_card}'
                    
                    cmds.append(add_ip)
                    
                    
                    file_cmd44 = f'sudo echo "ExecStart=/sbin/ip -6 addr add {b}/64 dev {eth_card}" >> {file_path}'
                    cmds.append(file_cmd44)

                    file_cmdz = f'sudo systemctl enable {unique_id}'
                    cmds.append(file_cmdz)
                    add_port_udp = f'iptables -A INPUT -p udp --dport {port_number} -j ACCEPT'
                    cmds.append(add_port_udp)

                    add_port_tcp = f'iptables -A INPUT -p tcp --dport {port_number} -j ACCEPT'
                    cmds.append(add_port_tcp)

                    server_proxy_adress = server.ip_address
                    command = f'echo "\n{proxy_cmd} -6 {g} -a -i{server_proxy_adress}{d}" >> {proxy_cfg_path}'
                    cmds.append(command)
                    
                    used_ports.append(ilk)
                    ilk += 1

                Server.objects.filter(id=server_id).update(
                used_port=','.join(map(str, used_ports))
                )    

                cmds.append(f'echo "\nflush" >> {proxy_cfg_path}')
                file_cmd0 = f'sudo echo "RemainAfterExit=yes" >> /etc/systemd/system/{unique_id}.service'
                file_cmd01 = f'sudo echo "" >> /etc/systemd/system/{unique_id}.service'
                file_cmd02 = f'sudo echo "[Install]" >> /etc/systemd/system/{unique_id}.service'
                file_cmd03 = f'sudo echo "WantedBy=multi-user.target" >> /etc/systemd/system/{unique_id}.service'
                s = f'sudo systemctl enable {unique_id}'
                s1 = f'sudo systemctl start {unique_id}'
                cmds.append(file_cmd0)
                cmds.append(file_cmd01)
                cmds.append(file_cmd02)
                cmds.append(file_cmd03)
                cmds.append(s)
                cmds.append(s1)

                proxy_cfg_add  = f'echo "\ninclude /conf/{unique_id} " >> /etc/3proxy/3proxy.cfg'
                cmds.append(proxy_cfg_add)
                restart_3proxy = "service 3proxy restart"
                cmds.append(restart_3proxy)
                # Open SSH connection and execute all commands
                
                task_id = str(uuid.uuid4())  # Generate a unique task identifier
                task = Task(task_id=task_id, status='running' , proxy_id = proxy.id)
                task.save()
                
                new_balance = balance - totalprice
                # Yeni bakiyeyi kullanıcı modeline kaydet
                request.user.bakiye_miktari = new_balance
                request.user.save()

                fatura = Fatura()
                fatura.user = request.user
                
                try:
                    # En son eklenen fatura nesnesini alın
                    last_fatura = Fatura.objects.latest('id')
                    new_fatura_no = int(last_fatura.fatura_no) + 1
                except Fatura.DoesNotExist:
                    # Eğer hiç fatura nesnesi yoksa başlangıç değeri olarak 1000 kullanın
                    new_fatura_no = 1000

                fatura.fatura_no = str(new_fatura_no)
                
                 # Eğer otomatik artan bir numara sistemi isterseniz bu kısmı değiştirmeniz gerekmektedir.
                fatura.musteri_ad = request.user.first_name
                fatura.tarih = datetime.now().date()
                fatura.miktar = totalprice
                fatura.hizmet = f"IPV6 Proxy ({quantity})"
                fatura.musteri_soyad = request.user.last_name
                fatura.save()
  
                import threading
                task_thread = threading.Thread(target=execute_commands, args=(task_id, server.ip_address, server.username, server.password, cmds))
                task_thread.start()
                
                return redirect('panel:my-proxies')

            else:
                servers = Server.objects.all()
                messages.error(request, "Please select a proxy type!")
                return render(request, "admin/panel/proxy/create.html", {'servers': servers})
        else:

            servers = Server.objects.all()
            
            messages.error(request, "Insufficient Balance!")
            return render(request, "admin/panel/proxy/create.html", {'servers': servers})
    else:
        servers = Server.objects.all()
        data = []
        for i in servers:
            if i.status == "1":
                if int(i.usage) <= int(i.limit):
                        data.append(i)
        return render(request, "admin/panel/proxy/create.html", {'servers': data})

def execute_commands(task_id, ip_address, username, password, cmds):
    # Open SSH connection and execute all commands
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_address, username=username, password=password)

    for cmd in cmds:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read())
        print(stderr.read())

    ssh.close()

    # Mark the task as completed (you can store this in a database or session)
    task = Task.objects.get(task_id=task_id)
    task.status = 'completed'
    task.save()


def check_task_status(request, task_id):
    task = get_object_or_404(Task, task_id=task_id)
    
    if task.status == 'completed':
        # Task has completed
        return JsonResponse({'status': 'completed'})
    else:
        # Task is still running or not found
        return JsonResponse({'status': 'running'})




def check_site(request, server_id, link):
    sunucu = Server.objects.get(id=server_id)
    username = sunucu.username
    password = sunucu.password
    ip_address = sunucu.ip_address
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_address, username=username, password=password)

    stdin, stdout, stderr = ssh.exec_command(f'ping6 -c 1 {link}')
    error = stderr.read().decode('utf-8')
    ssh.close()

    if error:  # Eğer bir hata mesajı varsa, ping başarısız oldu
        return JsonResponse({"message": "fail"})
    else:  # Eğer bir hata mesajı yoksa, ping başarılı oldu
        return JsonResponse({"message": "success"})

def payment2(request):
    merchant_id = '375401'
    merchant_key = b'f44MLzADS2z8jEj3'
    merchant_salt = b'dz4LLT5kFd1JfNwL'
    merchant_ok_url = 'https://v4proxy.net/panel/callback/basarili'
    merchant_fail_url = 'https://v4proxy.net/panel/callback/basarisiz'
    user_basket = html.unescape(json.dumps([['Altis Renkli Deniz Yatağı - Mavi', '18.00', 1],
                                            ['Pharmaso Güneş Kremi 50+ Yetişkin & Bepanthol Cilt Bakım Kremi', '33,25',
                                             2],
                                            ['Bestway Çocuklar İçin Plaj Seti Beach Set ÇANTADA DENİZ TOPU-BOT-KOLLUK',
                                             '45,42', 1]]))
    merchant_oid = 'OS' + random.randint(1, 9999999).__str__()
    test_mode = '1'
    debug_on = '1'
    non_3d = '0'
    client_lang = 'tr'
    non3d_test_failed = '0'
    user_ip = '88.224.125.29'
    email = 'testnon3d@paytr.com'
    payment_amount = "250"
    currency = 'TL'
    payment_type = 'card'
    user_name = 'Paytr Test'
    user_address = 'test test test'
    user_phone = '05555555555'
    card_type = 'bonus'
    installment_count = '0'
    hash_str = merchant_id + user_ip + merchant_oid + email + payment_amount + payment_type + installment_count + currency + test_mode + non_3d
    paytr_token = base64.b64encode(hmac.new(merchant_key, hash_str.encode() + merchant_salt, hashlib.sha256).digest())
    context = {
        'merchant_id': merchant_id,
        'user_ip': user_ip,
        'merchant_oid': merchant_oid,
        'email': email,
        'payment_type': payment_type,
        'payment_amount': payment_amount,
        'currency': currency,
        'test_mode': test_mode,
        'non_3d': non_3d,
        'merchant_ok_url': merchant_ok_url,
        'merchant_fail_url': merchant_fail_url,
        'user_name': user_name,
        'user_address': user_address,
        'user_phone': user_phone,
        'user_basket': user_basket,
        'debug_on': debug_on,
        'client_lang': client_lang,
        'paytr_token': paytr_token.decode(),
        'non3d_test_failed': non3d_test_failed,
        'installment_count': installment_count,
        'card_type': card_type
    }

    return render(request, 'admin/payment/deneme.html', context)

@csrf_exempt
def callback(request , status):
    if status == "basarili":
         return redirect('/panel/payment/basarili')
    elif status == "basarisiz":
        return redirect('/panel/payment/basarisiz')
    


@csrf_exempt
def payment_check2(request):
      
    if request.method != 'POST':
        return HttpResponse(str(''))

    post = request.POST
    
    # API Entegrasyon Bilgileri - Mağaza paneline giriş yaparak BİLGİ sayfasından alabilirsiniz.
    merchant_key = b'f44MLzADS2z8jEj3'
    merchant_salt = 'dz4LLT5kFd1JfNwL'

    # Bu kısımda herhangi bir değişiklik yapmanıza gerek yoktur.
    # POST değerleri ile hash oluştur.
    hash_str = post['merchant_oid'] + merchant_salt + post['status'] + post['total_amount']
    hash = base64.b64encode(hmac.new(merchant_key, hash_str.encode(), hashlib.sha256).digest())
    
    
    
    
    # Oluşturulan hash'i, paytr'dan gelen post içindeki hash ile karşılaştır
    # (isteğin paytr'dan geldiğine ve değişmediğine emin olmak için)
    # Bu işlemi yapmazsanız maddi zarara uğramanız olasıdır.
    if hash.decode('utf-8') != post['hash']:
        return HttpResponse(str('PAYTR notification failed: bad hash'))

    # BURADA YAPILMASI GEREKENLER
    # 1) Siparişin durumunu post['merchant_oid'] değerini kullanarak veri tabanınızdan sorgulayın.
    # 2) Eğer sipariş zaten daha önceden onaylandıysa veya iptal edildiyse "OK" yaparak sonlandırın.

    if post['status'] == 'success':  # Ödeme Onaylandı
        """
        BURADA YAPILMASI GEREKENLER
        1) Siparişi onaylayın.
        2) Eğer müşterinize mesaj / SMS / e-posta gibi bilgilendirme yapacaksanız bu aşamada yapmalısınız.
        3) 1. ADIM'da gönderilen payment_amount sipariş tutarı taksitli alışveriş yapılması durumunda değişebilir. 
        Güncel tutarı post['total_amount'] değerinden alarak muhasebe işlemlerinizde kullanabilirsiniz.
        """
        oid = post['merchant_oid']
        payment_track = PaymentTracking.objects.filter(merchant_oid=oid).first()
        user_track = payment_track.user
        actual_amount = float(post['total_amount']) / 100.0
        Bakiye.objects.create(user = user_track , bakiye_miktari = actual_amount , payment_method = "Credit Card" )
        username = user_track.username
        
        add_balance = user.objects.get(username = username)
        from decimal import Decimal
        actual_amount_decimal = Decimal(post['total_amount']) / 100
        add_balance.bakiye_miktari += actual_amount_decimal
        add_balance.save()
        
        return HttpResponse(str('OK'))
    else:  # Ödemeye Onay Verilmedi
        """
        BURADA YAPILMASI GEREKENLER
        1) Siparişi iptal edin.
        2) Eğer ödemenin onaylanmama sebebini kayıt edecekseniz aşağıdaki değerleri kullanabilirsiniz.
        post['failed_reason_code'] - başarısız hata kodu
        post['failed_reason_msg'] - başarısız hata mesajı
        """
        oid = post['merchant_oid']
        card = get_object_or_404(Proxy_number, oid=oid)
        card.delete()
        return HttpResponse(str('OK'))

def balance_check(request, user_id):
    try:
        balance_check = user.objects.get(pk=user_id)
        balance_check.bakiye_miktari
        return JsonResponse({"message": balance_check.bakiye_miktari})
    except user.DoesNotExist:
        return JsonResponse({"message": "fail"})



def fatura_pdf(request, fatura_id):
    fatura = Fatura.objects.get(pk=fatura_id)
    
    template = get_template('admin/payment/faturadeneme.html')
    user_data = get_object_or_404(user, id=request.user.id)
    context = {'fatura': fatura, 'user': user_data}
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fatura_{fatura_id}.pdf"'
    
    # UTF-8 Uyumlu PDF çıktısı için link callback fonksiyonu
    def link_callback(uri, rel):
        return uri
    
    # BytesIO kullanarak PDF oluştur
    pdf_file = BytesIO()
    pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file, encoding='utf-8', link_callback=link_callback)
    
    # BytesIO'dan PDF dosyasını response'a aktar
    response.write(pdf_file.getvalue())
    
    return response


def fatura_view(request , fatura_id):
    user_data = get_object_or_404(user, id=request.user.id)
    fatura = Fatura.objects.get(pk=fatura_id)
    tutar = round(fatura.miktar , 3)
    vergi = round((5 * tutar) / 6 , 3)
    vergi_yuzde = round((vergi *20 )/100 , 3)
    hesap = vergi - tutar
    return render(request, 'admin/payment/fatura_view.html' , {'user_data':user_data , 'fatura' : fatura , 'tutar':tutar, 'vergi':vergi , 'hesap':hesap,'vergi_yuzde':vergi_yuzde})