# 6. Plugins de Jellyfin

Jellyfin funciona bien sin plugins. Con unos pocos se convierte en la consola principal de todo el stack: pides, ves lo que llega y lo reproduces sin salir de su interfaz.

Revisado en octubre de 2026 con Jellyfin 12. Todos los repositorios citados estaban activos y sin archivar en esa fecha. Instala de uno en uno y comprueba que todo sigue bien antes del siguiente.

## Cómo se instalan

Los oficiales vienen en el catálogo. Los de terceros se añaden desde un repositorio:

1. **Panel → Plugins → Repositorios → +**: nombre y URL del manifiesto que da cada proyecto en su README.
2. **Panel → Plugins → Catálogo**: busca el plugin e instala.
3. Reinicia Jellyfin y recarga el navegador con <kbd>Ctrl</kbd> + <kbd>F5</kbd>.

> Jellyfin 12 usa en varios proyectos una URL de manifiesto distinta de la de 10.11. Copia la del README del proyecto para tu versión, no la de un tutorial antiguo.

## Seerr dentro de Jellyfin: la consola principal

### Jellyfin Enhanced

[n00bcodr/Jellyfin-Enhanced](https://github.com/n00bcodr/Jellyfin-Enhanced), GPL-3.0.

Es el plugin que une Jellyfin y Seerr. Una vez conectado:

- La búsqueda de Jellyfin enseña también lo que **no** tienes, con un botón para pedirlo a Seerr.
- Una pestaña de descubrimiento con lo que Seerr recomienda, dentro de Jellyfin.
- Estado de las peticiones y etiquetas de *arr en la ficha de cada título.
- Además: insignias de calidad en las carátulas (4K, HDR, Dolby Vision, Atmos), notas de TMDB, atajos de teclado, pausa con información, salto automático de intro y créditos usando los segmentos que detecta Intro Skipper, y "Spoiler Guard" para no ver sinopsis de lo que no has visto.

Configuración: **Panel → Plugins → Jellyfin Enhanced → Seerr**. URL interna de Seerr (`http://seerr:5055`), su clave de API (**Seerr → Settings → General**) y qué usuarios pueden pedir. Funciona en la web y en los clientes que cargan la web; las apps nativas de TV ven solo las funciones de servidor.

### JellyBridge (alternativa)

[kinggeorges12/JellyBridge](https://github.com/kinggeorges12/JellyBridge), GPL-3.0.

Otro enfoque: importa el contenido de descubrimiento de Seerr como una biblioteca más de Jellyfin. Marcar un título como favorito crea la petición. Útil si quieres que funcione también en apps de TV que no cargan scripts web. No lo combines con la integración de Seerr de Jellyfin Enhanced: dos caminos para pedir lo mismo confunden.

## Interfaz

| Plugin | Repositorio | Licencia | Qué añade |
|---|---|---|---|
| File Transformation | [IAmParadox27/jellyfin-plugin-file-transformation](https://github.com/IAmParadox27/jellyfin-plugin-file-transformation) | GPL-3.0 | Requisito de los demás plugins de interfaz: modifica la web en memoria en lugar de reescribir `index.html`, que en Docker suele fallar por permisos |
| Home Screen Sections | [IAmParadox27/jellyfin-plugin-home-sections](https://github.com/IAmParadox27/jellyfin-plugin-home-sections) | GPL-3.0 | Filas de inicio configurables: "Porque viste...", "Recién añadido en anime", etc. |
| Media Bar | [IAmParadox27/jellyfin-plugin-media-bar](https://github.com/IAmParadox27/jellyfin-plugin-media-bar) | Sin declarar | Banner rotatorio con fondos y logos en la portada. Hay una variante, [MakD/Jellyfin-Media-Bar](https://github.com/MakD/Jellyfin-Media-Bar) |

## Reproducción

| Plugin | Repositorio | Licencia | Qué añade |
|---|---|---|---|
| Intro Skipper | [intro-skipper/intro-skipper](https://github.com/intro-skipper/intro-skipper) | GPL-3.0 | Detecta intros y créditos analizando el audio y los guarda como segmentos; Jellyfin enseña su botón nativo de "Saltar" |

Con descarga en la nube, Intro Skipper tiene que leer el audio de cada episodio. Limita su tarea programada a horas tranquilas o a las bibliotecas que lo merezcan, o agotarás el límite de la API del servicio.

## Metadatos y subtítulos

| Plugin | Repositorio | Licencia | Qué añade |
|---|---|---|---|
| Fanart | [jellyfin/jellyfin-plugin-fanart](https://github.com/jellyfin/jellyfin-plugin-fanart) | MIT | Logos, fondos y carátulas de fanart.tv |
| Open Subtitles | [jellyfin/jellyfin-plugin-opensubtitles](https://github.com/jellyfin/jellyfin-plugin-opensubtitles) | GPL-3.0 | Búsqueda de subtítulos desde el reproductor. Complementa a Bazarr, no lo sustituye |

## Estadísticas y seguimiento

| Pieza | Repositorio | Licencia | Qué añade |
|---|---|---|---|
| Playback Reporting | [jellyfin/jellyfin-plugin-playbackreporting](https://github.com/jellyfin/jellyfin-plugin-playbackreporting) | GPL-3.0 | Quién vio qué, cuándo y cómo (directo o transcodificado) |
| Trakt | [jellyfin/jellyfin-plugin-trakt](https://github.com/jellyfin/jellyfin-plugin-trakt) | MIT | Sincroniza lo visto con Trakt |
| Jellystat | [CyferShepard/Jellystat](https://github.com/CyferShepard/Jellystat) | MIT | No es un plugin: es una app aparte con panel de estadísticas. Otro contenedor, otra base de datos |

## Lo que no hace falta

- Plugins de "descarga desde Jellyfin" o que buscan contenido en fuentes externas: Seerr y las *arr ya hacen ese trabajo, con control de calidad e idioma.
- Plugins que añaden canales o catálogos de terceros cuyo origen no puedes verificar. Mismo criterio que con los indexadores ([marco legal](01-marco-legal.md)).

## Orden sugerido

1. File Transformation.
2. Jellyfin Enhanced, y conectarlo a Seerr.
3. Intro Skipper.
4. Home Screen Sections y Media Bar.
5. Fanart, Playback Reporting y el resto, según te hagan falta.

---

Anterior: [Idioma](05-idioma.md) · Siguiente: [Seguridad](07-seguridad.md) · Volver al [inicio](../README.md)
