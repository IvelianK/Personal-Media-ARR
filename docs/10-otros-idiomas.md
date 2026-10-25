# 10. Otros idiomas

Todo lo anterior está pensado para castellano. Cambiar de idioma toca cinco sitios. El resto del stack no cambia.

| Dónde | Qué cambiar |
|---|---|
| Formatos personalizados | Las expresiones regulares de idioma |
| Perfiles | Qué formato suma y cuál resta |
| `langguard` | `LANG_DEFAULT` y, si aplica, `LANG_BY_ROOT` |
| Bazarr | El idioma del perfil de subtítulos |
| Jellyfin y Seerr | Idioma de metadatos, país, audio y subtítulos preferidos |

Códigos que usa cada sitio: `ffprobe` y `langguard` usan **ISO 639-2** de tres letras (`eng`, `fra`, `deu`, `ita`, `por`, `jpn`). Bazarr y Jellyfin usan sobre todo **ISO 639-1** de dos (`en`, `fr`, `de`). Las variantes regionales (`pt-BR`, `fr-CA`) solo existen en Jellyfin y en algunos proveedores de subtítulos.

## Inglés

El caso más fácil: casi todo el contenido nace en inglés y los nombres de escena lo asumen.

- **Formatos personalizados.** No hace falta uno de "inglés": las guías de [TRaSH](https://trash-guides.info/) ya traen "Language: Not English" con puntuación negativa. Se aplican con [Recyclarr](https://github.com/recyclarr/recyclarr) o [Profilarr](https://github.com/Dictionarry-Hub/profilarr).
- **Perfiles.** Los de TRaSH (WEB-1080p, WEB-2160p) tal cual. Puntuación mínima 0.
- **`langguard`.** `LANG_DEFAULT=eng`. Para anime en japonés con subtítulos en inglés, deja `LANG_BY_ROOT=/data/biblioteca/anime/=jpn`.
- **Bazarr.** Perfil `en`. OpenSubtitles.com y Addic7ed (vía `gestdown`) cubren casi todo.
- **Jellyfin y Seerr.** Idioma `en`, país `US` o `GB` según quieras los títulos de un lado u otro.

Lo único que hay que vigilar: releases "MULTi" (varias pistas) que el parser marca con el idioma de la primera. `langguard` lo resuelve mirando todas.

## Francés, alemán, italiano y otros con escena propia

Estos idiomas tienen grupos y etiquetas propios (`VFF`, `VFQ`, `TRUEFRENCH`, `GERMAN`, `DL`, `iTA`). TRaSH tiene perfiles específicos para francés y alemán.

- **Formatos.** Parte de los de TRaSH para tu idioma. Si no los hay, copia la estructura del [documento de idioma](05-idioma.md): un formato que suma con las marcas del idioma, otro que resta la variante que no quieres.
- **Variantes regionales.** Francés de Francia (`VFF`) frente a Quebec (`VFQ`), portugués de Portugal frente a Brasil: mismo problema que castellano y latino. Separa marcas fuertes de débiles y haz que "Solo <variante>" reste salvo que haya una marca fuerte de la que quieres.
- **`langguard`.** `LANG_DEFAULT=fra` (o `deu`, `ita`, `por`). Las variantes regionales solo se distinguen para el castellano; para otra, añade sus patrones a `VARIANTS` en `langguard.py`, con una prueba en `test_langguard.py`.

## Plantilla para cualquier idioma

1. **Recoge cómo se nombra.** Busca diez o veinte releases legítimas en tu idioma y anota cómo aparece: palabra completa (`Deutsch`), abreviatura (`GER`), código (`de`), bandera, variante regional.
2. **Formato "<Idioma>".** Expresión regular con esas marcas, con `\b` para no casar dentro de otras palabras (`\bger\b`, no `ger`).
3. **Formato "Solo <variante>"** si tu idioma tiene variantes que no quieres.
4. **Perfil.** +1000 al formato del idioma, -10000 a la variante no deseada, puntuación mínima 1000 si quieres que sea obligatorio o 0 si solo preferente.
5. **`langguard`.** `LANG_DEFAULT` con el código ISO 639-2. Si tu idioma no está en `LANGS`, añádelo con su prueba.
6. **Bazarr.** Activa el idioma y crea un perfil solo con él.
7. **Jellyfin.** Idioma de metadatos y país en cada biblioteca; audio y subtítulos preferidos en cada usuario.
8. **Seerr.** Idioma y región en **Settings → General**, para que los títulos salgan como en tu país.

## Varios idiomas a la vez

Por ejemplo, una casa donde se ve en castellano y en inglés:

- Un perfil por idioma en Sonarr y Radarr ("Español", "Inglés"). Seerr permite elegir perfil al pedir.
- Carpetas raíz separadas (`peliculas-es`, `peliculas-en`) si quieres bibliotecas separadas en Jellyfin.
- En `langguard`, una entrada por carpeta raíz: `LANG_BY_ROOT=/data/biblioteca/anime/=jpn,/data/biblioteca/peliculas-en/=eng`. La ruta decide qué idioma se exige.
- Releases duales (`Dual`, `MULTi` con las dos pistas) puntúan en los dos perfiles; dales un extra si las prefieres.

---

Anterior: [Lo que falta](09-lo-que-falta.md) · Siguiente: [Registro de decisiones](decisiones/README.md) · Volver al [inicio](../README.md)
