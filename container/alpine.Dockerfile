FROM ghcr.io/irfanhakim-as/dim-alpine:0.2.1-alpine-r4 AS builder

COPY dependencies/* /tmp/

RUN cat /tmp/alpine.build-deps.txt | xargs apk add --no-cache && \
    . "${PYTHON_VENV_PATH}"/bin/activate && \
    python3 -m pip install --no-cache-dir -r /tmp/requirements.txt

# ================================================================

FROM ghcr.io/irfanhakim-as/dim-alpine:0.2.1-alpine-r4 AS runtime

RUN rm -rf "${PYTHON_VENV_PATH}"

COPY --from=builder "${PYTHON_VENV_PATH}" "${PYTHON_VENV_PATH}"

COPY --chmod=0755 entrypoint.sh /

COPY root/* /"${APP_ROOT}"/

COPY data/*.json /"${APP_ROOT}"/data/

COPY models/*.py /"${APP_ROOT}"/"${APP_ROOT}"/models/

COPY settings/*.py /"${APP_ROOT}"/"${APP_ROOT}"/conf/

COPY commands/*.py /"${APP_ROOT}"/"${APP_ROOT}"/management/commands/

COPY base/*.py /"${APP_ROOT}"/"${APP_ROOT}"/

COPY lib/*.py /"${APP_ROOT}"/lib/