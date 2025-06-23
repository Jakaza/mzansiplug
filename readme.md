<!-- [Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/mzansiplug
ExecStart=/home/ubuntu/mzansiplug/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/mzansiplug.sock mzansiplug.wsgi:application

[Install]
WantedBy=multi-user.target

 -->

server {
    listen 80;
    server_name 54.159.177.219;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/ubuntu/mzansiplug;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/mzansiplug.sock;
    }
}