# Política de seguridad

## Qué cubre

| Parte | Cubierta |
|---|---|
| Verificador de idioma (`tools/langguard/`) | Sí |
| Ejemplo de despliegue (`deploy/`) | Sí |
| Workflows de GitHub Actions (`.github/`) | Sí |
| Documentación (`docs/`, `README.md`) | Si recomienda una configuración insegura o expone un dato que no debería ser público |
| Sonarr, Radarr, Prowlarr, Bazarr, Jellyfin, Seerr y el resto de aplicaciones de terceros | No. Informa a su proyecto |

Solo se mantiene la última versión de la rama `main`.

## Cómo informar de una vulnerabilidad

No abras una issue pública. Usa el reporte privado de GitHub: pestaña **Security** del repositorio, **Report a vulnerability**.

Incluye qué parte está afectada, cómo reproducirlo y el impacto que ves. Recibirás respuesta en un plazo de 7 días y, si se confirma, una corrección o un plan para corregirlo en 30 días como máximo. Se te citará en la corrección si lo deseas.

## Contenido protegido

Este repositorio no aloja, enlaza ni indexa contenido protegido por derechos de autor. Si encuentras algo que lo haga, o una instrucción que facilite infringirlos, comunícalo por la misma vía y se retirará.

## Fuera de alcance

- Configuraciones que el propio usuario decida exponer a internet en contra de lo que recomienda [la guía de seguridad](docs/07-seguridad.md).
- Vulnerabilidades de las imágenes de terceros que referencia `deploy/compose.yaml`. Comunícalas al proyecto de origen y revisa sus avisos de seguridad antes de actualizar el ejemplo.
