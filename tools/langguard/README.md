# langguard

Webhook para Sonarr y Radarr con dos funciones:

1. **Verificar el idioma.** En cada importación lee las pistas de audio con `ffprobe`. Si falta el idioma exigido, borra el fichero, marca la release como fallida y la app busca otra. Si la importación era una mejora, no borra (la app ya quitó el fichero anterior): solo bloquea la release.
2. **Rescatar importaciones.** Cada `RESCUE_INTERVAL` segundos importa por API las descargas que Sonarr y Radarr no importan solas. Solo rellena huecos: nunca sustituye un fichero existente.

Cómo decide y por qué: [documento de idioma](../../docs/05-idioma.md).

## Configuración

| Variable | Por defecto | Qué es |
|---|---|---|
| `SONARR_URL` / `RADARR_URL` | `http://sonarr:8989` / `http://radarr:7878` | URL interna de cada app. Solo hace falta cambiarla si no usas los nombres del `compose.yaml` |
| `SONARR_API_KEY` / `RADARR_API_KEY` | vacío | Claves de API (Settings → General). Sin clave, el rescate de esa app no se ejecuta |
| `LANG_DEFAULT` | `spa` | Idioma exigido (ISO 639-2): `spa`, `eng`, `fra`, `deu`, `ita`, `por`, `jpn` |
| `LANG_BY_ROOT` | `/data/biblioteca/anime/=jpn` | Excepciones por carpeta, separadas por comas: `ruta=idioma` |
| `DOWNLOADS` | `/data/descargas` | Carpeta de descargas, con subcarpetas `sonarr` y `radarr` |
| `RESCUE_INTERVAL` | `600` | Segundos entre rescates. `0` lo desactiva |
| `WEBHOOK_AUTH` | sin valor; impide el arranque | `usuario:clave` para autenticación Basic |

Un idioma no soportado en `LANG_DEFAULT` o `LANG_BY_ROOT` impide el arranque con un mensaje claro, en lugar de fallar en cada importación.

## Conectarlo

En Sonarr y Radarr: **Settings → Connect → + → Webhook**, método POST, eventos **On Import** y **On Upgrade**, con el usuario y la clave de `WEBHOOK_AUTH`:

- Sonarr: `http://langguard:8080/sonarr`
- Radarr: `http://langguard:8080/radarr`

El botón **Test** debe dejar `webhook de prueba recibido` en el registro del contenedor.

## Pruebas

```bash
cd tools/langguard && python -m unittest -v
```

Sin dependencias fuera de la biblioteca estándar de Python. `ffprobe` solo hace falta para ejecutarlo de verdad, no para las pruebas.

## Seguridad

- `WEBHOOK_AUTH` es obligatorio: sin ella, cualquier contenedor de la red interna podría pedirle que borre un fichero de la biblioteca.
- Su puerto no se publica fuera de la red de la pila.
- Corre sin root (`568:568`), sin capacidades, con el sistema de ficheros de solo lectura y `/data` montado de solo lectura: los ficheros los mueven Sonarr y Radarr por su API.
- Rechaza peticiones de más de 1 MB y JSON mal formado; responde al webhook al momento y procesa en segundo plano.
- Las claves llegan por entorno desde `.env`; nunca se escriben en disco ni en el registro.
