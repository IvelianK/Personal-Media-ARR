# 4. Configuración

Orden recomendado: cliente de descarga, Sonarr y Radarr, Prowlarr, Bazarr, Jellyfin y por último Seerr, que necesita a todos los demás.

Todas las apps tienen API. Lo que sigue se puede hacer a mano en cada interfaz o por script; los valores son los mismos.

## Autenticación en todas

En cada app: **Settings → General → Security**, método **Forms**, obligatorio también en la red local. Un usuario y contraseña propios, distintos de los de cualquier otro servicio. Más en [Seguridad](07-seguridad.md).

## Cliente de descarga

### Perfil `local` (qBittorrent)

- **Downloads → Default Save Path:** `/data/descargas`.
- Categorías `sonarr` y `radarr`, con ruta `/data/descargas/sonarr` y `/data/descargas/radarr`.
- Límite de subida y proporción razonables. Recuerda que compartir es distribuir ([marco legal](01-marco-legal.md)).

### Perfil `nube` (Decypharr)

En `config/decypharr/config.json`, lo que importa:

| Clave | Valor | Por qué |
|---|---|---|
| `mount.type` | `dfs` | Sistema de ficheros propio, optimizado para lectura secuencial |
| `mount.mount_path` | `/data/remote` | Dentro de `/data`, visible para todas las apps |
| `mount.dfs.uid` / `gid` | `568` | Los mismos que el resto del stack |
| `download_folder` | `/data/descargas` | Donde deja los enlaces simbólicos |
| `default_download_action` | `symlink` | Enlace, no copia |
| `skip_pre_cache` | `true` | Sin esto lee el principio de **cada** fichero de cada pack al añadirlo. Con un pack de 73 episodios agota el límite de la API del servicio ([tropiezo](08-tropiezos.md#el-límite-de-peticiones-compartido)) |
| `debrids[].rate_limit` | Por debajo del límite de tu plan | El límite suele ser por clave, y la clave la comparten todas tus apps |
| `hearsay.disabled` | `true` | Viene activado y publica en una red pública los hashes de lo que añades ([seguridad](07-seguridad.md#telemetría-que-viene-activada)) |
| `use_auth` | `true` | Y un usuario propio desde `/register` |
| `arrs[]` | `sonarr` y `radarr` con su URL interna y clave | Para reparaciones y limpieza de cola |

## Sonarr y Radarr

### Carpetas raíz

| App | Carpeta | Perfil por defecto |
|---|---|---|
| Sonarr | `/data/biblioteca/series` | Español |
| Sonarr | `/data/biblioteca/anime` | Anime |
| Radarr | `/data/biblioteca/peliculas` | Español |

### Cliente de descarga

**Settings → Download Clients → + → qBittorrent.** Host `qbittorrent` o `decypharr`, puerto `8080` o `8282`, categoría `sonarr` o `radarr`.

- **Remove Completed: no.** Parece contraintuitivo, pero si Sonarr vuelve a pedir un hash que ya importó una vez (un pack de temporada del que ya tenías un episodio), lo da por importado al instante y el cliente borra la carpeta antes de que nadie la procese. Conservarla permite rescatarla ([tropiezo](08-tropiezos.md#el-pack-que-sonarr-daba-por-importado)).
- **Remove Failed: sí.**

### Definiciones de calidad

**Settings → Quality:** con descarga en la nube el tamaño no ocupa disco. Los mínimos por defecto rechazaban packs de temporada válidos ("12 GB es menos de lo permitido"). Mínimo a 0, sin máximo.

### Renombrado

**Settings → Media Management → Rename Episodes / Rename Movies: sí.** Los nombres de muchas fuentes son ilegibles; los que genera Sonarr (`Serie - S01E01 - Título Bluray-1080p.mkv`) son los que mejor entienden Jellyfin y Bazarr.

### Perfiles y formatos personalizados

La parte importante. Está entera en [Idioma](05-idioma.md).

### Conexiones

**Settings → Connect:**

| Conexión | Tipo | Eventos | URL o host |
|---|---|---|---|
| langguard | Webhook, POST | On Import, On Upgrade | `http://langguard:8080/sonarr` (o `/radarr`), con el usuario y la clave de `WEBHOOK_AUTH` |
| Jellyfin | Emby / Jellyfin | On Import, On Upgrade, On Rename, On Delete | Host `jellyfin`, puerto `8096`, clave de API de Jellyfin, "Update Library" sí |

El aviso a Jellyfin es necesario si usas descarga en la nube: un montaje FUSE no genera eventos de cambio, así que Jellyfin no se entera solo.

## Prowlarr

1. **Indexers → Add Indexer:** solo los que cumplan el [marco legal](01-marco-legal.md).
2. **Settings → Apps:** añade Sonarr y Radarr con sus URL internas (`http://sonarr:8989`, `http://radarr:7878`), sus claves de API y `Prowlarr Server` = `http://prowlarr:9696`. Sincronización completa.
3. Comprueba en Sonarr y Radarr (**Settings → Indexers**) que el indexador aparece. Sonarr exige que la búsqueda vacía de prueba devuelva resultados de categoría TV: un indexador que solo da películas no se sincroniza con él.

Si un indexador tarda mucho (más de unos 90 segundos), Sonarr lo marca como no disponible y deja de usarlo un tiempo. No vuelve a usarlo por mucho que lo arregles, hasta que caduque la penalización o lo borres y Prowlarr lo vuelva a crear.

## Bazarr

| Sección | Valor |
|---|---|
| Languages | Activar `Spanish`. Perfil "Castellano" con `es` |
| Defaults | Series y películas con el perfil "Castellano" |
| Sonarr / Radarr | `sonarr:8989` / `radarr:7878` con sus claves |
| Providers | Ver abajo |
| Use embedded subtitles | Sí: si el fichero ya trae subtítulos en español, no busca más |
| Security | Forms |

Proveedores con buena cobertura en español: **OpenSubtitles.com** (cuenta gratuita), `subtitulamostv`, `subtis`, `gestdown` y `tvsubtitles`. Revisa de dónde saca cada proveedor sus subtítulos antes de activarlo: algunos los extraen de releases sin licencia, y el criterio es el mismo que con los indexadores ([marco legal](01-marco-legal.md)).

No actives `embeddedsubtitles` como proveedor si la biblioteca vive en un montaje remoto: extrae los subtítulos leyendo el fichero entero.

## Jellyfin

1. Asistente inicial: idioma `es`, país `ES`, idioma de metadatos `es`. Así los títulos y sinopsis salen en castellano de España y no en el latino.
2. **Bibliotecas:** Películas (`/data/biblioteca/peliculas`), Series (`.../series`) y Anime (`.../anime`). En las tres:
   - Idioma de metadatos Español, país España.
   - **Monitorización en tiempo real: no** (con montaje remoto). El aviso llega desde Sonarr y Radarr.
   - **Extracción de imágenes de capítulos y trickplay: no** con montaje remoto. Lee cada vídeo entero.
3. **Usuario → Reproducción:** audio preferido `spa`, subtítulos `spa`, modo "Inteligente".
4. **Panel → Reproducción → Transcodificación:** VAAPI (gráficas AMD e Intel) con `/dev/dri/renderD128`, decodificación por hardware de H.264, HEVC, VP9 y AV1, mapeo de tonos activado.
5. **Panel → Claves de API:** crea una para Sonarr y Radarr.

Los plugins van en su propio documento: [Plugins de Jellyfin](06-plugins-jellyfin.md).

## Seerr

1. Primer acceso: **Use your Jellyfin account**, servidor `jellyfin`, puerto `8096`.
2. **Settings → Jellyfin:** sincroniza bibliotecas y activa las tres.
3. **Settings → Services → Radarr:** perfil "Español", carpeta `/data/biblioteca/peliculas`, disponibilidad mínima "Released".
4. **Settings → Services → Sonarr:**
   - Perfil "Español", carpeta `/data/biblioteca/series`.
   - **Anime profile:** "Anime", **Anime root folder:** `/data/biblioteca/anime`. Seerr detecta si una serie es anime y la manda con ese perfil y a esa carpeta.
5. **Settings → General:** idioma `es`, región `ES`.

A partir de aquí, pedir algo desde Seerr (o desde Jellyfin con el plugin) lo pone en marcha sin tocar nada más.

---

Anterior: [Despliegue](03-despliegue.md) · Siguiente: [Idioma](05-idioma.md) · Volver al [inicio](../README.md)
