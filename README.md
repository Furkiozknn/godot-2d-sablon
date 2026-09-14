# Godot 2D ÅablonlarÄ±

Bu klasÃ¶r iki hazÄ±r, **Ã§alÄ±ÅŸÄ±r durumda** Godot 4.7 projesi iÃ§erir:

| KlasÃ¶r | TÃ¼r | Ne var iÃ§inde |
|---|---|---|
| `ustten-gorunum/` | Top-down | 8 yÃ¶nlÃ¼ ivmeli hareket, sÄ±nÄ±rlÄ± oda, takip eden kamera |
| `yandan-gorunum/` | Side-scroller | YerÃ§ekimi, zÄ±plama, 2 platform, takip eden kamera |

## Hemen Ã§alÄ±ÅŸtÄ±r

```
godot --path "D:\Repolar\godot-2d-sablon\ustten-gorunum"
godot --path "D:\Repolar\godot-2d-sablon\yandan-gorunum"
```

Ya da Godot'u aÃ§Ä±p **Import** ile `project.godot` dosyasÄ±nÄ± seÃ§.

**Kontroller**
- Ãœstten gÃ¶rÃ¼nÃ¼m: `WASD` / yÃ¶n tuÅŸlarÄ±, `E` etkileÅŸim
- Yandan gÃ¶rÃ¼nÃ¼m: `A`/`D` hareket, `BoÅŸluk` veya `W` zÄ±pla

## Neden bu ayarlar?

Bu makinede **Intel UHD Graphics** var (tÃ¼mleÅŸik, ayrÄ± ekran kartÄ± yok) ve
sÃ¼rÃ¼cÃ¼sÃ¼ eski. Godot 4'Ã¼n varsayÄ±lan **Forward+** renderer'Ä± Vulkan istiyor ve
eski Intel sÃ¼rÃ¼cÃ¼lerinde Ã§Ã¶kme/doÄŸrulama hatasÄ± biliniyor bir sorun. O yÃ¼zden
her iki proje de **GL Compatibility** renderer'Ä±na ayarlÄ±:

```
renderer/rendering_method="gl_compatibility"
```

Bu bir taviz deÄŸil â€” 2D iÃ§in doÄŸru seÃ§im zaten: daha hafif, tÃ¼mleÅŸik GPU'da
daha hÄ±zlÄ±, web export'u da sorunsuz.

DiÄŸer ayarlar:
- **640x360 taban Ã§Ã¶zÃ¼nÃ¼rlÃ¼k**, 1280x720 pencere â€” 2x, 3x tam kat Ã¶lÃ§ekler
- `stretch/mode="canvas_items"` + `aspect="keep"` â€” piksel bozulmaz
- `default_texture_filter=0` (nearest) â€” pixel art bulanÄ±klaÅŸmaz
- `snap_2d_transforms_to_pixel=true` â€” titreme (jitter) olmaz
- 60 fizik tick

## KlasÃ¶r dÃ¼zeni

```
<proje>/
  scenes/      .tscn sahne dosyalarÄ±
  scripts/     .gd kod dosyalarÄ±
  assets/
    sprites/   gÃ¶rseller
    audio/     ses
    fonts/     yazÄ± tipleri
  addons/      eklentiler (ÅŸimdilik boÅŸ, gerekmiyor)
  icon.svg     yer tutucu ikon â€” kendi ikonunla deÄŸiÅŸtir
```

`ortak-varliklar/` klasÃ¶rÃ¼ iki projede de kullanacaÄŸÄ±n ortak dosyalar iÃ§in.

## DÄ±ÅŸa aktarma

`export_presets.cfg` hazÄ±r, iki hedef tanÄ±mlÄ±:
- **Windows Masaustu** -> `build/windows/oyun.exe`
- **Web (HTML5)** -> `build/web/index.html`

Komut satÄ±rÄ±ndan:
```
godot --headless --path "<proje yolu>" --export-release "Windows Masaustu"
godot --headless --path "<proje yolu>" --export-release "Web (HTML5)"
```

