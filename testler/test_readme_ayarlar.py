# -*- coding: utf-8 -*-
"""README'deki ayar tabloları `oyuncu.gd` ile aynı mı?

Şablonu kullanan kişi Inspector'da ne bulacağını README'den öğreniyor. Bir
`@export` eklendiğinde, silindiğinde ya da varsayılanı değiştiğinde tablo
sessizce yanlış kalmamalı.
"""

import re
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parent.parent
README = (KOK / "README.md").read_text(encoding="utf-8")

EXPORT = re.compile(r"^@export\s+var\s+(\w+)\s*:\s*float\s*=\s*([0-9.]+)", re.M)
SATIR = re.compile(r"^\|\s*`(\w+)`\s*\|\s*([0-9.]+)\s*\|", re.M)


def _tablo(ad):
    m = re.search(rf"<!-- ayarlar:{ad} -->(.*?)<!-- /ayarlar:{ad} -->", README, re.S)
    assert m, f"README'de <!-- ayarlar:{ad} --> blogu yok"
    return {k: float(v) for k, v in SATIR.findall(m.group(1))}


def _gd(proje):
    kaynak = (KOK / proje / "scripts" / "oyuncu.gd").read_text(encoding="utf-8")
    return {k: float(v) for k, v in EXPORT.findall(kaynak)}


@pytest.mark.parametrize("ad, proje", [("yandan", "yandan-gorunum"),
                                       ("ustten", "ustten-gorunum")])
def test_readme_ayar_tablosu_oyuncu_gd_ile_ayni(ad, proje):
    tablo, gd = _tablo(ad), _gd(proje)
    assert gd, f"{proje}/scripts/oyuncu.gd icinde @export float bulunamadi"
    assert tablo == gd, (
        f"README tablosu ({ad}) ile oyuncu.gd ayrismis:\n"
        f"  yalniz README'de : {sorted(set(tablo) - set(gd))}\n"
        f"  yalniz oyuncu.gd : {sorted(set(gd) - set(tablo))}\n"
        f"  farkli deger     : {sorted(k for k in set(gd) & set(tablo) if gd[k] != tablo[k])}"
    )
