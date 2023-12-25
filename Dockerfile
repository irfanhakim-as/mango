FROM ghcr.io/irfanhakim-as/dim:0.1.0-update-r2

ENV APP="base"

# ================= DO NOT EDIT BEYOND THIS LINE =================

COPY entrypoint.sh /

COPY requirements.txt /tmp/

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY root/*.py /${APP}/

COPY models/*.py ${APP}/models/

COPY settings/*.py ${APP}/conf/

COPY commands/*.py ${APP}/management/commands/

COPY base/*.py ${APP}/

COPY lib/*.py lib/
