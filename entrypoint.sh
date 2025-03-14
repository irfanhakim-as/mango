#!/usr/bin/env sh

export APP_ROOT="${APP_ROOT:-base}"
export APACHE_USER="${APACHE_USER:-www-data}"

# ================= DO NOT EDIT BEYOND THIS LINE =================

if [ -f "/etc/init.d/celeryd" ] && [ -f "/etc/init.d/celerybeat" ]; then
    BACKEND_SCHEDULER="celery"
fi

python3 manage.py makemigrations

python3 manage.py migrate

chmod -R 775 "/${APP_ROOT}" /var/log/apache2

chown -R "${APACHE_USER}": "/${APP_ROOT}" /var/log/apache2

python3 manage.py test

if [ ${?} -eq 0 ]; then
    python3 manage.py entrypoint > /dev/null 2>&1

    if [ "${BACKEND_SCHEDULER}" = "celery" ]; then
        /etc/init.d/celeryd start && /etc/init.d/celerybeat start
    fi

    for cmd in apache2ctl httpd; do
        if [ -x "$(command -v ${cmd})" ]; then
            "${cmd}" -D FOREGROUND; break
        fi
    done
else
    tail -f /dev/null
fi
