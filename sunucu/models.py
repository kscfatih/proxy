import subprocess
from django.db import models
from django.core.validators import validate_comma_separated_integer_list

class Server(models.Model):
    name = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    eth_card = models.CharField(max_length=200, null=True)
    ipv6 = models.CharField(max_length=200, null=True)
    ipv4 = models.CharField(max_length=200, null=True)
    location = models.CharField(max_length=200, null=True)
    used_port = models.TextField(validators=[validate_comma_separated_integer_list] , null=True)
    limit = models.CharField(max_length=200, null=True, blank=True)
    usage = models.CharField(max_length=200, null=True , blank=True)
    status = models.CharField(max_length=200, null=True , blank=True)
    image = models.CharField(max_length=200, null=True , blank=True)
    def run_command(self, command):
        # İçerideki çift tırnaklar yerine tek tırnak kullanılıyor
        full_command = f"sshpass -p {self.password} ssh -o StrictHostKeyChecking=no -l {self.username} {self.ip_address} '{command}'"
        result = subprocess.run(full_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')
    
    def update_conf_file(self, file_path, line_to_add):
        # İçerideki çift tırnaklar yerine tek tırnak kullanılıyor
        command = f'echo -e "{line_to_add}" | sudo tee -a {file_path}'
        output, error = self.run_command(command)
        
        ServerLog.objects.create(
            server=self, 
            command=command, 
            output=output, 
            error=error
        )

    def install_proxy(self):
        proxy_url = "https://github.com/z3APA3A/3proxy/releases/download/0.9.3/3proxy-0.9.3.x86_64.deb"
        download_command = f'wget {proxy_url}'
        install_command = "dpkg -i 3proxy-0.9.3.x86_64.deb"
        
        output, error = self.run_command(download_command)
        output2, error2 = self.run_command(install_command)

        # ServerLog nesnesini oluştur
        ServerLog.objects.create(
            server=self,
            command=download_command,
            output=output,
            error=error
        )
        ServerLog.objects.create(
            server=self,
            command=install_command,
            output=output2,
            error=error2
        )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super(Server, self).save(*args, **kwargs)
        
        if is_new:
            
           
            self.update_conf_file("/etc/security/limits.conf", "root hard nofile 999999\nroot soft nofile 999999")
            self.update_conf_file("/etc/sysctl.conf", "fs.file-max = 999999")
            self.install_proxy()

class ServerLog(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    command = models.TextField()
    output = models.TextField()
    error = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

