# -*- coding: utf-8 -*-
"""Denetleyicinin hissi, sayılarla.

`arac/dogrula.py` README'deki iki başlık sayısının hâlâ doğru olduğunu
kontrol ediyor. Bu dosya bir seviye aşağısına bakıyor: kojot penceresinin
gerçekten `kojot_suresi` kadar olduğunu, tamponun gerçekten `zipla_tampon_suresi`
kadar geriye baktığını, kesmenin tepeyi düşürdüğünü ve zeminin gerçekten zemin
olduğunu.

Neden ayrı: README sayısı değiştiğinde `dogrula.py` kırmızı olur ve doğrusu
budur — ama *hangi* davranışın bozulduğunu söylemez. Bu testler bunu söylüyor.
Hiçbir sayı burada sabitlenmiyor; hepsi `oyuncu.gd`'den okunan sabitlerden
türetiliyor, çünkü amaç sabitleri dondurmak değil, sabitlerle davranış
arasındaki ilişkiyi korumak.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parent.parent


def _yukle():
    yol = KOK / "arac" / "zipla-egrisi.py"
    spec = importlib.util.spec_from_file_location("zipla_egrisi", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


z = _yukle()


# --------------------------------------------------------------------------
# sabitler oyuncu.gd'den okunuyor mu
# --------------------------------------------------------------------------


def test_sabitler_gd_dosyasindan_okunuyor():
    """Bir sayı iki yerde yazıyorsa, biri er geç yanlış olur."""
    kaynak = (KOK / "yandan-gorunum" / "scripts" / "oyuncu.gd").read_text(encoding="utf-8")
    assert "zipla_gucu" in kaynak and str(int(z.ZIPLA_GUCU)) in kaynak
    assert "yercekimi" in kaynak and str(int(z.YERCEKIMI)) in kaynak
    assert str(z.KESME) in kaynak


def test_fizik_adimi_proje_ayarindan_geliyor():
    proje = (KOK / "yandan-gorunum" / "project.godot").read_text(encoding="utf-8")
    if "physics_ticks_per_second" in proje:
        assert ("physics_ticks_per_second=%d" % z.TICK) in proje.replace(" ", "")
    else:
        assert z.TICK == 60, "ayar yoksa Godot varsayilani 60 olmali"
    assert z.DT == pytest.approx(1.0 / z.TICK)


def test_sabitler_akla_yakin():
    assert z.ZIPLA_GUCU > 0 and z.YERCEKIMI > 0
    assert 0.0 < z.KESME < 1.0, "kesme carpani zıplamayı kısmalı, tersine çevirmemeli"
    assert z.KOJOT > 0 and z.TAMPON > 0


# --------------------------------------------------------------------------
# değişken zıplama yüksekliği
# --------------------------------------------------------------------------


def test_tusu_birakmak_tepeyi_dusurur():
    tam = z.kos(0.72, bas_t=0.0)
    erken = z.kos(0.72, bas_t=0.0, birak_t=0.10)
    assert erken["tepe"] < tam["tepe"]


def test_ne_kadar_erken_birakilirsa_o_kadar_alcak():
    tepeler = [z.kos(0.72, bas_t=0.0, birak_t=t)["tepe"] for t in (0.04, 0.08, 0.12)]
    assert tepeler == sorted(tepeler), "daha gec birakmak daha alcak ziplama uretmemeli"


def test_tepeden_sonra_birakmak_hicbir_sey_degistirmez():
    """Kesme yalnızca yükselirken uygulanır; düşerken basılmayan tuş hız katmaz."""
    tam = z.kos(0.9, bas_t=0.0)
    gec = z.kos(0.9, bas_t=0.0, birak_t=0.60)
    assert gec["tepe"] == pytest.approx(tam["tepe"])


def test_tepe_teorik_degere_yakin_ama_ayrik_entegrasyon_yuzunden_ustunde():
    teorik = z.ZIPLA_GUCU ** 2 / (2 * z.YERCEKIMI)
    tam = z.kos(0.72, bas_t=0.0)["tepe"]
    assert tam > teorik, "ayrik adimlarla integre edilen ziplama teorikten alcak olamaz"
    assert tam - teorik < 0.1 * teorik, "fark bir fizik adimi mertebesinde kalmali"


def test_hic_basilmazsa_ziplamaz():
    r = z.kos(0.5)
    assert r["zipladi"] is None
    assert r["tepe"] == pytest.approx(0.0, abs=1e-6)


# --------------------------------------------------------------------------
# kojot süresi
# --------------------------------------------------------------------------


def test_kojot_penceresi_icinde_basmak_ziplatir():
    gecikme = z.KOJOT * 0.5
    r = z.kos(0.72, zemin_biter=0.10, bas_t=0.10 + gecikme)
    assert r["zipladi"] is not None


def test_kojot_penceresinden_sonra_basmak_ziplatmaz():
    gecikme = z.KOJOT * 2.0
    r = z.kos(0.72, zemin_biter=0.10, bas_t=0.10 + gecikme)
    assert r["zipladi"] is None


def test_kojot_penceresi_gd_dosyasindaki_sure_kadar():
    """Sınır tam `kojot_suresi`'nde olmalı, bir fizik adımı toleransıyla."""
    icerde = z.kos(0.72, zemin_biter=0.10, bas_t=0.10 + z.KOJOT - z.DT * 2)
    disarda = z.kos(0.72, zemin_biter=0.10, bas_t=0.10 + z.KOJOT + z.DT * 3)
    assert icerde["zipladi"] is not None, "pencerenin icinde ziplamali"
    assert disarda["zipladi"] is None, "pencerenin disinda ziplamamali"


