#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Python kopyası motorla aynı şeyi mi söylüyor?

`arac/zipla-egrisi.py`, `oyuncu.gd`'nin `_physics_process` gövdesinin Python'a
taşınmış hâli; README'deki 58 ve 35 piksel oradan geliyor. Bir kopya ancak
aslıyla karşılaştırıldığı sürece güvenilirdir: `oyuncu.gd`'de satırların
sırası değişirse (örneğin yerçekimi zıplamadan sonra uygulanırsa) Python
kopyası eski sonucu üretmeye devam eder ve hiçbir şey kırmızı yanmaz.

Bu betik o boşluğu kapatır. `arac/motor-olcumu.gd`'nin gerçek Godot'ta
ölçtüğü değerleri okur ve aynı senaryoları Python kopyasında koşturup
karşılaştırır:

    godot --headless --path yandan-gorunum --import
    godot --headless --path yandan-gorunum --script "$PWD/arac/motor-olcumu.gd" > motor.log
    python3 arac/motor-karsilastir.py motor.log

Godot kurulu değilse bu adım yerelde koşmaz; CI her PR'da koşturur.
"""

import importlib.util
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError, ValueError):
    pass

KOK = Path(__file__).resolve().parent.parent
ONEK = "MOTOR_OLCUM "

# Motor ile kopya arasında izin verilen fark. Godot'un çarpışma payı
# (safe_margin) ve kayan nokta sırası yüzünden birebir eşitlik beklenmez;
# ama README tam piksel yazıyor, yani fark yarım pikseli geçmemeli.
TOLERANS_PX = 0.5


def _yukle():
    yol = KOK / "arac" / "zipla-egrisi.py"
    spec = importlib.util.spec_from_file_location("zipla_egrisi", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def olcumu_oku(metin):
    """Godot çıktısından `MOTOR_OLCUM {...}` satırını bulup sözlüğe çevirir."""
    for satir in metin.splitlines():
        satir = satir.strip()
        if satir.startswith(ONEK):
            return json.loads(satir[len(ONEK):])
    raise ValueError("Godot ciktisinda MOTOR_OLCUM satiri yok - olcum betigi calisti mi?")


def python_olcumu(z):
    """Aynı senaryolar, Python kopyasında."""
    dusus = z.kos(0.72, y0=45.0)["kondu"]
    return {
        "tam": z.kos(0.72, bas_t=0.0)["tepe"],
        "erken": z.kos(0.72, bas_t=0.0, birak_t=0.10)["tepe"],
        "kojot_010": z.kos(0.72, zemin_biter=0.10, bas_t=0.20)["zipladi"] is not None,
        "kojot_015": z.kos(0.72, zemin_biter=0.10, bas_t=0.25)["zipladi"] is not None,
        "tampon_008": z.kos(0.72, y0=45.0, bas_t=dusus - 0.08)["zipladi"] is not None,
        "tampon_020": z.kos(0.72, y0=45.0, bas_t=dusus - 0.20)["zipladi"] is not None,
        "tick": z.TICK,
    }


def karsilastir(motor, kopya):
    """(ad, motor, kopya, tamam) listesi döndürür."""
    sonuc = []
    for ad in ("tam", "erken"):
        m, k = motor.get(ad), kopya[ad]
        tamam = (isinstance(m, (int, float))
                 and abs(m - k) <= TOLERANS_PX
                 and round(m) == round(k))
        sonuc.append((ad, m, k, tamam))
    for ad in ("kojot_010", "kojot_015", "tampon_008", "tampon_020", "tick"):
        m, k = motor.get(ad), kopya[ad]
        sonuc.append((ad, m, k, m == k))
    return sonuc


def main(argv):
    if len(argv) != 2:
        print("kullanim: python3 arac/motor-karsilastir.py <godot-ciktisi.log>")
        return 2
    try:
        motor = olcumu_oku(Path(argv[1]).read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError) as e:
        print(f"HATA: {e}")
        return 1

    print(f"motor: Godot {motor.get('godot', '?')}, {motor.get('tick', '?')} Hz")
    hata = 0
    for ad, m, k, tamam in karsilastir(motor, python_olcumu(_yukle())):
        if isinstance(m, float) or isinstance(k, float):
            m_s = f"{m:.2f}" if isinstance(m, (int, float)) else repr(m)
            ayrinti = f"motor {m_s} px, python {k:.2f} px"
        else:
            ayrinti = f"motor {m}, python {k}"
        print(f"  {'TAMAM' if tamam else 'HATA '} {ad:<11} {ayrinti}")
        hata += not tamam

    if hata:
        print(f"\n{hata} olcum ayristi: arac/zipla-egrisi.py artik oyuncu.gd'nin "
              "motordaki davranisini temsil etmiyor.")
        return 1
    print("\nPython kopyasi motorla ayni sonucu veriyor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
