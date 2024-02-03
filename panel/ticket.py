from django.shortcuts import render
from datetime import datetime
from django.core.paginator import Paginator
from .models import Ticket,Proxies,Ticket_report
from django.http import JsonResponse , HttpResponse , HttpResponseRedirect
from django.contrib.auth.decorators import login_required
@login_required
def ticket(request):
    user = request.user
    status = request.GET.get('status')
    products = Proxies.objects.filter(user_id=user)
    answered_count = Ticket.objects.filter(status='answered',user=user).count()
    pending_count = Ticket.objects.filter(status='pending',user=user).count()
    closed_count = Ticket.objects.filter(status='closed',user=user).count()
    if status in ['answered', 'pending', 'closed']:
        tickets = Ticket.objects.filter(user=user, status=status)
    else:
        tickets = Ticket.objects.filter(user=user)

    tickets = tickets.order_by('-created_at')
    ticket_paginator = Paginator(tickets, 5)
    page_number = request.GET.get('page')
    ticket_page_obj = ticket_paginator.get_page(page_number)

    context = {
        'products' : products,
        'answered_count': answered_count,
        'pending_count': pending_count,
        'closed_count': closed_count,
        'tickets':ticket_page_obj
        }
    return render(request,"admin/ticket/index.html", context)

@login_required
def detail(request,id):
    ticket = Ticket.objects.get(id=id)
    messages = Ticket_report.objects.filter(ticket=id)
    context = {'messages':messages,'ticket':ticket}
    return render(request,"admin/ticket/detail.html",context)

@login_required
def create(request):

    if request.method == 'POST':
       title = request.POST.get('title')
       description = request.POST.get('description', 'boş')
       priority = request.POST.get('priority')
       product_id = request.POST.get('product_id')
       if product_id != 'yok':
        #context = {'product_id':product_id}
        #return render(request,"admin/ticket/index.html",context)

            product = Proxies.objects.get(id=product_id)
            
       else:
            product = None 
       user = request.user

       ticket = Ticket.objects.create(
           user=user,
           title=title,
           description=description,
           priority=priority,
           status = 'pending',
           product=product,
           created_at=datetime.now()    
       )

       Ticket_report.objects.create(
           description=description,
           processed_by='customer',
           created_at=datetime.now(),
           ticket=ticket
       )

       return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def answer(request,id):
    
    if request.method == 'POST':
        description = request.POST.get('description')
        ticket = Ticket.objects.get(id=id)
        Ticket_report.objects.create(
           description=description,
           processed_by='customer',
           created_at=datetime.now(),
           ticket=ticket
       )

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