def test_kenardan_dusen_oyuncu_ziplamadan_da_asagi_gider():
    r = z.kos(0.5, zemin_biter=0.10)
    son_y = r["iz"][-1][1]
    assert son_y < 0.0, "zemin bittikten sonra oyuncu duseyi terk etmeli"


# --------------------------------------------------------------------------
# zıplama tamponu
# --------------------------------------------------------------------------


def _inis_ani():
    return z.kos(0.72, y0=45.0)["kondu"]


def test_inise_yakin_basilan_tus_yutulmaz():
    inis = _inis_ani()
    r = z.kos(0.72, y0=45.0, bas_t=inis - z.TAMPON * 0.5)
    assert r["zipladi"] is not None
    assert r["zipladi"] >= inis - z.DT, "ziplama inisten once olmamali"


def test_cok_erken_basilan_tus_yutulur():
    inis = _inis_ani()
    r = z.kos(0.72, y0=45.0, bas_t=inis - z.TAMPON * 2.5)
    assert r["zipladi"] is None


def test_tampon_penceresi_gd_dosyasindaki_sure_kadar():
    inis = _inis_ani()
    icerde = z.kos(0.72, y0=45.0, bas_t=inis - (z.TAMPON - z.DT * 2))
    disarda = z.kos(0.72, y0=45.0, bas_t=inis - (z.TAMPON + z.DT * 4))
    assert icerde["zipladi"] is not None
    assert disarda["zipladi"] is None


def test_yuksekten_dusus_gercekten_zemine_iniyor():
    r = z.kos(1.2, y0=45.0)
    assert r["kondu"] is not None
    assert r["iz"][-1][1] == pytest.approx(0.0, abs=1e-6)


# --------------------------------------------------------------------------
# simülasyonun kendisi
# --------------------------------------------------------------------------


def test_iz_her_fizik_adiminda_bir_ornek_tutuyor():
    sure = 0.5
    r = z.kos(sure)
    assert len(r["iz"]) == pytest.approx(sure / z.DT + 1, abs=2)
    assert r["iz"][0][0] == 0.0


def test_zeminde_duran_oyuncu_zeminin_altina_gecmiyor():
    r = z.kos(1.0)
    assert all(y >= -1e-9 for _, y in r["iz"])


def test_ziplama_sonrasi_geri_iner():
    r = z.kos(1.5, bas_t=0.0)
    assert r["iz"][-1][1] == pytest.approx(0.0, abs=1e-6)


def test_ayni_girdi_ayni_cikti():
    a = z.kos(0.72, bas_t=0.0, birak_t=0.1)
    b = z.kos(0.72, bas_t=0.0, birak_t=0.1)
    assert a["iz"] == b["iz"]


# --------------------------------------------------------------------------
# README ile bağ
# --------------------------------------------------------------------------


def test_dogrula_betigi_hala_gecerli():
    """README'deki sayılar simülasyonla uyuşuyor mu - `arac/dogrula.py`'nin işi."""
    import subprocess

    p = subprocess.run([sys.executable, str(KOK / "arac" / "dogrula.py")],
                       capture_output=True, text=True, cwd=str(KOK))
    assert p.returncode == 0, (p.stdout or "") + (p.stderr or "")
