FROM ghcr.io/irfanhakim-as/dim-alpine:0.2.1-alpine-r2

ENV APP_ROOT="base"

# ================= DO NOT EDIT BEYOND THIS LINE =================

COPY dependencies/* /tmp/

RUN . "${PYTHON_VENV_PATH}"/bin/activate && \
    python3 -m pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -rf /tmp/*

COPY --chmod=0755 entrypoint.sh /

COPY root/* /"${APP_ROOT}"/

COPY data/*.json /"${APP_ROOT}"/data/

COPY models/*.py /"${APP_ROOT}"/"${APP_ROOT}"/models/

COPY settings/*.py /"${APP_ROOT}"/"${APP_ROOT}"/conf/

COPY commands/*.py /"${APP_ROOT}"/"${APP_ROOT}"/management/commands/

COPY base/*.py /"${APP_ROOT}"/"${APP_ROOT}"/

COPY lib/*.py /"${APP_ROOT}"/lib/