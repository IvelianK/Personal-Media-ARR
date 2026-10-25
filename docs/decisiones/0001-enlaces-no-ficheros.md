# 0001. Enlaces a un servicio en la nube, no ficheros en el disco

**Estado:** aceptada, con la descarga local como alternativa documentada

## Contexto

El servidor tiene dos discos en espejo, lentos y con espacio limitado. Una biblioteca de películas en 4K ocupa varios TB. Además, compartir por torrent desde casa expone la IP del hogar.

## Decisión

El cliente de descarga es un puente que imita la API de qBittorrent y delega en un servicio en la nube. El resultado se monta por FUSE y la biblioteca son enlaces simbólicos. El perfil `local` del `compose.yaml` queda como alternativa para quien prefiera ficheros reales.

## Alternativas descartadas

- **Solo descarga local.** La opción por defecto de casi todas las guías. Exige espacio, desgasta discos y comparte desde la IP de casa.
- **Reproductor que lee directamente del servicio, sin biblioteca.** Más simple, pero sin perfiles, sin control de idioma y sin subtítulos gestionados.

## Consecuencias

- (+) La biblioteca ocupa kilobytes. Lo que el servicio ya tiene llega en segundos.
- (+) Sin tráfico P2P desde casa.
- (-) Dependencia total de un tercero y de su API: límites de peticiones, caídas, cambios de condiciones.
- (-) El ancho de banda de reproducción es el de internet, no el del disco. Con un enlace de 100 Mb/s no da para 4K remux.
- (-) Un montaje FUSE colgado puede bloquear contenedores ([tropiezo](../08-tropiezos.md#el-proceso-que-no-se-dejaba-matar)).
- (=) Lo que se puede descargar legalmente no cambia: el servicio es una herramienta, las fuentes siguen siendo las de [0005](0005-solo-fuentes-legitimas.md).
