#!/bin/bash

export APP_ROOT="base"

# ================= DO NOT EDIT BEYOND THIS LINE =================

python3 manage.py makemigrations

python3 manage.py migrate

chmod -R 775 /$APP_ROOT \
        /var/log/apache2

chmod 755 /etc/init.d/celeryd \
        /etc/init.d/celerybeat

chmod 640 /etc/default/celeryd

chown -R www-data: /$APP_ROOT /var/log/apache2

python3 manage.py test

if [ $? -eq 0 ]; then
    python3 manage.py entrypoint &> /dev/null
    
    /etc/init.d/celeryd start && /etc/init.d/celerybeat start
    
    apache2ctl -D FOREGROUND
else
    tail -f /dev/null
fi
