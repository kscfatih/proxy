from django.urls import path
from . import views,ticket,payment
from django.urls import  include

app_name = 'panel'

urlpatterns = [
    path('', views.index, name='home'),
    path('login', views.login_user, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout_user, name='logout'),
    path('rastgele', views.rastgele, name='rastgele'),
    path('my-proxies', views.proxies, name='my-proxies'),
    path('create', views.create, name='create'),
    path('create-48', views.create_48, name='create-48'),
    path('change-password/<int:user_id>/', views.change_password, name='change_password'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('ticket', ticket.ticket, name='ticket'),
    path('ticket-detail/<int:id>', ticket.detail,name='ticket-detail'),
    path('create-ticket' , ticket.create , name='create-ticket'),
    path('ticket-answer/<int:id>' , ticket.answer , name='ticket-answer'),
    path('payment/<str:status>', payment.payment, name='status'),
    path('payment', payment.payment, name='payment'),
    path('view_proxy/<int:id>', views.view_proxy, name='view_proxy'),
    path('task/<str:task_id>', views.check_task_status, name='task'),
    path('check_site/<int:server_id>/<path:link>/', views.check_site),
    path('payment2/', views.payment2),
    path('payment_check', views.payment_check2),
    path('balance-check/<int:user_id>', views.balance_check),
    path('callback/<str:status>', views.callback),
    path('add-card', payment.save_card),
    path('delete-card/<int:id>', payment.delete_card),
    path('hesap/<str:merchant_oid>/<str:payment_amount>', payment.hesap),
    path('fatura/<int:fatura_id>/pdf/', views.fatura_pdf, name='fatura_pdf'),
    path('bincodecontrol/<int:bincode>/', payment.bin_code_control , name='bin_code_control' ),
    path('invoice-view', payment.invoiceView , name='invoice-view' ),
    path('paypall', payment.paypall  ),
    path('payment-completed/', payment.successful, name='payment-completed'),
    path('payment-failed/', payment.cancelled, name='payment-failed'),
    path('fatura-view/<int:fatura_id>', views.fatura_view),
    path('accounts/', include('allauth.urls')),
    path('account-detail', views.account_settings, name='account-detail'),

    
    ]

