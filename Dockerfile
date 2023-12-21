FROM ghcr.io/irfanhakim-as/dim:0.0.3-stable-r1

ENV APP="base"

# ================= DO NOT EDIT BEYOND THIS LINE =================

COPY requirements.txt /tmp/

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY entrypoint.sh /

COPY root/*.py /${APP}/

COPY models/*.py ${APP}/models/

COPY settings/*.py ${APP}/settings/

COPY commands/*.py ${APP}/management/commands/

COPY base/*.py ${APP}/

COPY lib/*.py lib/
