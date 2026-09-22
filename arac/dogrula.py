#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""README'deki zıplama sayıları hâlâ doğru mu?

`arac/zipla-egrisi.py` sabitleri `yandan-gorunum/scripts/oyuncu.gd`'den ve
fizik adımını `project.godot`'tan okuyor. Bu betik o simülasyonu çalıştırıp
sonucu README'nin *yazdığı* sayılarla karşılaştırır.

Neden var: denetleyicinin hissini değiştiren bir commit (zıplama gücü,
yerçekimi, kesme çarpanı, kojot ya da tampon süresi) README'yi sessizce
yanlışa düşürebilir. "Ölçülmüş, tahmin edilmemiş" iddiası ancak bir kapı
onu koruyorsa iddia olmaktan çıkar.

Tek bir sayı iki yerde yazmıyor: beklenen değerler README'den okunuyor,
gerçek değerler simülasyondan geliyor.

    python3 arac/dogrula.py
"""

import importlib.util
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError, ValueError):
    pass

KOK = Path(__file__).resolve().parent.parent


def _yukle():
    yol = KOK / "arac" / "zipla-egrisi.py"
    spec = importlib.util.spec_from_file_location("zipla_egrisi", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _readme_sayilari():
    metin = (KOK / "README.md").read_text(encoding="utf-8")
    kaliplar = {
        "tam": r"tuşu basılı tutmak (\d+) piksel",
        "erken": r"0,10 saniyede bırakmak (\d+) piksel",
        "kojot": r"kojot süresi kenardan (\d+,\d+) saniye",
        "tampon": r"zıplama tamponu inişten (\d+,\d+) saniye",
    }
    bulunan = {}
    for ad, kalip in kaliplar.items():
        m = re.search(kalip, metin)
        if not m:
            raise SystemExit(
                f"README.md icinde '{ad}' sayisi bulunamadi (kalip: {kalip}).\n"
                "Alt metin degistiyse bu betikteki kalip da guncellenmeli."
            )
        bulunan[ad] = float(m.group(1).replace(",", "."))
    return bulunan


def main():
    z = _yukle()
    bekleniyor = _readme_sayilari()
    hata = 0

    tam = z.kos(0.72, bas_t=0.0)["tepe"]
    erken = z.kos(0.72, bas_t=0.0, birak_t=0.10)["tepe"]

    kontroller = [
        ("degisken zipla - tus basili", round(tam), bekleniyor["tam"]),
        ("degisken zipla - 0,10 s'de birakildi", round(erken), bekleniyor["erken"]),
        ("kojot suresi (oyuncu.gd)", z.KOJOT, bekleniyor["kojot"]),
        ("zipla tamponu (oyuncu.gd)", z.TAMPON, bekleniyor["tampon"]),
    ]
    for ad, gercek, beklenen in kontroller:
        if abs(gercek - beklenen) > 1e-9:
            print(f"  HATA  {ad}: simulasyon {gercek}, README {beklenen}")
            hata += 1
        else:
            print(f"  TAMAM {ad}: {gercek}")

    # Davranis kapilari: sayilar degil, kararlar.
    kojot_icinde = z.kos(0.72, zemin_biter=0.10, bas_t=0.20)["zipladi"] is not None
    kojot_disinda = z.kos(0.72, zemin_biter=0.10, bas_t=0.25)["zipladi"] is not None
    dusus = z.kos(0.72, y0=45.0)["kondu"]
    tampon_icinde = z.kos(0.72, y0=45.0, bas_t=dusus - 0.08)["zipladi"] is not None
    tampon_disinda = z.kos(0.72, y0=45.0, bas_t=dusus - 0.20)["zipladi"] is not None

    davranis = [
        ("kenardan +0,10 s sonra ziplanabiliyor", kojot_icinde, True),
        ("kenardan +0,15 s sonra ziplanamiyor", kojot_disinda, False),
        ("inise 0,08 s kala basilan tus hatirlaniyor", tampon_icinde, True),
        ("inise 0,20 s kala basilan tus yutuluyor", tampon_disinda, False),
    ]
    for ad, gercek, beklenen in davranis:
        if gercek is not beklenen:
            print(f"  HATA  {ad}: {gercek}")
            hata += 1
        else:
            print(f"  TAMAM {ad}")

    if hata:
        print(f"\n{hata} kontrol basarisiz - README ile denetleyici ayrismis.")
        return 1
    print(f"\n{len(kontroller) + len(davranis)} kontrol gecti.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
