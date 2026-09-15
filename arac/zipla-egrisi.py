#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""README'deki zıplama eğrilerinin kaynağı.

`yandan-gorunum/scripts/oyuncu.gd` içindeki `_physics_process` gövdesinin
birebir kopyası. Sabitler o dosyadan, fizik adımı `project.godot`
içindeki 60 Hz'den geliyor. Godot'ta +y aşağı; burada da öyle.

Amaç: `assets/zipla-hissi.svg` üzerindeki sayıların elle uydurulmadığını
göstermek. Bağımlılık yok:

    python3 arac/zipla-egrisi.py
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

DT = 1.0 / 60.0            # project.godot: physics/common/physics_ticks_per_second
ZIPLA_GUCU = 330.0         # oyuncu.gd: @export var zipla_gucu
YERCEKIMI = 980.0          # oyuncu.gd: @export var yercekimi
KOJOT = 0.12               # oyuncu.gd: @export var kojot_suresi
TAMPON = 0.12              # oyuncu.gd: @export var zipla_tampon_suresi
KESME = 0.45               # oyuncu.gd: velocity.y *= 0.45


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
