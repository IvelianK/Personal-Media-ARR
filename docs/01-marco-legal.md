# 1. Marco legal

Este documento no es asesoramiento jurídico. Resume el criterio que sigue la guía y te indica qué preguntarte antes de añadir una fuente. Si tienes dudas sobre tu caso, consulta a un profesional de tu país.

## La regla

**El software es legal. Lo que decide si tu uso lo es son las fuentes.** Sonarr, Radarr, Prowlarr y Jellyfin son herramientas de gestión, igual que un gestor de descargas o un reproductor. Ninguna trae contenido. Toda la responsabilidad está en qué indexadores y qué servicios les conectas.

## Fuentes que sí

| Fuente | Ejemplos | Notas |
|---|---|---|
| Tus propios soportes | DVD, Blu-ray y CD que has comprado | La compra no autoriza cualquier copia. En España, comprueba los requisitos de la [copia privada (art. 31.2 LPI)](https://www.boe.es/buscar/act.php?id=BOE-A-1996-8930#a31) y las reglas sobre [medidas tecnológicas (art. 160 LPI)](https://www.boe.es/buscar/act.php?id=BOE-A-1996-8930#a160). Usa solo métodos permitidos en tu caso |
| Dominio público | Cine clásico cuyos derechos han expirado, noticiarios históricos | Los plazos cambian por país. En la UE, por regla general, 70 años tras la muerte del último autor relevante |
| Licencias libres | Películas abiertas de la Blender Foundation, obras con licencia Creative Commons | Respeta la atribución y las condiciones de la licencia |
| Bibliotecas y archivos abiertos | Internet Archive (colecciones de dominio público), filmotecas con acceso abierto | Solo las colecciones marcadas como de libre uso |
| Contenido propio | Vídeos familiares, grabaciones propias | Ideal para Jellyfin, aunque no pase por Sonarr ni Radarr |
| Servicios con licencia | Tiendas que venden descargas sin DRM | Consulta la licencia de compra: debe permitir guardar y usar el fichero de la forma prevista |

## Fuentes que no

- Trackers, webs de enlaces y agregadores que distribuyen películas y series sin licencia de sus titulares.
- Listas compartidas de "fuentes" o configuraciones de terceros cuyo contenido no puedes verificar.
- Saltarse geobloqueos, DRM o bloqueos judiciales para acceder a contenido.

Esta guía no nombra ninguna fuente de ese tipo ni explica cómo configurarla.

## Los servicios en la nube ("debrid") y los indexadores públicos

Un servicio que descarga por ti y te deja leer el resultado es una herramienta neutra, como un servidor alquilado. El problema aparece por lo que le pides que descargue. Si lo usas, que sea para contenido que podrías descargar legalmente en casa.

Lo mismo vale para los indexadores públicos de torrents: muchos indexan de todo. Si lo usas para distribuciones de software libre o colecciones abiertas, bien; si filtra contenido protegido a tu biblioteca, el problema es tuyo, no de la herramienta.

> Ojo con un efecto colateral: compartir por torrent significa **subir** lo que descargas. En muchos países la infracción no es solo descargar, sino poner a disposición de otros. Con un cliente local, revisa la proporción de subida y qué compartes.

## Preguntas antes de añadir una fuente

1. ¿Sé quién es el titular de los derechos de lo que voy a obtener?
2. ¿Tengo una licencia, una compra o una excepción legal que me lo permita?
3. ¿La fuente distribuye lo mismo de forma legítima, o es casualidad que tenga algo legal?
4. ¿Voy a compartir (subir) ese contenido con terceros?

Si alguna respuesta es "no lo sé", no la añadas.

## Qué no cambia si eres estricto

Todo lo que cuenta esta guía funciona igual con fuentes legales: los perfiles, el verificador de idioma, los subtítulos, Jellyfin, Seerr y los plugins. Lo único que cambia es la lista de indexadores. Con tus propios discos, de hecho, ni siquiera hace falta un indexador: ripeas, dejas el fichero en una carpeta de importación y Radarr o Sonarr lo ordenan.

---

Anterior: [El stack](00-el-stack.md) · Siguiente: [Arquitectura](02-arquitectura.md) · Volver al [inicio](../README.md)
