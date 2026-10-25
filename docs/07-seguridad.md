# 7. Seguridad

## Qué se expone y qué no

| Servicio | Red local | Internet | Por qué |
|---|---|---|---|
| Jellyfin | Sí | Solo por VPN o túnel con control de acceso | Tiene usuarios y está pensado para ello, pero es una superficie grande |
| Seerr | Sí | Solo por VPN o túnel con control de acceso | Quien entra puede pedir contenido |
| Sonarr, Radarr, Prowlarr, Bazarr | Sí, por el proxy | **No** | Tienen claves de API de todo lo demás y pueden borrar la biblioteca |
| Cliente de descarga | No (solo red interna) | **No** | Con su API se puede añadir cualquier cosa |
| langguard | No (solo red interna) | **No** | Webhook con autenticación Basic obligatoria; solo lo llaman Sonarr y Radarr por la red `media` |

En el `compose.yaml` de ejemplo todo escucha en `127.0.0.1`. Si cambias `BIND` a `0.0.0.0`, recuerda que Docker publica puertos saltándose el cortafuegos del sistema.

## Credenciales

- Autenticación por formulario en todas las apps, **también en la red local**. El modo "sin autenticación para direcciones locales" deja entrar a cualquier equipo de casa comprometido.
- Usuario y contraseña distintos de los de cualquier otro servicio. Si los tienes en un gestor de contraseñas, mejor.
- Las claves de API van en `.env` con permisos `600`, nunca en el `compose.yaml` ni en un repositorio.
- La clave del servicio en la nube suele dar acceso completo a la cuenta. Trátala como una contraseña: si ha pasado por un chat, un ticket o una captura, rótala.
- Al terminar de configurar por scripts, borra cualquier fichero temporal con claves (`/tmp`, historiales de shell).

## Telemetría que viene activada

Revisa los valores por defecto de cada app. Dos ejemplos encontrados al montar esto:

- **Decypharr trae "Hearsay" activado.** Participa en una red pública y publica los hashes de lo que añades, para que otros sepan si un torrent está en caché. Los hashes no son títulos, pero un hash identifica exactamente un torrent. Se desactiva con `"hearsay": {"disabled": true}` en `config.json`.
- **Varias apps envían analíticas anónimas** de uso. En Sonarr, Radarr y Prowlarr: **Settings → General → Analytics**. En Bazarr: **Settings → General → Analytics**.

## Límites de la API del servicio en la nube

Los servicios en la nube limitan las peticiones por clave (en el probado, 100 por minuto). Esa clave la comparten el puente, cualquier utilidad que consulte la caché y cualquier otra app que la use, por ejemplo un reproductor en el móvil. Cuando se supera:

- Las lecturas del montaje devuelven `I/O error` o van a cientos de kB/s.
- El puente guarda en caché ese estado de error y sigue fallando aunque el límite ya se haya recuperado. Reiniciarlo lo limpia.

Mitigaciones: `skip_pre_cache: true`, un `rate_limit` del puente por debajo del límite real y no lanzar escaneos masivos (Intro Skipper, trickplay, extracción de capítulos) sobre el montaje remoto.

## Contenedores

| Medida | Dónde |
|---|---|
| Puertos solo en `127.0.0.1` | `BIND` en `.env` |
| `no-new-privileges` | Todos menos el puente FUSE, que necesita `fusermount` (setuid) |
| `langguard` sin capacidades y de solo lectura | `cap_drop: [ALL]`, `read_only: true` |
| `init: true` en el puente FUSE y en Seerr | Que una parada no deje procesos huérfanos |
| IPv6 desactivado en el puente | Con registros AAAA y sin conectividad IPv6, Go y busybox se quedaban esperando |
| Una red propia para la pila | `media`; el proxy del host usa los puertos vinculados a `127.0.0.1` |

## Copias de seguridad

Lo que merece copia es `config/`: bases de datos de Sonarr, Radarr, Prowlarr, Bazarr, Jellyfin y Seerr. Unos cientos de MB. La biblioteca, si son enlaces a un servicio en la nube, no necesita copia: se reconstruye desde el historial. Si son ficheros locales de tus propios discos, sí.

Las apps hacen copias propias (Sonarr y Radarr, semanales en `config/Backups`). Para restaurar, para la app y sustituye su carpeta de `config`.

---

Anterior: [Plugins de Jellyfin](06-plugins-jellyfin.md) · Siguiente: [Tropiezos](08-tropiezos.md) · Volver al [inicio](../README.md)
