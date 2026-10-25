# langguard: verificador de idioma y rescate de importaciones para Sonarr y Radarr
# Fijada por digest; Dependabot la mantiene al día
FROM python:3.15-alpine@sha256:d44b1254cb92329418d164b22b20d86bbd3869d48e80e09e476531a409a728bb

LABEL org.opencontainers.image.title="langguard" \
      org.opencontainers.image.source="https://github.com/IvelianK/Personal-Media-ARR" \
      org.opencontainers.image.licenses="MIT"

RUN apk add --no-cache ffmpeg
COPY langguard.py /app/langguard.py
# Lectura para cualquier UID: el contenedor corre con el PUID del stack, no como root
RUN chmod 755 /app && chmod 644 /app/langguard.py

USER 568:568
EXPOSE 8080
CMD ["python", "-u", "/app/langguard.py"]
