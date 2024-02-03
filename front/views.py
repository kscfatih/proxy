from django.shortcuts import render
import requests
from .forms import ProxyForm
import time
import aiohttp
import asyncio

def index(request):
    return render(request,"front/dashboard/index.html")





def format_proxy(proxy):
    if proxy.startswith("http://"):
        proxy_type = "HTTP"
        ip, port, username, password = proxy.replace("http://", "").split(':')
    elif proxy.startswith("socks4://"):
        proxy_type = "SOCKS4"
        ip, port, username, password = proxy.replace("socks4://", "").split(':')
    elif proxy.startswith("socks5://"):
        proxy_type = "SOCKS5"
        ip, port, username, password = proxy.replace("socks5://", "").split(':')
    else:
        # Varsayılan olarak HTTP tipi atayabilirsiniz veya başka bir mantığa göre karar verebilirsiniz
        proxy_type = "HTTP"
        ip, port, username, password = proxy.split(':')

    formatted_proxy = f"http://{username}:{password}@{ip}:{port}"
    return formatted_proxy, ip, proxy_type

async def check_proxy(proxy_list):
    tasks = [check_proxy_async(proxy) for proxy in proxy_list if proxy.strip()]
    results = await asyncio.gather(*tasks)
    return results


async def check_proxy_async(proxy):
    formatted_proxy, ip, proxy_type = format_proxy(proxy)  # IP adresini alın
    start_time = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.google.com', proxy=formatted_proxy, timeout=10) as response:
                end_time = time.time()
                response_time = round((end_time - start_time) * 1000)
                is_active = response.status == 200
    except Exception as e:
        is_active = False
        response_time = None
    country = await get_country(ip) if is_active else 'Bilinmiyor'
    return proxy, is_active, response_time, country, proxy_type


async def get_country(ip):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://ip-api.com/json/{ip}') as response:
                json_response = await response.json()
                country = json_response.get('country')
                return country
    except Exception as e:
        print(f"IP sorgulama hatası: {e}")
        return None


async def proxy_check(request):
    result = []
    if request.method == 'POST':
        form = ProxyForm(request.POST)
        if form.is_valid():
            proxy_list = form.cleaned_data['proxy_data'].split('\n')
            results = await check_proxy(proxy_list)  # Asenkron fonksiyonu await ile çağırın
            result.extend(results)
    else:
        form = ProxyForm()
    return render(request, 'front/proxy_check.html', {'form': form, 'result': result})



