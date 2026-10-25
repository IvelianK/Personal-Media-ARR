# 0003. Verificar el idioma abriendo el fichero tras importarlo

**Estado:** aceptada

## Contexto

Sonarr y Radarr eligen release por su nombre, y el nombre no es fiable: `ESP` lo usan releases latinas, las banderas de muchos catálogos incluyen subtítulos y muchas releases no dicen el idioma. El protocolo Torznab no transporta las pistas de audio.

## Decisión

Dos capas. Antes de descargar, formatos personalizados sobre el nombre con una puntuación mínima que exige una marca de castellano. Después de importar, `langguard` abre el fichero con `ffprobe`, mira las pistas reales y, si no cumplen, borra, bloquea la release y deja que la app busque otra.

## Alternativas descartadas

- **Solo formatos personalizados.** Dejaron pasar dos releases sin castellano en la primera hora.
- **Comprobar antes de descargar.** No hay de dónde sacar la información sin descargar al menos la cabecera, y eso es justo lo que hace una importación con descarga en la nube.
- **Extensión dentro de Sonarr y Radarr.** No tienen sistema de extensiones para la decisión de importación; solo scripts y webhooks.

## Consecuencias

- (+) La biblioteca solo contiene lo que se ha comprobado.
- (+) Rechazar cuesta poco con descarga en la nube: cabeceras de unos MB.
- (-) Con descarga local, rechazar significa haber descargado el fichero entero.
- (-) Pistas sin etiqueta (`und`) obligan a fiarse del nombre.
- (=) Un servicio más que mantener, pequeño y con pruebas.
