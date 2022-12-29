FROM ghcr.io/irfanhakim-as/dim:0.0.1-stable

ENV APP="base"

# ================= DO NOT EDIT BEYOND THIS LINE =================

COPY celery/default/* /etc/default/

COPY celery/init.d/* /etc/init.d/

COPY entrypoint.sh /

COPY requirements.txt /tmp/

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY base/*.py $APP/

COPY lib/*.py lib/

COPY commands/*.py $APP/management/commands/
