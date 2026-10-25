# 8. Tropiezos

Formato de postmortem sin culpables: qué pasó, por qué, qué hice y qué me llevo. Ninguno costó datos que no se pudieran recuperar. Ordenados por lo que más enseñaron, no por fecha.

| # | Tropiezo | Dónde | Tipo |
|---|---|---|---|
| 1 | [La pista "spa" que era latina](#la-pista-spa-que-era-latina) | Radarr | Idioma |
| 2 | [El pack que Sonarr daba por importado](#el-pack-que-sonarr-daba-por-importado) | Sonarr | Importación |
| 3 | [El rescate que borró lo que iba a rescatar](#el-rescate-que-borró-lo-que-iba-a-rescatar) | langguard | Importación |
| 4 | [El límite de peticiones compartido](#el-límite-de-peticiones-compartido) | Servicio en la nube | API |
| 5 | [El proceso que no se dejaba matar](#el-proceso-que-no-se-dejaba-matar) | Puente FUSE | Contenedores |
| 6 | [Nombres que nadie entendía](#nombres-que-nadie-entendía) | Radarr | Parseo |
| 7 | [El cable de 100 Mb/s](#el-cable-de-100-mbs) | Red | Hardware |
| 8 | [La caché que empujaba al swap](#la-caché-que-empujaba-al-swap) | ZFS | Memoria |
| 9 | [Otros más pequeños](#otros-más-pequeños) | Varios | Varios |

---

## La pista "spa" que era latina

**Qué pasó.** La primera película que llegó traía una pista `spa` y pasó todos los filtros. Su nombre seguía el patrón `Pelicula.Año.1080p.ENG.ITA.And.ESP.LATINO` (nombre ficticio, mismo patrón).

**Por qué.** El formato "Castellano" aceptaba `ESP` y "Solo latino" solo restaba si no había ninguna marca de español. `ESP` contaba como marca, así que se anulaban. Y el verificador solo comprobaba que hubiera una pista `spa`, sin mirar de dónde.

**Qué hice.** Separé las marcas débiles (`ESP`, `SPA`, `Spanish`) de las fuertes (`Castellano`, `ES-ES`, `España`). "Solo latino" ahora exige que no haya ninguna fuerte. El verificador, si el nombre dice latino sin marca fuerte, solo acepta una pista rotulada como castellano. Reenvié el webhook a mano con esa importación: la rechazó, la bloqueó y Radarr buscó otra.

**Qué me llevo.** "Spanish" no es un idioma, son dos. Cualquier regla que no lo separe falla en silencio.

---

## El pack que Sonarr daba por importado

**Qué pasó.** Una serie de 73 episodios se quedó en 2. Sonarr había pedido los packs de temporada, la nube los tenía listos y nadie los importaba.

**Por qué.** Cada pack se había pedido antes para un solo episodio. Sonarr apunta el hash como importado. Al volver a pedirlo para el resto, lo da por importado al instante; el cliente, con "Remove Completed" activado, borraba la carpeta en ese mismo momento.

**Qué hice.** Desactivé "Remove Completed" (con enlaces simbólicos no ocupa nada) y añadí el rescate a `langguard`: periódicamente importa por API las carpetas que nadie ha importado, asignando la serie a partir del historial. Además, el normalizador pasó a anunciar los packs como temporada (`S01`) y no como episodio, para que se importen enteros a la primera.

**Qué me llevo.** Un estado "importado" basado en el hash y no en los ficheros es una mentira esperando su momento.

---

## El rescate que borró lo que iba a rescatar

**Qué pasó.** La primera ejecución del rescate dejó la serie en 0 de 73: borró los dos episodios que sí había.

**Por qué.** Encontró un pack que contenía esos dos episodios con mejor calidad y Sonarr lo trató como una mejora: borró el fichero existente y luego intentó mover el nuevo. El nuevo no se pudo mover porque el cliente ya había limpiado la carpeta. Resultado: ni el viejo ni el nuevo.

**Qué hice.** El rescate ahora solo rellena huecos: descarta cualquier fichero cuyo episodio ya tenga uno. Los dos episodios volvieron con la siguiente búsqueda. Eran enlaces, no ficheros: no se perdió nada en el almacenamiento.

**Qué me llevo.** Automatizar una importación es automatizar un borrado. Lo primero que hay que preguntarse es qué se puede sobrescribir.

---

## El límite de peticiones compartido

**Qué pasó.** Lecturas a 540 kB/s, algunos ficheros con `I/O error` inmediato, y la API del servicio en la nube devolviendo HTTP 429.

**Por qué.** El plan permitía 100 peticiones por minuto por clave. El puente "precalentaba" cada fichero al añadir un pack (73 episodios, 73 peticiones), Sonarr lanzaba `ffprobe` sobre cada uno, y la misma clave la usaba un reproductor en el móvil. Los ficheros que fallaron durante el pico quedaron marcados como error dentro del puente y siguieron fallando después, aunque el servicio los servía perfectamente (comprobado pidiendo el enlace directo: 9 MB/s).

**Qué hice.** `skip_pre_cache: true`, `rate_limit` del puente a 60 por minuto y reinicio del puente para limpiar su estado. Cero errores desde entonces.

**Qué me llevo.** Un límite "por clave" es un límite por persona. Hay que repartirlo entre todo lo que usa esa clave, no solo el stack.

---

## El proceso que no se dejaba matar

**Qué pasó.** `docker restart` del puente devolvió "container ... is zombie and can not be killed".

**Por qué.** El proceso principal murió, pero varios hilos se quedaron bloqueados dentro del montaje FUSE, esperando lecturas que no iban a llegar. Sin un `init`, nadie recoge esos procesos.

**Qué hice.** Aborté la conexión FUSE escribiendo `1` en `/sys/fs/fuse/connections/<id>/abort`, desmonté en diferido con `umount -l` y recreé el contenedor con `init: true`. Un detalle que costó un terminal colgado: el `<id>` hay que sacarlo de `/proc/self/mountinfo`. `mountpoint -d` hace `stat` sobre el montaje bloqueado y se queda esperando para siempre.

**Qué me llevo.** Cualquier contenedor que monte FUSE lleva `init: true`. Y ante un montaje colgado, nada que haga `stat` sobre él.

---

## Nombres que nadie entendía

**Qué pasó.** Radarr rechazaba como "Unable to parse release" justo las releases en castellano, que eran las que se buscaban.

**Por qué.** Venían con el título traducido y sin año, del tipo `El Gran Clásico [1080p][Castellano]`. El parser de Radarr necesita título y año para casar con la película.

**Qué hice.** Un normalizador Torznab entre la fuente y Prowlarr. Como la búsqueda llega por IMDb ID, sabe de qué título se trata y antepone `Título original Año` al nombre ([arquitectura](02-arquitectura.md#el-normalizador-torznab)). Para ficheros ya descargados con nombres así, el rescate importa indicando la película por ID.

**Qué me llevo.** Las *arr están hechas para nombres de escena en inglés. Para cualquier otro mundo hace falta traducir antes de que lleguen.

---

## El cable de 100 Mb/s

**Qué pasó.** El servidor bajaba de internet a 8,5 MB/s y el PC de al lado, en la misma red, a 44 MB/s.

**Por qué.** `ethtool` lo dejó claro: la tarjeta soporta y anuncia 1 Gb/s, pero el enlace negociaba 100 Mb/s. El otro extremo no ofrecía gigabit: cable con pares dañados o de categoría vieja, o un puerto de 100 Mb.

**Qué hice.** Nada en remoto: forzar una renegociación por SSH puede dejar la máquina sin red. Queda documentado y pendiente de cambiar cable o puerto.

**Qué me llevo.** Antes de culpar al software de una lectura lenta, `ethtool <interfaz> | grep Speed`.

---

## La caché que empujaba al swap

**Qué pasó.** 790 MB libres de 31 GB, 2,5 GB en swap y aplicaciones lentas.

**Por qué.** La caché ARC de ZFS tenía permitido crecer hasta 29,5 GB y llegó a 17. Es caché y se libera bajo presión, pero no lo bastante rápido: el kernel prefería mandar aplicaciones al swap.

**Qué hice.** Limitar la ARC a 12 GB con un script de arranque de TrueNAS que escribe en `/sys/module/zfs/parameters/zfs_arc_max`.

Y un error mío al explicarlo: recomendé `swapoff -a && swapon -a` para vaciar el swap. En ese servidor el swap es un zvol que activa un script de arranque, no `/etc/fstab`, así que `swapon -a` no lo volvió a montar. Se quedó sin swap hasta reactivarlo con `swapon /dev/zvol/boot-pool/swap`.

**Qué me llevo.** Antes de dar un comando genérico de sistema, mirar cómo está montado ese sistema en concreto.

---

## Otros más pequeños

| Síntoma | Causa | Arreglo |
|---|---|---|
| Un servicio externo solo era inalcanzable desde el servidor, no desde el PC | Bloqueos de rangos de IP de un CDN por parte del proveedor de internet, en franjas concretas. El servidor resolvía a una IP bloqueada; el PC, con otro DNS, a otra que no lo estaba | Diagnosticar con `curl -v` y comparar IP resueltas. El problema no es del stack |
| Peticiones HTTP colgadas desde ciertos contenedores | Recibían registros AAAA sin tener IPv6 | `sysctls: net.ipv6.conf.all.disable_ipv6: 1` |
| `Permission denied` al arrancar el puente | Arrancaba con su UID por defecto (1000) | `PUID` y `PGID` en su entorno |
| Sonarr dejó de usar el indexador durante horas | Las búsquedas tardaban más de 90 s y lo penalizó | Tiempos de espera cortos en el indexador; borrar y resincronizar desde Prowlarr para quitar la penalización |
| El anime daba 0 resultados con el indexador funcionando | Sonarr busca anime solo en la categoría 5070 y los resultados venían en 5000 | Etiquetar las series con ambas categorías |
| Releases de anime válidas rechazadas | "Solo latino" penalizaba etiquetas que en anime se refieren a subtítulos | Quitar ese formato del perfil de anime |
| Packs de temporada rechazados por tamaño | Mínimos de las definiciones de calidad | Mínimo a 0 con descarga en la nube |
| Imagen propia que no arrancaba (`Permission denied` al leer el script) | El fichero llegó con permisos `600` y `COPY --chmod` quitó también el bit de ejecución al directorio | `RUN chmod 755 /app && chmod 644 /app/*.py` |

---

Anterior: [Seguridad](07-seguridad.md) · Siguiente: [Lo que falta](09-lo-que-falta.md) · Volver al [inicio](../README.md)
