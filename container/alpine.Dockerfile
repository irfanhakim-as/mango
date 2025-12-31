FROM ghcr.io/irfanhakim-as/dim-alpine:0.4.0-stable-r1

# ================= DO NOT EDIT BEYOND THIS LINE =================

COPY dependencies/* /tmp/

RUN sort /tmp/alpine.build-deps.txt > /tmp/alpine.build-deps.tmp && \
    apk info | sort > /tmp/alpine.run-deps.tmp && \
    comm -23 /tmp/alpine.build-deps.tmp /tmp/alpine.run-deps.tmp > /tmp/alpine.build-deps.txt && \
    apk add --no-cache --virtual .build-deps $(cat /tmp/alpine.build-deps.txt) && \
    python3 -m pip install --no-cache-dir -r /tmp/requirements.txt && \
    # ln -sf "${PYTHON_VENV_PATH}"/lib/python3.8/site-packages/backports_zoneinfo-0.2.1.dist-info "${PYTHON_VENV_PATH}"/lib/python3.8/site-packages/backports.zoneinfo-0.2.1.dist-info && \
    ln -sf "${PYTHON_VENV_PATH}"/bin/celery /usr/local/bin/celery && \
    apk del .build-deps && \
    rm -rf /tmp/*

COPY --chmod=0755 entrypoint.sh /

COPY root/* /"${APP_ROOT}"/

COPY data/*.json /"${APP_ROOT}"/data/

COPY models/*.py /"${APP_ROOT}"/"${APP_ROOT}"/models/

COPY settings/*.py /"${APP_ROOT}"/"${APP_ROOT}"/conf/

COPY commands/*.py /"${APP_ROOT}"/"${APP_ROOT}"/management/commands/

COPY base/*.py /"${APP_ROOT}"/"${APP_ROOT}"/

COPY lib/*.py /"${APP_ROOT}"/lib/