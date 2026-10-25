# 0002. Una sola carpeta montada como `/data` en todos

**Estado:** aceptada

## Contexto

Las guías habituales montan en cada contenedor lo suyo: `/downloads` en el cliente, `/tv` en Sonarr, `/movies` en Radarr. Las rutas no coinciden entre apps y hacen falta "remote path mappings". Con enlaces simbólicos a un montaje FUSE es peor: un enlace absoluto solo resuelve si la ruta de destino existe igual en el contenedor que lo lee.

## Decisión

Un dataset propio, montado completo como `/data` en todos los contenedores, con `rshared` en el que crea el montaje FUSE y `rslave` en el resto.

## Alternativas descartadas

- **Montajes separados por app.** Más "mínimo privilegio", pero obliga a copiar en vez de mover y rompe los enlaces.
- **Rutas del host dentro de los contenedores.** Funciona, pero ata la configuración de cada app a la estructura de un servidor concreto.

## Consecuencias

- (+) Mover de descargas a biblioteca es instantáneo. Los enlaces resuelven igual en todas las apps.
- (+) Copiar o destruir el dataset es copiar o destruir el stack entero.
- (-) Todas las apps ven todo `/data`. Se acepta: comparten usuario y propósito.
- (-) Desde el host, los enlaces apuntan a rutas que no existen. Para depurar hay que entrar en un contenedor.
