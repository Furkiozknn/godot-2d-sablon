# -*- coding: utf-8 -*-
"""Duraklatma menüsü ve tuş atama modülü, Godot olmadan bakılabilen kısmı.

Davranışın kendisi `arac/girdi-ayarlari-testi.gd` ile gerçek Godot'ta
sınanıyor. Bu dosya iki projenin aynı modülü taşıdığını ve kayıtlı
olduğunu koruyor: biri düzeltilip öbürü unutulursa CI kırmızı yanar.
"""

import re
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parent.parent
PROJELER = ["yandan-gorunum", "ustten-gorunum"]
MODUL = ["scripts/girdi_ayarlari.gd", "scripts/duraklat.gd", "scenes/duraklat.tscn"]


def _oku(yol):
    return (KOK / yol).read_text(encoding="utf-8")


@pytest.mark.parametrize("dosya", MODUL)
def test_iki_proje_ayni_modulu_tasiyor(dosya):
    assert _oku(f"yandan-gorunum/{dosya}") == _oku(f"ustten-gorunum/{dosya}")


@pytest.mark.parametrize("proje", PROJELER)
def test_modul_autoload_olarak_kayitli(proje):
    ayar = _oku(f"{proje}/project.godot")
    bolum = re.search(r"^\[autoload\]\n(.*?)(?=^\[|\Z)", ayar, re.S | re.M)
    assert bolum, f"{proje}/project.godot icinde [autoload] yok"
    kayit = dict(re.findall(r'^(\w+)="\*res://([^"]+)"', bolum.group(1), re.M))
    assert kayit.get("GirdiAyarlari") == "scripts/girdi_ayarlari.gd"
    assert kayit.get("Duraklat") == "scenes/duraklat.tscn"
    for yol in kayit.values():
        assert (KOK / proje / yol).is_file(), yol


@pytest.mark.parametrize("proje", PROJELER)
def test_her_eylemin_menude_bir_adi_var(proje):
    ayar = _oku(f"{proje}/project.godot")
    girdi = re.search(r"^\[input\]\n(.*?)(?=^\[|\Z)", ayar, re.S | re.M).group(1)
    eylemler = re.findall(r"^(\w+)=\{", girdi, re.M)
    etiketler = set(re.findall(r'&"(\w+)":', _oku(f"{proje}/scripts/duraklat.gd")))
    assert eylemler, "project.godot'ta eylem bulunamadi"
    assert set(eylemler) <= etiketler, sorted(set(eylemler) - etiketler)


def test_kayit_proje_disina_yazmiyor():
    """Oyuncunun tuşları user:// altına gider, proje klasörüne değil."""
    kaynak = _oku("yandan-gorunum/scripts/girdi_ayarlari.gd")
    assert 'const DOSYA := "user://girdi.cfg"' in kaynak
    assert "res://" not in kaynak.split("const DOSYA")[1].split("\n")[0]


def test_godot_testi_readme_de_anlatiliyor():
    readme = _oku("README.md")
    assert (KOK / "arac" / "girdi-ayarlari-testi.gd").is_file()
    assert "arac/girdi-ayarlari-testi.gd" in readme