Export ÅŸablonlarÄ± (4.7.2) zaten kurulu, ek indirme gerekmiyor.

## Yandan gÃ¶rÃ¼nÃ¼mdeki Ã¼Ã§ Ã¶nemli detay

`scripts/oyuncu.gd` iÃ§inde platform oyunlarÄ±nÄ± "iyi hissettiren" Ã¼Ã§ teknik var.
Bunlar olmadan oyun teknik olarak Ã§alÄ±ÅŸÄ±r ama hantal hissettirir:

1. **Kojot sÃ¼resi** (coyote time) â€” platformun kenarÄ±ndan dÃ¼ÅŸtÃ¼kten sonra
   0,12 saniye daha zÄ±playabilirsin. Oyuncu "tam basmÄ±ÅŸtÄ±m" hissi yaÅŸamaz.
2. **ZÄ±plama tamponu** (jump buffer) â€” yere inmeden hemen Ã¶nce boÅŸluÄŸa
   bastÄ±ysan, yere deÄŸdiÄŸin an zÄ±plar. BasÄ±lan tuÅŸ yutulmaz.
3. **DeÄŸiÅŸken zÄ±plama yÃ¼ksekliÄŸi** â€” tuÅŸu erken bÄ±rakÄ±rsan zÄ±plama kÄ±salÄ±r.
   KÄ±sa/uzun zÄ±plama kontrolÃ¼ verir.

DeÄŸerleri editÃ¶rde `Oyuncu` dÃ¼ÄŸÃ¼mÃ¼nÃ¼ seÃ§ip Inspector'dan deneyerek ayarla.

## Elindeki araÃ§lar

| AraÃ§ | Yol | Ne iÃ§in |
|---|---|---|
| **Pixelorama 1.2.1** | `D:\Araclar\Pixelorama\Pixelorama-Windows-64bit\Pixelorama.exe` | **Sprite ve pixel art + animasyon.** Ä°lk aÃ§acaÄŸÄ±n bu. Godot ile yazÄ±lmÄ±ÅŸ, sprite sheet dÄ±ÅŸa aktarÄ±r. |
| Krita 5.3.3 | `D:\Araclar\krita\bin\krita.exe` | Elle Ã§izim, bÃ¼yÃ¼k tuval, doku. Pixelorama'yÄ± tamamlar. |
| rFXGen 5.0 | `D:\Araclar\rFXGen\rfxgen_v5.0_win_x64\rfxgen.exe` | ZÄ±plama/vuruÅŸ/toplama sesi Ã¼retir. Tek tÄ±kla retro sfx. |
| butler | `D:\Araclar\butler\butler.exe` | Oyunu itch.io'ya yÃ¼kler. |
| ffmpeg 9.0.1 | PATH'te | Ses/video dÃ¶nÃ¼ÅŸtÃ¼rme. |

## Sonraki adÄ±mlar

1. **Pixelorama**'yÄ± aÃ§, 16x16 veya 32x32 bir karakter Ã§iz, `assets/sprites/` iÃ§ine PNG kaydet.
2. `Gorsel` dÃ¼ÄŸÃ¼mÃ¼nÃ¼ `Polygon2D`'den `AnimatedSprite2D`'ye Ã§evir, SpriteFrames
   oluÅŸtur.
3. Ãœstten gÃ¶rÃ¼nÃ¼mde zemin iÃ§in **TileMapLayer** ekle (Godot'un dahili tilemap
   editÃ¶rÃ¼ yeterli â€” Tiled gibi harici araca gerek yok).
4. Sesler iÃ§in `assets/audio/` + `AudioStreamPlayer2D`.

_Bu ÅŸablonlar Claude tarafÄ±ndan hazÄ±rlandÄ± ve headless iÃ§e aktarma testinden
hatasÄ±z geÃ§ti (2026-09-14)._