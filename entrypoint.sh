#!/bin/bash

export APP_ROOT="base"

# ================= DO NOT EDIT BEYOND THIS LINE =================

if [ -f "/etc/init.d/celeryd" ] && [ -f "/etc/init.d/celerybeat" ]; then
    BACKEND_SCHEDULER="celery"
fi

python3 manage.py makemigrations

python3 manage.py migrate

chmod -R 775 /${APP_ROOT} /var/log/apache2

chown -R www-data: /${APP_ROOT} /var/log/apache2

python3 manage.py test

if [ ${?} -eq 0 ]; then
    python3 manage.py entrypoint &> /dev/null

    if [ "${BACKEND_SCHEDULER}" = "celery" ]; then
        /etc/init.d/celeryd start && /etc/init.d/celerybeat start
    fi

    apache2ctl -D FOREGROUND
else
    tail -f /dev/null
fi
