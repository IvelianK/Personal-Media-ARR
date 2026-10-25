import unittest

import langguard as L


class Verdict(unittest.TestCase):
    def test_castellano_rotulado(self):
        self.assertTrue(L.verdict([("spa", "Castellano"), ("eng", "")], "spa", ""))

    def test_pista_latina_no_cuenta(self):
        self.assertFalse(L.verdict([("spa", "Latino"), ("eng", "")], "spa", ""))

    def test_release_latina_con_pista_spa_sin_rotular(self):
        self.assertFalse(L.verdict([("eng", ""), ("spa", "DDP5.1")], "spa", "Pelicula.2021.1080p.ENG.ITA.And.ESP.LATINO"))

    def test_release_latina_con_pista_castellano_rotulada(self):
        self.assertTrue(L.verdict([("spa", "Castellano"), ("spa", "Latino")], "spa", "Pelicula.2021.1080p.ESP.LATINO"))

    def test_release_dual_con_marca_fuerte(self):
        self.assertTrue(L.verdict([("spa", "")], "spa", "Pelicula 2021 1080p Castellano-Latino ES-EN"))

    def test_sin_pista_del_idioma(self):
        self.assertFalse(L.verdict([("eng", "")], "spa", "Pelicula 2021 1080p Spanish"))

    def test_und_se_fia_del_nombre(self):
        self.assertTrue(L.verdict([("und", "")], "spa", "Pelicula 2021 1080p Castellano"))
        self.assertFalse(L.verdict([("und", "")], "spa", "Pelicula 2021 1080p Latino"))

    def test_anime_japones(self):
        self.assertTrue(L.verdict([("jpn", ""), ("eng", "")], "jpn", ""))
        self.assertFalse(L.verdict([("eng", "")], "jpn", ""))
        self.assertTrue(L.verdict([("und", "")], "jpn", "Serie - 01 Japanese 1080p"))
        self.assertFalse(L.verdict([("und", "")], "jpn", "Serie - 01 1080p"))
        self.assertFalse(L.verdict([("und", "")], "jpn", "Serie 01 English Dub"))

    def test_otros_idiomas(self):
        self.assertTrue(L.verdict([("ger", "Deutsch")], "deu", ""))
        self.assertTrue(L.verdict([("eng", "English")], "eng", ""))
        self.assertTrue(L.verdict([("fre", "VFF")], "fra", ""))
        self.assertFalse(L.verdict([("eng", "")], "fra", ""))


class Configuracion(unittest.TestCase):
    roots = L.parse_roots("/data/biblioteca/anime/=jpn, /data/biblioteca/peliculas-en/=eng")

    def test_parse_roots(self):
        self.assertEqual(self.roots, {"/data/biblioteca/anime/": "jpn", "/data/biblioteca/peliculas-en/": "eng"})

    def test_idioma_por_carpeta(self):
        self.assertEqual(L.lang_for_path("/data/biblioteca/anime/X/S01/e.mkv", self.roots, "spa"), "jpn")
        self.assertEqual(L.lang_for_path("/data/biblioteca/peliculas-en/X/x.mkv", self.roots, "spa"), "eng")
        self.assertEqual(L.lang_for_path("/data/biblioteca/series/X/e.mkv", self.roots, "spa"), "spa")

    def test_idioma_desconocido_no_arranca(self):
        with self.assertRaises(SystemExit):
            L.load_config({"LANG_DEFAULT": "rus", "WEBHOOK_AUTH": "test:clave"})
        with self.assertRaises(SystemExit):
            L.load_config({"LANG_BY_ROOT": "/data/x/=xxx", "WEBHOOK_AUTH": "test:clave"})

    def test_autenticacion_obligatoria(self):
        with self.assertRaises(SystemExit):
            L.load_config({})

    def test_valores_por_defecto(self):
        cfg = L.load_config({"WEBHOOK_AUTH": "test:clave"})
        self.assertEqual((cfg.default, cfg.interval, cfg.webhook_auth), ("spa", 600, "test:clave"))
        self.assertEqual(cfg.arrs["sonarr"].id_field, "seriesId")


class Rescate(unittest.TestCase):
    q = {"quality": {"id": 7}}

    def item(self, path, eps, series_id=3, rejections=()):
        return {"path": path, **self.q, "series": {"id": series_id},
                "episodes": [{"id": i, "hasFile": has} for i, has in eps],
                "rejections": [{"reason": r} for r in rejections]}

    def test_match_grab_por_palabras_completas(self):
        grabs = [{"sourceTitle": "Aliens 1986 1080p", "movieId": 1},
                 {"sourceTitle": "Alien 1979 1080p BluRay Castellano", "movieId": 2},
                 {"sourceTitle": "Alien 1979 1080p BluRay Castellano Extended Edition", "movieId": 3}]
        self.assertEqual(L.match_grab("Alien 1979 [1080p BluRay][Castellano]", grabs)["movieId"], 2)
        self.assertIsNone(L.match_grab("Alie", grabs))

    def test_match_grab_con_titulo_reescrito(self):
        carpeta = "Serie Temporada 6 [1080p][Castellano]"
        grabs = [{"sourceTitle": "Serie S06 1080p Serie Temporada 6 1080p Castellano [SPANISH]", "seriesId": 3}]
        self.assertEqual(L.match_grab(carpeta, grabs)["seriesId"], 3)

    def test_solo_rellena_huecos(self):
        items = [self.item("/d/e1.mkv", [(1, True)]), self.item("/d/e2.mkv", [(2, False)])]
        self.assertEqual([f["episodeIds"] for f in L.pick_episodes(items, 3, "HASH")], [[2]])

    def test_ignora_otra_serie_y_rechazos_duros(self):
        items = [self.item("/d/a.mkv", [(1, False)], series_id=9),
                 self.item("/d/b.mkv", [(2, False)], rejections=["Not an upgrade for existing episode file"]),
                 self.item("/d/c.mkv", [(3, False)], rejections=["Unable to determine if file is a sample"])]
        self.assertEqual([f["path"] for f in L.pick_episodes(items, 3, "HASH")], ["/d/c.mkv"])

    def test_pelicula_es_el_video_mas_grande(self):
        items = [{"path": "/d/extra.mkv", "size": 10, **self.q, "rejections": [{"reason": "Unknown Movie"}]},
                 {"path": "/d/peli.mkv", "size": 900, **self.q, "rejections": [{"reason": "Unknown Movie"}]}]
        self.assertEqual(L.pick_movie(items, 5, "HASH"), [{"path": "/d/peli.mkv", "quality": {"id": 7}, "languages": [],
                                                           "releaseGroup": "", "downloadId": "HASH", "movieId": 5}])
        self.assertEqual(L.pick_movie([], 5, "HASH"), [])

    def test_pelicula_de_otro_id_no_se_importa(self):
        items = [{"path": "/d/otra.mkv", "movie": {"id": 9}, "size": 900, **self.q},
                 {"path": "/d/correcta.mkv", "movie": {"id": 5}, "size": 100, **self.q}]
        self.assertEqual(L.pick_movie(items, 5, "HASH")[0]["path"], "/d/correcta.mkv")


if __name__ == "__main__":
    unittest.main()
