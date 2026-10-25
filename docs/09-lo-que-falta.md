# 9. Lo que falta

Dos listas distintas. La primera, lo que le faltaría a **este** montaje para ser perfecto y que se puede hacer hoy. La segunda, lo que falta en las propias aplicaciones y en el ecosistema, y que ningún montaje puede arreglar del todo desde fuera.

## Para un stack perfecto

| Pieza | Qué resolvería | Esfuerzo |
|---|---|---|
| Enlace de 1 Gb/s en el servidor | Reproducir 4K remux sin cortes desde un montaje remoto | Un cable |
| Fuentes legítimas con buena cobertura en castellano | Sin ellas, el resto del stack no tiene qué ordenar. Tiendas sin DRM, colecciones abiertas, tus propios discos | Variable |
| Búsqueda periódica de lo que falta | Sonarr y Radarr no vuelven a buscar solos lo que está "pendiente" salvo por RSS. Un buscador programado (o una tarea en la propia app) lo reintenta | Bajo |
| Limpieza automática | Borrar lo visto hace meses o lo que nadie ha abierto. Maintainerr o Janitorr hacen esto con reglas | Bajo |
| Avisos | Una notificación cuando algo se rechaza por idioma o lleva un día sin importarse | Bajo |
| Copias de `config/` fuera del servidor | Las bases de datos son lo único irrecuperable | Bajo |
| Perfiles versionados | Formatos y perfiles en un fichero que se aplica con Profilarr o Recyclarr, en lugar de crearlos a mano | Medio |
| Un normalizador publicado y probado | El diseño está en la [arquitectura](02-arquitectura.md#el-normalizador-torznab); falta una versión genérica para fuentes legítimas | Medio |
| Copia de la biblioteca local | Si son ripeos de tus discos, una copia en otro sitio. Si son enlaces, no hace falta | Variable |

## Lo que falta en las aplicaciones

### Sonarr y Radarr

- **No saben qué pistas de audio trae una release antes de descargarla.** Deciden por el nombre. Sonarr 5 enseña todas las pistas, pero solo **después** de importar. Haría falta que los formatos personalizados pudieran evaluarse también con la información real del fichero tras importarlo, y actuar (rechazar y buscar otra) si no cumple. Es lo que hace `langguard` desde fuera.
- **"Spanish" es un solo idioma.** Radarr tiene "Spanish (Latino)" en algunos sitios, pero el parser no distingue de forma fiable. Haría falta una variante regional (`es-ES`, `es-419`) en el modelo de idiomas y en el parser.
- **El estado "importado" va por hash, no por fichero.** Si el mismo torrent se pide para otro episodio, se da por hecho. Haría falta comprobar qué ficheros del torrent se importaron realmente.
- **Las importaciones manuales con "mejora" borran antes de mover.** Si el movimiento falla, te quedas sin ninguno de los dos. Haría falta mover primero a un temporal y borrar después.
- **No saben qué hacer con un nombre sin año.** Aunque la búsqueda fuera por IMDb ID y el indexador lo devuelva, el parser descarta el resultado. Haría falta confiar en el ID cuando viene del propio indexador.
- **Penalizan un indexador lento durante horas**, sin forma sencilla de quitar la penalización desde la interfaz.

### Prowlarr y el protocolo Torznab

- **No hay atributos estándar para pistas de audio, subtítulos ni idioma regional.** Torznab tiene `language`, pero casi ningún indexador lo rellena y no distingue variantes. Un atributo como `audiolanguages=spa-ES,eng` resolvería medio problema de este documento.
- **No hay atributo de "pack de temporada"** fiable: Sonarr lo deduce del nombre.

### Bazarr

- **Solo admite una instancia de Sonarr y una de Radarr.** Obliga a meter el anime en el mismo Sonarr que las series.
- Los proveedores sin cuenta para español son pocos y frágiles.

### Jellyfin

- **Un montaje sin eventos de cambio no se vigila.** Con FUSE hay que avisar desde fuera. Haría falta un modo de "sondeo" por biblioteca.
- **El idioma de audio preferido es por usuario, no por biblioteca.** Un "castellano para series, japonés para anime" sería natural.

### Servicios en la nube y sus puentes

- **El límite de peticiones es por clave y la clave es por cuenta.** Haría falta poder crear claves por aplicación, con su propio límite y permisos de solo lectura.
- **Los estados de error del puente no caducan solos.** Un fichero que falló durante un pico de 429 sigue fallando hasta reiniciar.
- **Hay telemetría activada por defecto** que publica qué añades.

## Lo que falta en el ecosistema de torrents

Aquí "torrents" incluye cualquier distribución legítima por BitTorrent: distribuciones de software libre, colecciones de dominio público, lanzamientos de cine independiente que se distribuyen así.

- **Nombres sin estándar.** Cada grupo y cada catálogo nombra a su manera. Sin título original, año e idioma en un formato predecible, todo lo demás es adivinar.
- **Metadatos fuera del torrent.** La información técnica (`mediainfo`) vive, si vive, en una página web. Un fichero de metadatos estándar dentro del torrent, firmado por quien lo publica, permitiría saber idioma y pistas antes de descargar.
- **Sin forma de verificar el origen.** Nada garantiza que un torrent con un nombre concreto contenga lo que dice ni que quien lo publica tenga derecho a hacerlo. Firmas de publicador y listas de editores verificados ayudarían a separar lo legítimo de lo que no.
- **Packs y episodios mezclados.** Un episodio suelto, una temporada y una serie completa se publican igual y se distinguen por el nombre.

---

Anterior: [Tropiezos](08-tropiezos.md) · Siguiente: [Otros idiomas](10-otros-idiomas.md) · Volver al [inicio](../README.md)
