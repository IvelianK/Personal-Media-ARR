# langguard: verificador de idioma y rescate de importaciones para Sonarr y Radarr
# Fijada por digest; Dependabot la mantiene al día
FROM python:3.13-alpine@sha256:bf12ecc0bea3f171d55145dd02c78b5eeb09f30ee2ac9cc2b4c9e4e8f5e30741

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
