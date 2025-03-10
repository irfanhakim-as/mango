FROM ghcr.io/irfanhakim-as/dim:0.2.0-alpine-r1

# ================= DO NOT EDIT BEYOND THIS LINE =================

COPY dependencies/* /tmp/

RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -rf /tmp/*

COPY --chmod=0755 entrypoint.sh /

COPY root/* /"${APP_ROOT}"/

COPY data/*.json /"${APP_ROOT}"/data/

COPY models/*.py /"${APP_ROOT}"/"${APP_ROOT}"/models/

COPY settings/*.py /"${APP_ROOT}"/"${APP_ROOT}"/conf/

COPY commands/*.py /"${APP_ROOT}"/"${APP_ROOT}"/management/commands/

COPY base/*.py /"${APP_ROOT}"/"${APP_ROOT}"/

COPY lib/*.py /"${APP_ROOT}"/lib/