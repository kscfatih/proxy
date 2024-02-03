from django.db.models.signals import post_save , post_delete
from django.dispatch import receiver
from .models import Ticket_report, Ticket , Proxies
from .middleware import user_local
import paramiko

@receiver(post_save, sender=Ticket_report)
def post_save_ticket_report(sender, instance, created, **kwargs):
    if created:
        current_user = getattr(user_local, 'current_user', None)
        if current_user and not current_user.is_anonymous:
            instance.processed_by = current_user.first_name
            instance.save()

            ticket = instance.ticket
            if ticket:
                ticket.status = 'Answered' if current_user.is_superuser else 'Pending'
                ticket.save()


@receiver(post_delete, sender=Proxies)
def post_delete_proxy(sender, instance, **kwargs):
    server = instance.server
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server.ip_address, username="root", password=server.password)
        stdin, stdout, stderr = ssh.exec_command('if [ ! -d "/home/proxy_log" ]; then mkdir /home/proxy_log; fi')
        print(stdout.readlines())
        stdin, stdout, stderr = ssh.exec_command(f'cp /etc/3proxy/conf/{instance.unique_id} /home/proxy_log')
        print(stdout.readlines())
        stdin, stdout, stderr = ssh.exec_command(f'rm -rf /etc/systemd/system/{instance.unique_id}.service')
        print(stdout.readlines())
        stdin, stdout, stderr = ssh.exec_command(f'rm -rf /etc/3proxy/conf/{instance.unique_id}')
        print(stdout.readlines())
        stdin, stdout, stderr = ssh.exec_command(f"sed -i '/{instance.unique_id}/d' /etc/3proxy/3proxy.cfg")
        print(stdout.readlines())
        stdin, stdout, stderr = ssh.exec_command("service 3proxy restart")
        print(stdout.readlines())
        ssh.close()
    except Exception as e:
        print(f"SSH bağlantısı sırasında hata oluştu: {e}")  
    