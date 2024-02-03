# myapp/forms.py
from django import forms

class ProxyForm(forms.Form):
    proxy_data = forms.CharField(widget=forms.Textarea, label='Proxy Listesi')
