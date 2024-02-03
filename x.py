# run_delete_expired_proxies.py

import os
import django

# Django projenizin ana dizinini belirtin
django_project_dir = '/home/v4proxy'

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "v4proxy.settings")  # Django projenizin adını buraya ekleyin
django.setup()

from panel.tasks import delete_expired_proxies
import time

while True:
    delete_expired_proxies.delay()
    time.sleep(5)  # Her saatte bir çalıştır
