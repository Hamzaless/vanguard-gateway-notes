# Vanguard Gateway — Tersine Mühendislik Notları

Vanguard istemci yığını (vgc / vgk) için tel protokolü, kriptografi, IPC çerçeveleme ve istemci
bağımlılık kapıları. Hedef sürümler: Vanguard 1.19.1.x, VALORANT release-13.09.

**Türkçe** · [English](README.md)

Savunma amaçlı güvenlik araştırması. Yalnızca protokol dokümantasyonu, atlatma aracı yok.
Kullanımı Riot Games Hizmet Şartları'nı ihlal eder ve kalıcı yasakla sonuçlanır.
Hesap kimliği, kimlik bilgisi veya oturum anahtarı içermez.

## Dokümanlar

| Dosya | İçerik |
|---|---|
| [docs/tr/00-summary.md](docs/tr/00-summary.md) | Doğrulanmış bulgular, kapsam |
| [docs/tr/01-protocol.md](docs/tr/01-protocol.md) | Uç noktalar, başlıklar, çerçeve, zarf |
| [docs/tr/02-crypto.md](docs/tr/02-crypto.md) | RSA-OAEP (SHA-512), AES-256-GCM, `J0+1` |
| [docs/tr/03-auth-payload.md](docs/tr/03-auth-payload.md) | Kimlik doğrulama alanları, cihaz kimliği, `ht` |
| [docs/tr/04-key-recovery.md](docs/tr/04-key-recovery.md) | Sunucu RSA anahtarının kurtarılması |
| [docs/tr/05-ipc-pipe.md](docs/tr/05-ipc-pipe.md) | 26 B IPC çerçevesi, mesaj tipleri |
| [docs/tr/06-client-gates.md](docs/tr/06-client-gates.md) | `restartRequired`, vgrl, Riot ID kapısı |
| [docs/tr/07-detection.md](docs/tr/07-detection.md) | Yaptırım sınıflandırması, ölçülen zamanlama |
| [docs/tr/08-negative-results.md](docs/tr/08-negative-results.md) | 20 çürütülmüş hipotez |
| [docs/tr/09-methodology.md](docs/tr/09-methodology.md) | Teknikler, doğrulama kuralı |
| [docs/tr/10-open-questions.md](docs/tr/10-open-questions.md) | Açık maddeler, geri çekilen iddialar |
| [docs/tr/11-reproducibility.md](docs/tr/11-reproducibility.md) | Yeniden üretim notları |
| [docs/tr/12-glossary.md](docs/tr/12-glossary.md) | Terimler |
| [docs/tr/13-rms.md](docs/tr/13-rms.md) | RMS oturum taşıyıcısı |
| [docs/tr/14-emulator-architecture.md](docs/tr/14-emulator-architecture.md) | Bileşen ikamesi ve sınırları |
| [docs/tr/15-memory-capture.md](docs/tr/15-memory-capture.md) | Canlı bellek dökümü ve incelemesi |
| [docs/tr/VERIFICATION.md](docs/tr/VERIFICATION.md) | İddia bazlı doğrulama |
| [schemas/vanguard.proto](schemas/vanguard.proto) | Trafikten çıkarılan alan numaraları |
| [data/measurements.md](data/measurements.md) | Kota, süreler, sayaçlar |
| [data/knowledge.json](data/knowledge.json) | Makine-okunur bilgi tabanı |
| [reference/](reference/) | Çalışır referans kod (İngilizce) |

## Durum

| Alan | Durum |
|---|---|
| Tel biçimi, zarf | çözüldü, byte düzeyinde doğrulandı |
| Kriptografi | çözüldü, gidiş-dönüş doğrulandı |
| Kimlik doğrulama alanları | çözüldü; p2/p3 türetimi çekirdekte |
| Sunucu açık anahtarı | canlı bellekten kurtarılabilir |
| IPC protokolü | çözüldü, 62/62 mesaj |
| İstemci kapıları | çözüldü |
| RMS taşıyıcısı | haritalandı, kapanış davranışı ölçüldü |
| Sanal bölüm CFG | statik çıkarılamıyor |
| `htt` / `gg` | doğrulama teyitli, türetim bilinmiyor |

## Referans kod

```bash
python3 reference/run_all.py     # çevrimdışı self-test
```

## Hukuki

Riot Games istemci değiştirmeyi ve anti-cheat atlatmayı yasaklar. Bu materyal savunma amaçlı
araştırma ve protokol eğitimi için yayınlanmıştır. Kimlik bilgisi, oturum anahtarı veya hesap
tanımlayıcısı içermez.

MIT lisanslı.
