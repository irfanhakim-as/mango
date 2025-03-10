FROM ghcr.io/irfanhakim-as/dim:0.2.0-alpine-r1

# ================= DO NOT EDIT BEYOND THIS LINE =================

COPY dependencies/* /tmp/

RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -rf /tmp/*

COPY --chmod=0755 entrypoint.sh /

COPY root/* /"${APP}"/

COPY data/*.json data/

COPY models/*.py "${APP}"/models/

COPY settings/*.py "${APP}"/conf/

COPY commands/*.py "${APP}"/management/commands/

COPY base/*.py "${APP}"/

COPY lib/*.py lib/
