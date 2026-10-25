"""Verificador de idioma y rescate de importaciones para Sonarr y Radarr.

Webhook: Sonarr/Radarr lo llaman en cada importacion (On Import / On Upgrade). Lee las pistas de
audio con ffprobe y, si no esta el idioma exigido, borra el fichero, marca la release como fallida
(lista de bloqueo) y la app busca otra. En una mejora no borra: Sonarr ya quito el fichero anterior.

Rescate: cada RESCUE_INTERVAL segundos importa por API las carpetas de descargas que las apps no
importan solas (hash ya usado antes, nombres sin año). Solo rellena huecos: nunca sustituye un
fichero existente.

Configuracion por entorno: ver README.md.
"""
import base64
import hmac
import json
import logging
import os
import re
import subprocess
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import NamedTuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("langguard")


class Arr(NamedTuple):
    url: str
    key: str
    file_endpoint: str  # episodefile | moviefile
    id_field: str  # seriesId | movieId


class Lang(NamedTuple):
    codes: frozenset  # etiquetas de idioma de pista (ISO 639-1/2 y nombres)
    title: re.Pattern  # como se rotula la pista o se anuncia la release


# Idiomas soportados (ISO 639-2). Para anadir uno: entrada aqui y su prueba.
LANGS = {
    "spa": Lang(frozenset({"spa", "es", "esp", "spanish"}), re.compile(r"castellano|espa[nñ]ol|spanish|\bspa\b|\besp\b", re.I)),
    "eng": Lang(frozenset({"eng", "en", "english"}), re.compile(r"english|ingl[eé]s|\beng\b", re.I)),
    "fra": Lang(frozenset({"fra", "fre", "fr", "french"}), re.compile(r"fran[cç]ais|french|\bvf[fqi]?\b|\bfre\b", re.I)),
    "deu": Lang(frozenset({"deu", "ger", "de", "german"}), re.compile(r"deutsch|german|\bger\b", re.I)),
    "ita": Lang(frozenset({"ita", "it", "italian"}), re.compile(r"italiano|italian|\bita\b", re.I)),
    "por": Lang(frozenset({"por", "pt", "portuguese"}), re.compile(r"portugu[eê]s|portuguese|\bpor\b", re.I)),
    "jpn": Lang(frozenset({"jpn", "ja", "jp", "japanese"}), re.compile(r"japanese|japon[eé]s|\bjpn\b", re.I)),
}
# Variantes regionales que no cuentan: (marca de la variante no deseada, marca fuerte de la deseada).
# Castellano: ESP/SPA a secas tambien los usa el latino, asi que solo cuentan marcas fuertes.
VARIANTS = {
    "spa": (re.compile(r"latino|latam|latinoam|mexic|\blat\b", re.I),
            re.compile(r"castellano|\bcast\b|\bcas\b|\bes[-_]es\b|\[es[-\]]|spain|espa[nñ]a", re.I)),
}
# En anime con pistas sin etiquetar, el nombre de la release delata un doblaje
DUB = re.compile(r"\bdub(bed)?\b|doblad[oa]|doblaje", re.I)
# Rechazos de ManualImport que solo significan "no entiendo el nombre" o "ffprobe no pudo leer":
# con la serie o pelicula ya identificada por el historial se puede importar igual.
SOFT_REJECTION = re.compile(r"parse|sample|unknown movie|unknown series", re.I)
MAX_BODY = 1 << 20


def parse_roots(spec):
    """'/data/biblioteca/anime/=jpn,/data/biblioteca/peliculas-en/=eng' -> {ruta: idioma}."""
    pairs = (item.split("=", 1) for item in spec.split(",") if "=" in item)
    return {path.strip(): lang.strip() for path, lang in pairs}


def lang_for_path(path, roots, default):
    return next((lang for root, lang in roots.items() if path.startswith(root)), default)


def verdict(tracks, want, release_title):
    """True si alguna pista cumple. Si el idioma tiene una variante no deseada, descarta las pistas
    rotuladas con ella y, si la release se anuncia con esa variante sin marca fuerte de la deseada,
    exige una pista rotulada con la marca fuerte."""
    lang = LANGS[want]
    unwanted, strong = VARIANTS.get(want, (None, None))
    doubtful = unwanted and unwanted.search(release_title) and not strong.search(release_title)
    for code, title in tracks:
        if unwanted and unwanted.search(title):
            continue
        if doubtful and not strong.search(title):
            continue
        if code in lang.codes or lang.title.search(title):
            return True
    # Pistas sin etiquetar: se fia del nombre de la release
    if tracks and all(code in ("und", "") for code, _ in tracks):
        if want == "jpn":
            return bool(lang.title.search(release_title)) and not DUB.search(release_title)
        return bool(lang.title.search(release_title)) and not (unwanted and unwanted.search(release_title))
    return False


