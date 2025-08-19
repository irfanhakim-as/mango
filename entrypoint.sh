#!/usr/bin/env sh

# ================= DO NOT EDIT BEYOND THIS LINE =================

python3 manage.py makemigrations

python3 manage.py migrate

chmod -R 775 "/${APP_ROOT}" "${LOG_PATH}"

chown -R "${APACHE_USER}": "/${APP_ROOT}" "${LOG_PATH}"

python3 manage.py test

if [ ${?} -eq 0 ]; then
    python3 manage.py entrypoint > /dev/null 2>&1

    if [ -f "/etc/init.d/celeryd" ] && [ -f "/etc/init.d/celerybeat" ]; then
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
