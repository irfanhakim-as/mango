FROM ghcr.io/irfanhakim-as/dim:0.1.0-stable-r1

ENV APP="base"

# ================= DO NOT EDIT BEYOND THIS LINE =================

COPY entrypoint.sh /

COPY requirements.txt /tmp/

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY root/*.py /${APP}/

COPY data/*.json data/

COPY models/*.py ${APP}/models/

COPY settings/*.py ${APP}/conf/

COPY commands/*.py ${APP}/management/commands/

COPY base/*.py ${APP}/

COPY lib/*.py lib/
