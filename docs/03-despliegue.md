# 3. Despliegue

De cero a todo arrancado. Comandos para un host Linux con Docker Compose v2; en TrueNAS SCALE, por SSH.

## 1. Requisitos

| Requisito | Por qué |
|---|---|
| Docker con Compose v2 | Toda la pila es un `compose.yaml` |
| Un sistema de ficheros con espacio para configuraciones (unos pocos GB) | Bases de datos, carátulas y cachés |
| Espacio para la biblioteca, si descargas en local | Con descarga en la nube, la biblioteca son enlaces |
| Gráfica integrada o dedicada (opcional) | Transcodificar en Jellyfin sin quemar CPU |
| `/dev/fuse` (solo perfil `nube`) | El montaje del servicio en la nube |
| Enlace de red de 1 Gb/s | Un 4K remux no cabe en 100 Mb/s. Compruébalo con `ethtool <interfaz>` |

## 2. Estructura

Crea también las carpetas de configuración y caché de cada app. Si no existen, Docker las crea como root y las apps que corren sin root (Jellyfin, Seerr) no arrancan.

```bash
sudo mkdir -p /mnt/pool/apps/media/{config/{prowlarr,sonarr,radarr,bazarr,jellyfin,seerr,qbittorrent,decypharr},biblioteca/{peliculas,series,anime},descargas,remote,cache/{jellyfin,decypharr}}
```

```bash
sudo chown -R 568:568 /mnt/pool/apps/media
```

En TrueNAS, crea antes un dataset para `media`: así puedes hacerle instantáneas y borrarlo de una vez.

## 3. Configuración

```bash
git clone https://github.com/IvelianK/Personal-Media-ARR.git
```

```bash
cd Personal-Media-ARR/deploy && cp .env.example .env && chmod 600 .env
```

Edita `.env`, que vive junto a `compose.yaml` en `deploy/`: como mínimo `MEDIA_ROOT`, `PUID`, `PGID` y `WEBHOOK_AUTH`. Si el host tiene gráfica para transcodificar, descomenta `devices` en el servicio `jellyfin` y pon `RENDER_GID`. Las claves de Sonarr y Radarr se rellenan después del primer arranque.

## 4. Primer arranque

Elige perfil: `local` (qBittorrent en el servidor) o `nube` (Decypharr con un servicio en la nube).

```bash
docker compose --profile local up -d --build
```

Espera a que Sonarr y Radarr arranquen y obtén sus claves de API. Los comandos siguientes muestran secretos en el terminal: no copies la salida a tickets ni al historial de un informe.

```bash
grep -o '<ApiKey>[^<]*' /mnt/pool/apps/media/config/sonarr/config.xml
```

```bash
grep -o '<ApiKey>[^<]*' /mnt/pool/apps/media/config/radarr/config.xml
```

Ponlas en `.env` y recrea solo `langguard`. Hasta entonces, el rescate de importaciones no hace nada:

```bash
docker compose up -d langguard
```

## 5. Proxy inverso y DNS local

Las apps solo escuchan en `127.0.0.1`. Pon delante tu proxy de siempre. Con Caddy y un certificado por DNS:

```
sonarr.example.com {
    reverse_proxy 127.0.0.1:8989
}
```

Repite para `radarr` (7878), `prowlarr` (9696), `bazarr` (6767), `seerr` (5055) y `jellyfin` (8096). En tu DNS local (AdGuard Home, Pi-hole, el router) reescribe esos nombres a la IP del servidor para no salir a internet.

No publiques Sonarr, Radarr, Prowlarr, Bazarr ni el cliente de descarga en internet. Si necesitas acceso desde fuera, usa una VPN de malla. Detalle en [Seguridad](07-seguridad.md).

## 6. Comprobación

```bash
docker compose ps
```

Todos `Up` y, los que lo tienen, `(healthy)`. Si usas el perfil `nube`, comprueba que el montaje se ve desde otra app:

```bash
docker exec sonarr ls /data/remote
```

Si sale vacío, revisa la propagación (`rshared` en el puente, `rslave` en el resto) en la [arquitectura](02-arquitectura.md#con-descarga-en-la-nube).

## Actualizar

Con el mismo perfil que usaste al arrancar, para que también se actualice el cliente de descarga y se reconstruya `langguard`:

```bash
docker compose --profile local pull --ignore-buildable && docker compose --profile local up -d --build
```

Fija versiones en lugar de `latest` si prefieres actualizar a mano: Dependabot propondrá los cambios en tu fork.

## Desmontarlo todo

Parar y borrar contenedores, imágenes y red:

```text
docker compose --profile local --profile nube down --rmi all
```

Los datos siguen en `MEDIA_ROOT`. Borrarlos es irreversible; si es un dataset, `zfs destroy` sobre él. Antes de destruirlo, comprueba que no queda un montaje FUSE activo (`grep remote /proc/self/mountinfo`): un `stat` sobre un montaje colgado bloquea el terminal ([tropiezo](08-tropiezos.md#el-proceso-que-no-se-dejaba-matar)).

---

Anterior: [Arquitectura](02-arquitectura.md) · Siguiente: [Configuración](04-configuracion.md) · Volver al [inicio](../README.md)
