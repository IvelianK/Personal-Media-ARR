# 0004. El anime en el mismo Sonarr, con su carpeta y su perfil

**Estado:** aceptada

## Contexto

El anime se quiere con audio japonés; el resto de series, en castellano. Lo habitual es un segundo Sonarr dedicado al anime.

## Decisión

Un solo Sonarr con dos carpetas raíz (`series` y `anime`) y dos perfiles ("Español" y "Anime"). Seerr manda el anime a su carpeta y perfil automáticamente. `langguard` decide el idioma exigido por la carpeta.

## Alternativas descartadas

- **Dos Sonarr.** Más aislado, pero Bazarr solo admite una instancia de Sonarr: el anime se quedaría sin gestión de subtítulos, que es justo lo que más necesita.

## Consecuencias

- (+) Un contenedor menos y un único sitio para configurar Sonarr.
- (+) Bazarr cubre series y anime.
- (-) Los formatos personalizados son comunes a los dos perfiles; solo cambian las puntuaciones. Un formato pensado para series puede afectar al anime si no se le pone 0 en ese perfil (pasó con "Solo latino").
