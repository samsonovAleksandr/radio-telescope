FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-numpy rtl-sdr ca-certificates && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin observer \
    && install -d -o observer -g observer /data
COPY web /opt/observer
ENV DATA_DIR=/data PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 10001:10001
EXPOSE 8080
CMD ["python3","/opt/observer/server.py"]