def audio_tracks(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index:stream_tags=language,title", "-of", "json", path],
        capture_output=True, text=True, timeout=120, check=True,
    ).stdout
    return [
        ((s.get("tags") or {}).get("language", "und").lower(), (s.get("tags") or {}).get("title", ""))
        for s in json.loads(out).get("streams", [])
    ]


def api(arr, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{arr.url}/api/v3/{path}", data=data, method=method,
                                 headers={"X-Api-Key": arr.key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
    return json.loads(raw) if raw else None


def mark_failed(name, arr, download_id):
    if not download_id:
        log.warning("%s: sin downloadId, no se puede marcar la release como fallida", name)
        return
    query = urllib.parse.urlencode({"downloadId": download_id, "eventType": 1, "pageSize": 1})
    records = api(arr, "GET", f"history?{query}")["records"]
    if records:
        api(arr, "POST", f"history/failed/{records[0]['id']}")
        log.info("%s: release %s marcada como fallida, se buscara otra", name, download_id)


def handle(name, arr, payload, cfg):
    event = payload.get("eventType")
    if event == "Test":
        log.info("%s: webhook de prueba recibido", name)
        return
    if event != "Download":
        return
    f = payload.get("episodeFile") or payload.get("movieFile") or {}
    path, file_id = f.get("path"), f.get("id")
    if not path or type(file_id) is not int or file_id <= 0:
        log.warning("%s: payload sin ruta o con id de fichero no valido", name)
        return
    release_title = (payload.get("release") or {}).get("releaseTitle") or f.get("sceneName") or f.get("relativePath", "")
    want = lang_for_path(path, cfg.roots, cfg.default)
    try:
        tracks = audio_tracks(path)
    except Exception as e:  # ffprobe falla: no se toca nada
        log.error("%s: ffprobe fallo en %s: %s", name, path, e)
        return
    ok = verdict(tracks, want, release_title)
    log.info("%s: %s | exige=%s | pistas=%s | %s", name, path, want, tracks, "OK" if ok else "RECHAZADO")
    if ok:
        return
    if payload.get("isUpgrade"):
        # La app ya borro el fichero anterior: borrar este dejaria el titulo sin ninguno
        log.warning("%s: mejora sin el idioma exigido; se conserva el fichero y se bloquea la release", name)
    else:
        api(arr, "DELETE", f"{arr.file_endpoint}/{file_id}")
    mark_failed(name, arr, payload.get("downloadId"))


def norm(text):
    """Palabras en minusculas: para casar el nombre de la carpeta con el titulo de la peticion."""
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def match_grab(folder_name, grabs):
    """La peticion cuyo titulo contiene el nombre de la carpeta como palabras completas. Si hay varias,
    la mas especifica (titulo mas corto): asi 'Alien' no casa con 'Aliens' ni gana a 'Alien 1979'."""
    key = norm(folder_name)
    hits = [g for g in grabs if key and f" {key} " in f" {norm(g['sourceTitle'])} "]
    return min(hits, key=lambda g: len(g["sourceTitle"]), default=None)


def importable(item):
    return all(SOFT_REJECTION.search(r.get("reason", "")) for r in item.get("rejections", []))


def file_entry(item, download_id):
    return {"path": item["path"], "quality": item["quality"], "languages": item.get("languages") or [],
            "releaseGroup": item.get("releaseGroup") or "", "downloadId": download_id}


def pick_episodes(items, series_id, download_id):
    """Solo huecos: sustituir un episodio existente borra el bueno antes de mover el nuevo."""
    return [{**file_entry(it, download_id), "seriesId": series_id, "episodeIds": [e["id"] for e in it["episodes"]]}
            for it in items
            if importable(it) and (it.get("series") or {}).get("id") == series_id
            and it.get("episodes") and not any(e.get("hasFile") for e in it["episodes"])]


def pick_movie(items, movie_id, download_id):
    """La pelicula es el video mas grande; el resto son extras."""
    candidates = [it for it in items if importable(it) and
                  (it.get("movie") or {}).get("id") in (None, movie_id)]
    if not candidates:
        return []
    return [{**file_entry(max(candidates, key=lambda it: it.get("size", 0)), download_id), "movieId": movie_id}]


def rescue(name, arr, downloads, done):
    """done: carpetas ya resueltas; no se vuelven a examinar (cada vista previa lee cabeceras)."""
    root = f"{downloads}/{name}"
    if not arr.key or not os.path.isdir(root):
        return
    grabs = api(arr, "GET", "history?eventType=1&pageSize=1000&sortKey=date&sortDirection=descending")["records"]
    for folder_name in os.listdir(root):
        folder = f"{root}/{folder_name}"
        if folder in done or not os.path.isdir(folder):
            continue
        grab = match_grab(folder_name, grabs)
        if not grab:
            continue
        target = grab[arr.id_field]
        if arr.id_field == "movieId" and api(arr, "GET", f"movie/{target}").get("hasFile"):
            done.add(folder)
            continue
        # Sin seriesId/movieId en la vista previa: con el ID, Sonarr devuelve una lista vacia
        items = api(arr, "GET", "manualimport?" + urllib.parse.urlencode({"folder": folder, "filterExistingFiles": "true"}))
        pick = pick_episodes if arr.id_field == "seriesId" else pick_movie
        files = pick(items, target, grab["downloadId"])
        if files:
            api(arr, "POST", "command", {"name": "ManualImport", "files": files, "importMode": "move"})
            log.info("%s: rescate de %d fichero(s) de %s", name, len(files), folder_name)
        done.add(folder)


class Config(NamedTuple):
    arrs: dict
    default: str
    roots: dict
    downloads: str
    interval: int
    webhook_auth: str  # "usuario:clave" para Basic auth


def load_config(env):
    cfg = Config(
        arrs={
            "sonarr": Arr(env.get("SONARR_URL", "http://sonarr:8989"), env.get("SONARR_API_KEY", ""), "episodefile", "seriesId"),
            "radarr": Arr(env.get("RADARR_URL", "http://radarr:7878"), env.get("RADARR_API_KEY", ""), "moviefile", "movieId"),
        },
        default=env.get("LANG_DEFAULT", "spa"),
        roots=parse_roots(env.get("LANG_BY_ROOT", "/data/biblioteca/anime/=jpn")),
        downloads=env.get("DOWNLOADS", "/data/descargas"),
        interval=int(env.get("RESCUE_INTERVAL", "600")),
        webhook_auth=env.get("WEBHOOK_AUTH", ""),
    )
    unknown = {cfg.default, *cfg.roots.values()} - LANGS.keys()
    if unknown:
        raise SystemExit(f"Idiomas no soportados: {sorted(unknown)}. Soportados: {sorted(LANGS)}")
    if ":" not in cfg.webhook_auth or not all(cfg.webhook_auth.split(":", 1)):
        raise SystemExit("WEBHOOK_AUTH requiere usuario:clave antes de arrancar")
    if cfg.interval < 0:
        raise SystemExit("RESCUE_INTERVAL no puede ser negativo")
    return cfg


def make_handler(cfg):
    expected = "Basic " + base64.b64encode(cfg.webhook_auth.encode()).decode()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            name = self.path.strip("/")
            if name not in cfg.arrs:
                self.send_error(404)
                return
            if not hmac.compare_digest(self.headers.get("Authorization", ""), expected):
                self.send_error(401)
                return
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                self.send_error(400)
                return
            if length <= 0 or length > MAX_BODY:
                self.send_error(413 if length > MAX_BODY else 400)
                return
            try:
                payload = json.loads(self.rfile.read(length))
            except ValueError:
                self.send_error(400)
                return
            if not isinstance(payload, dict):
                self.send_error(400)
                return
            # Responde ya: ffprobe y la API pueden tardar mas que el timeout del webhook
            self.send_response(200)
            self.send_header("Content-Length", "0")
            self.end_headers()
            threading.Thread(target=self.process, args=(name, payload), daemon=True).start()

        @staticmethod
        def process(name, payload):
            try:
                handle(name, cfg.arrs[name], payload, cfg)
            except Exception:
                log.exception("%s: error procesando webhook", name)

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args):
            pass

    return Handler


def rescue_loop(cfg):
    done = set()
    while True:
        time.sleep(cfg.interval)
        for name, arr in cfg.arrs.items():
            try:
                rescue(name, arr, cfg.downloads, done)
            except Exception:
                log.exception("%s: error en el rescate de importaciones", name)


if __name__ == "__main__":
    config = load_config(os.environ)
    if config.interval > 0:
        threading.Thread(target=rescue_loop, args=(config,), daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", 8080), make_handler(config)).serve_forever()
