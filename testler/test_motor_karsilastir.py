# -*- coding: utf-8 -*-
"""`arac/motor-karsilastir.py`'nin kendisi doğru karar veriyor mu?

Motor ölçümü CI'da gerçek Godot ile koşuyor; burada Godot yok. Bu testler
karşılaştırıcının mantığını sabit Godot çıktılarıyla sınıyor: aynı sonucu
geçiriyor mu, ayrışanı yakalıyor mu, eksik çıktıyı sessizce yutuyor mu.
"""

import importlib.util
import json
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parent.parent


def _yukle(ad, dosya):
    spec = importlib.util.spec_from_file_location(ad, KOK / "arac" / dosya)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


k = _yukle("motor_karsilastir", "motor-karsilastir.py")
z = _yukle("zipla_egrisi", "zipla-egrisi.py")


def _log(tmp_path, olcum, gurultu=True):
    satirlar = []
    if gurultu:
        satirlar.append("Godot Engine v4.7.2.stable.official - https://godotengine.org")
        satirlar.append("")
    satirlar.append("MOTOR_OLCUM " + json.dumps(olcum))
    yol = tmp_path / "motor.log"
    yol.write_text("\n".join(satirlar) + "\n", encoding="utf-8")
    return yol


def _uyumlu():
    """Python kopyasıyla birebir aynı, motorun üretebileceği bir ölçüm."""
    o = k.python_olcumu(z)
    o["godot"] = "4.7.2-stable (official)"
    return o


def test_motor_ile_ayni_olcum_gecer(tmp_path):
    assert k.main(["x", str(_log(tmp_path, _uyumlu()))]) == 0


def test_carpisma_payi_kadar_fark_tolere_edilir(tmp_path):
    o = _uyumlu()
    o["tam"] += 0.06          # Godot 4.7.2'de gozlenen fark mertebesi
    o["erken"] += 0.06
    assert k.main(["x", str(_log(tmp_path, o))]) == 0


def test_tepe_ayrisirsa_kirmizi(tmp_path):
    """oyuncu.gd'de yercekimi ziplamadan sonra uygulanirsa motor ~53 px olcer."""
    o = _uyumlu()
    o["tam"] = 52.89
    assert k.main(["x", str(_log(tmp_path, o))]) == 1


def test_readme_yuvarlamasini_degistiren_fark_kirmizi(tmp_path):
    """Yarim pikselin altinda kalsa da README'deki tam sayiyi degistiren fark."""
    o = _uyumlu()
    kopya = o["erken"]
    o["erken"] = round(kopya) + 0.5001      # ornegin 35.38 -> 35.5001: yuvarlama 36
    assert abs(o["erken"] - kopya) < k.TOLERANS_PX, "test kurulumu: fark toleransin icinde olmali"
    assert k.main(["x", str(_log(tmp_path, o))]) == 1


@pytest.mark.parametrize("ad", ["kojot_010", "kojot_015", "tampon_008", "tampon_020"])
def test_davranis_ayrisirsa_kirmizi(tmp_path, ad):
    o = _uyumlu()
    o[ad] = not o[ad]
    assert k.main(["x", str(_log(tmp_path, o))]) == 1


def test_farkli_fizik_adimi_kirmizi(tmp_path):
    o = _uyumlu()
    o["tick"] = 120
    assert k.main(["x", str(_log(tmp_path, o))]) == 1


def test_eksik_alan_kirmizi_ve_cokmez(tmp_path):
    o = _uyumlu()
    del o["tam"]
    assert k.main(["x", str(_log(tmp_path, o))]) == 1


def test_olcum_satiri_yoksa_kirmizi(tmp_path):
    yol = tmp_path / "motor.log"
    yol.write_text("SCRIPT ERROR: Parse Error\n", encoding="utf-8")
    assert k.main(["x", str(yol)]) == 1


def test_dosya_yoksa_kirmizi(tmp_path):
    assert k.main(["x", str(tmp_path / "yok.log")]) == 1


def test_arguman_yoksa_kullanim(capsys):
    assert k.main(["x"]) == 2
    assert "kullanim" in capsys.readouterr().out


def test_kesme_carpani_export_olarak_okunuyor():
    """Kesme carpani artik Inspector'dan ayarlanabiliyor; kopya onu okumali."""
    kaynak = (KOK / "yandan-gorunum" / "scripts" / "oyuncu.gd").read_text(encoding="utf-8")
    assert "@export var kesme_carpani" in kaynak
    assert "velocity.y *= kesme_carpani" in kaynak
    assert z.KESME == pytest.approx(z._export(kaynak, "kesme_carpani"))
