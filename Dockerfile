FROM ghcr.io/irfanhakim-as/dim:0.2.0-stable-r1

ARG APP="base"

# ================= DO NOT EDIT BEYOND THIS LINE =================

COPY --chmod=0755 entrypoint.sh /

COPY requirements.txt /tmp/

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY root/* /"${APP}"/

COPY data/*.json data/

COPY models/*.py "${APP}"/models/

COPY settings/*.py "${APP}"/conf/

COPY commands/*.py "${APP}"/management/commands/

COPY base/*.py "${APP}"/

COPY lib/*.py lib/
