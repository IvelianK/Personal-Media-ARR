# 0006. Las apps de gestión, solo en la red local

**Estado:** aceptada

## Contexto

Sonarr, Radarr, Prowlarr y Bazarr guardan claves de API de todo lo demás y pueden borrar la biblioteca entera. Son objetivo habitual de escaneos en internet, y su autenticación no está pensada para exposición pública.

## Decisión

Ningún puerto publicado fuera de `127.0.0.1`. Se accede por un proxy inverso con TLS y nombres del DNS local. Desde fuera de casa, solo por VPN de malla. Jellyfin y Seerr pueden publicarse con un túnel y control de acceso; el resto, nunca. Autenticación por formulario en todas, también en la red local.

## Alternativas descartadas

- **Publicarlas con autenticación básica del proxy.** Una capa más, pero sigue siendo una contraseña frente a internet.
- **Sin autenticación en la red local.** Cómodo, pero cualquier dispositivo de casa comprometido tiene acceso total.

## Consecuencias

- (+) Superficie expuesta mínima.
- (-) Para pedir algo desde fuera hace falta la VPN o Seerr publicado.
