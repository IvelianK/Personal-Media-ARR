# 0005. Solo fuentes legítimas, y la guía no nombra otras

**Estado:** aceptada

## Contexto

Buena parte de las guías de *arr en internet dan por hecho fuentes que distribuyen contenido sin licencia, o las insinúan. El software es neutro, pero una guía que enseña a conectarlo a esas fuentes facilita la infracción.

## Decisión

La guía solo describe fuentes legítimas: soportes propios, dominio público, licencias libres, archivos abiertos y servicios con licencia. No nombra, enlaza ni explica la configuración de trackers, agregadores o listas de fuentes de contenido sin licencia. Las piezas que dependen de una fuente concreta (como el normalizador Torznab) se documentan como diseño, sin código atado a ninguna.

## Alternativas descartadas

- **Documentarlo todo y añadir un aviso legal.** Un aviso no cambia lo que enseña la guía.
- **No tratar la descarga en absoluto.** Dejaría fuera la mitad del stack y lo más útil de lo aprendido.

## Consecuencias

- (+) La guía se puede compartir y enlazar sin problema.
- (+) Todo lo técnico (perfiles, idioma, verificación, plugins) es igual de útil con fuentes legales.
- (-) Quien busque "qué indexadores poner" no lo encontrará aquí.
