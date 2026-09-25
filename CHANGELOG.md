# Değişiklik günlüğü

Bu şablondan oyun başlattıysanız burası, **kendi projenize taşımaya değer**
değişiklikleri bulacağınız yer. Her madde hangi projeyi ve hangi dosyayı
etkilediğini söyler; güncellemeyi nasıl alacağınız README'deki
[Şablon güncellemelerini almak](README.md#şablon-güncellemelerini-almak)
bölümünde.

Etiketler: **[yandan]** `yandan-gorunum/`, **[üstten]** `ustten-gorunum/`,
**[depo]** yalnızca bu deponun araçları, CI'ı ya da belgeleri — kendi
projenize taşımanız gerekmez.

Henüz sürüm etiketi yok; maddeler commit tarihine göre sıralı.

## Yayımlanmamış

### Oyunu etkileyenler

- **[yandan]** `scenes/level.tscn`: Örnek seviyenin iki ucuna görünmez duvar
  (`SolDuvar`, `SagDuvar`) eklendi. Önceden zeminin kenarından yürüyen oyuncu
  sonsuza kadar düşüyordu.
- **[yandan] [üstten]** `scenes/level.tscn`: `Oyuncu/Kamera` için seviye
  sınırları (`limit_*`) ayarlandı; kamera artık seviyenin dışındaki boşluğu
  göstermiyor. Sınırlar seviyede, `oyuncu.tscn` seviyeden bağımsız kalıyor.
- **[üstten]** `scenes/level.tscn`: `Oyuncu` örneğinin betiği gereksiz yere
  aynı dosyayla eziliyordu; `oyuncu.tscn`'deki betiği değiştirseniz bile
  seviye eskisini kullanırdı. Ezme kaldırıldı.
- **[yandan] [üstten]** `export_presets.cfg`: Web preset'i tek iş
  parçacıklı (`variant/thread_support=false`). Çok iş parçacıklı web çıktısı
  COOP/COEP başlıkları ister; GitHub Pages bunları vermez ve oyun açılmaz.
- **[yandan]** `scripts/oyuncu.gd`: Kesme çarpanı (`kesme_carpani`, 0.45) ve
  yatay `ivme` / `surtunme` (1400 / 1200) artık `@export`; Inspector'dan
  ayarlanabiliyor. Varsayılanlar aynı, his değişmedi.

### Depo

- **[depo]** Zıplama hissi artık gerçek Godot'ta da ölçülüyor
  (`arac/motor-olcumu.gd`) ve Python kopyasıyla karşılaştırılıyor
  (`arac/motor-karsilastir.py`); CI her PR'da koşturuyor.
- **[depo]** `arac/seviye-sinirlari.gd`: oyuncunun örnek seviyeden
  çıkamadığını iki projede de koşturarak gösteriyor; CI'da.
- **[depo]** GitHub Actions: `checkout` v7, `setup-python` v7,
  `upload-sarif` v4 (Node 20 emekliliği). CI'ın indirdiği Godot zip'i
  çalıştırılmadan önce resmî SHA-512 özetiyle karşılaştırılıyor.
- **[depo]** README: hızlı başlangıç, ayar tabloları (her `@export` ve
  varsayılanı; `testler/test_readme_ayarlar.py` bunları `oyuncu.gd` ile
  karşılaştırıyor), şablon güncellemelerini alma yolu, web export'undan
  gerçek ekran görüntüleri. Belgelenen `--export-release` komutu taze bir
  klonda `build/web` klasörü olmadığı için başarısız oluyordu; README artık
  klasörü önce açıyor. Belgelenen `godot --path <proje>` da taze bir klonda
  görseller içe aktarılmadığı için karakteri göstermiyordu; README artık
  önce editörle açmayı ya da bir kez `--import` çalıştırmayı söylüyor.

## 2026-09-22 ve öncesi

- **[depo]** CI: README'deki zıplama sayılarını koruyan kapı, Python
  davranış testleri, iki projenin Godot 4.7.2 ile açılış kontrolü,
  godot-refcheck ile kaynak referansı taraması.
- **[yandan]** `AnimatedSprite2D` ve `idle` / `yuru` / `zipla` / `dus`
  animasyon durumları.
- İlk sürüm: iki proje, GL Compatibility, piksel-mükemmel ayarlar,
  Windows + Web export preset'leri.
