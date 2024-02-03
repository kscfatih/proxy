"""
URL configuration for v4proxy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

from panel.views import set_language,privacy_policy,terms_of_services,login_user
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('', include('front.urls')),
    path('management/', admin.site.urls),
    path('management/', admin.site.urls),
    path('panel/', include('panel.urls')),
    path("login", login_user, name="login"),
    path('<str:language_code>/panel/', include('panel.urls')),
    path("set_language/<str:language>/", set_language, name="set-language"),
    path('paypal/',include('paypal.standard.ipn.urls')),
    path('accounts/', include('allauth.urls')),
    path('privacy-policy',privacy_policy,name="privacy-policy"),
    path('terms-of-service',terms_of_services,name="terms-of-service")
]
urlpatterns = i18n_patterns(
    *urlpatterns,
    prefix_default_language=False,
)

