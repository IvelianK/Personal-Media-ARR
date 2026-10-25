# 0007. El rescate de importaciones solo rellena huecos

**Estado:** aceptada, sustituye a una primera versión que podía sustituir ficheros

## Contexto

Sonarr da por importado un hash que ya usó y Radarr no sabe interpretar nombres sin año. Quedaban descargas completas sin importar. `langguard` incorporó un rescate que las importa por API. La primera versión aceptaba cualquier fichero que Sonarr considerara una mejora; en una de ellas Sonarr borró el episodio existente, no pudo mover el nuevo y dejó dos episodios sin fichero.

## Decisión

El rescate descarta cualquier fichero cuyo episodio ya tenga uno, y en Radarr no actúa si la película ya tiene fichero. Las mejoras de calidad las decide Sonarr o Radarr por su cuenta, nunca el rescate.

## Alternativas descartadas

- **Confiar en la decisión de Sonarr.** Es la que borró los ficheros.
- **Mover a un temporal antes de importar.** Más seguro para mejoras, pero añade complejidad para un caso que no hace falta cubrir.

## Consecuencias

- (+) El rescate no puede empeorar la biblioteca: como mucho, no hace nada.
- (-) Una mejora que solo esté en una descarga atascada no se aplica sola.
