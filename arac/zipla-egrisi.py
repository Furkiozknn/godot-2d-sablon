#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""README'deki zıplama eğrilerinin kaynağı.

`yandan-gorunum/scripts/oyuncu.gd` içindeki `_physics_process` gövdesinin
birebir kopyası. Sabitler o dosyadan, fizik adımı `project.godot`'tan
**çalışma anında okunur** — burada kopyalanmaz. Denetleyicinin hissi
değişirse bu çıktı da, README'deki eğriler de onu takip eder. Godot'ta
+y aşağı; burada da öyle.

Amaç: `docs/zipla-hissi.svg` üzerindeki sayıların elle uydurulmadığını
göstermek. Bağımlılık yok:

    python3 arac/zipla-egrisi.py      # Windows'ta: python arac\zipla-egrisi.py
"""

import sys

# Windows konsolu varsayilan olarak cp857/cp1254 kullanir; cikti borulandiginda
# (`> dosya`, CI logu, editor terminali) Python o kod sayfasina yazmaya calisir
# ve Turkce harfler bozulur ya da UnicodeEncodeError atar. stdout'u UTF-8'e
# sabitlemek ikisini de onler; eski surumlerde sessizce atlanir.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError, ValueError):  # Python < 3.7 veya tuhaf stdout
    pass

import re
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
_GD = KOK / "yandan-gorunum" / "scripts" / "oyuncu.gd"
_PROJE = KOK / "yandan-gorunum" / "project.godot"


def _dosya(yol):
    try:
        return yol.read_text(encoding="utf-8")
    except OSError as e:
        raise SystemExit(f"okunamadi: {yol} ({e})")


def _export(kaynak, ad):
    """oyuncu.gd icindeki `@export var <ad>: float = <sayi>` degerini okur."""
    m = re.search(rf"@export\s+var\s+{ad}\s*:\s*float\s*=\s*([0-9.]+)", kaynak)
    if not m:
        raise SystemExit(f"oyuncu.gd icinde '{ad}' bulunamadi - adi mi degisti?")
    return float(m.group(1))


# Sabitler oyuncu.gd'den OKUNUR, burada kopyalanmaz. Boylece birileri
# denetleyicinin hissini degistirdiginde bu betigin ciktisi ve README'deki
# egriler kendiliginden onu takip eder; sessizce yanlis kalamazlar.
_KAYNAK = _dosya(_GD)
ZIPLA_GUCU = _export(_KAYNAK, "zipla_gucu")
YERCEKIMI = _export(_KAYNAK, "yercekimi")
KOJOT = _export(_KAYNAK, "kojot_suresi")
TAMPON = _export(_KAYNAK, "zipla_tampon_suresi")

_kesme = re.search(r"velocity\.y\s*\*=\s*([0-9.]+)", _KAYNAK)
if not _kesme:
    raise SystemExit("oyuncu.gd icinde degisken zipla kesmesi (velocity.y *= ...) bulunamadi")
KESME = float(_kesme.group(1))

_tick = re.search(r"physics_ticks_per_second\s*=\s*([0-9]+)", _dosya(_PROJE))
TICK = int(_tick.group(1)) if _tick else 60      # Godot varsayilani 60
DT = 1.0 / TICK


def kos(sure, y0=0.0, zemin_biter=None, bas_t=None, birak_t=None):
    """Tek bir koşuyu simüle eder.

    y0            başlangıç yüksekliği (px, yukarı pozitif)
    zemin_biter   bu andan sonra ayak altında zemin yok (kenardan düşme)
    bas_t/birak_t "zipla" tuşuna basma / bırakma anları (sn)
    """
    y, vy = -y0, 0.0
    kojot = KOJOT if y0 == 0.0 else 0.0
    tampon = 0.0
    t, iz, zipladi, kondu = 0.0, [], None, None

    while t <= sure + 1e-9:
        iz.append((t, -y))
        yerde = y >= -1e-9 and vy >= 0.0 and (zemin_biter is None or t < zemin_biter)

        if not yerde:
            vy += YERCEKIMI * DT
            kojot -= DT
        else:
            kojot = KOJOT
            if kondu is None and t > 0.0:
                kondu = t
            y, vy = 0.0, min(vy, 0.0)

        basildi = bas_t is not None and abs(t - bas_t) < DT / 2
        tampon = TAMPON if basildi else tampon - DT

        if tampon > 0.0 and kojot > 0.0:
            vy, tampon, kojot = -ZIPLA_GUCU, 0.0, 0.0
            if zipladi is None:
                zipladi = t

        if birak_t is not None and abs(t - birak_t) < DT / 2 and vy < 0.0:
            vy *= KESME

        y += vy * DT
        if y > 0.0 and (zemin_biter is None or t < zemin_biter):
            y, vy = 0.0, 0.0          # zemine kenetle
        t += DT

    return {"iz": iz, "zipladi": zipladi, "kondu": kondu,
            "tepe": max(v for _, v in iz)}


def main():
    tam = kos(0.72, bas_t=0.0)
    erken = kos(0.72, bas_t=0.0, birak_t=0.10)
    teorik = ZIPLA_GUCU ** 2 / (2 * YERCEKIMI)

    print("1. Değişken zıplama yüksekliği")
    print(f"   tuş basılı tutuldu       : {tam['tepe']:5.1f} px")
    print(f"   0,10 s'de bırakıldı      : {erken['tepe']:5.1f} px  "
          f"(tam zıplamanın %{100 * erken['tepe'] / tam['tepe']:.0f}'i)")
    print(f"   teorik v^2/2g            : {teorik:5.1f} px  "
          f"(ayrık entegrasyon {tam['tepe'] - teorik:+.1f} px fark yaratıyor)")

    print("\n2. Kojot süresi")
    for gecikme in (0.10, 0.15):
        r = kos(0.72, zemin_biter=0.10, bas_t=0.10 + gecikme)
        print(f"   kenardan +{gecikme:.2f} s sonra basıldı : "
              f"{'zıpladı' if r['zipladi'] is not None else 'geç kaldı, düşmeye devam'}")

    print("\n3. Zıplama tamponu")
    for onceden in (0.08, 0.20):
        dusus = kos(0.72, y0=45.0)
        inis = dusus["kondu"]
        r = kos(0.72, y0=45.0, bas_t=inis - onceden)
        print(f"   inişe {onceden:.2f} s kala basıldı     : "
              f"{'iniş anında zıpladı' if r['zipladi'] is not None else 'tuş yutuldu'}")


if __name__ == "__main__":
    main()
