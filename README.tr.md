# Vanguard Gateway — Tersine Mühendislik Notları

> Savunma amaçlı güvenlik araştırması. Yalnızca protokol dokümantasyonu; atlatma aracı yok.
> Buradaki bilgileri kullanmak Riot Games Hizmet Şartları'nı ihlal eder ve kalıcı yasakla sonuçlanır.

**Türkçe** · [English](README.md)

**Başlangıç:** [`docs/tr/01-protocol.md`](docs/tr/01-protocol.md)

## Dokümanlar

| Dosya | İçerik |
|---|---|
| [`docs/tr/00-summary.md`](docs/tr/00-summary.md) | Doğrulanmış bulgular, kapsam, kapsam dışı |
| [`docs/tr/01-protocol.md`](docs/tr/01-protocol.md) | Uç noktalar, başlıklar, çerçeve, zarf yerleşimi |
| [`docs/tr/02-crypto.md`](docs/tr/02-crypto.md) | RSA-OAEP (SHA-512), AES-256-GCM, `J0+1` kuralı, boyut özdeşlikleri |
| [`docs/tr/03-auth-payload.md`](docs/tr/03-auth-payload.md) | 11 alanlı kimlik doğrulama mesajı, cihaz kimliği aritmetiği, `ht` formülü |
| [`docs/tr/04-key-recovery.md`](docs/tr/04-key-recovery.md) | Sunucu RSA anahtarının canlı süreçten kurtarılması; 401/400 oracle |
| [`docs/tr/05-ipc-pipe.md`](docs/tr/05-ipc-pipe.md) | 26 baytlık pipe çerçevesi, `0x64→0x65` (1250 B), heartbeat, sağlık kontrolü |
| [`docs/tr/06-client-gates.md`](docs/tr/06-client-gates.md) | `restartRequired`, `vgrl` ordinal'ları, Riot ID kapısı, ürün oturumu |
| [`docs/tr/07-detection.md`](docs/tr/07-detection.md) | Yaptırım sınıflandırması ve ölçülen zamanlama |
| [`docs/tr/08-negative-results.md`](docs/tr/08-negative-results.md) | 20 çürütülmüş hipotez (tekrar denemeyin) |
| [`docs/tr/09-methodology.md`](docs/tr/09-methodology.md) | Teknikler, doğrulama kuralı, adres hiyerarşisi |
| [`docs/tr/10-open-questions.md`](docs/tr/10-open-questions.md) | Açık maddeler, geri çekilen iddialar, sınırlar |
| [`docs/tr/11-reproducibility.md`](docs/tr/11-reproducibility.md) | Yeniden üretim notları |
| [`docs/tr/12-glossary.md`](docs/tr/12-glossary.md) | Terimler |
| [`docs/tr/VERIFICATION.md`](docs/tr/VERIFICATION.md) | İddia bazlı doğrulama kaydı |
| [`docs/tr/13-rms.md`](docs/tr/13-rms.md) | RMS oturum taşıyıcısı |
| [`docs/tr/14-emulator-architecture.md`](docs/tr/14-emulator-architecture.md) | Ne yerine ne geçiyor, sınırlar |
| [`data/knowledge.json`](data/knowledge.json) | Ajanlar için makine-okunur bilgi tabanı |
| [`docs/tr/VERIFICATION.md`](docs/tr/VERIFICATION.md) | İddia bazlı doğrulama: değer, kanıt kaynağı, durum |
| [`schemas/vanguard.proto`](schemas/vanguard.proto) | **Doğrulanmış** alan numaraları (düz metinden çıkarıldı) |
| [`data/measurements.md`](data/measurements.md) | Kota, süreler, sayaçlar, oracle kodları |
| [`reference/`](reference/) | Çalışır referans kod: istek üretimi + pipe cevapları (İngilizce) |

## Durum

| Alan | Durum |
|---|---|
| Tel biçimi ve zarf | çözüldü, byte düzeyinde doğrulandı |
| Kriptografi (OAEP-SHA512 + AES-256-GCM) | çözüldü, gidiş-dönüş doğrulandı |
| Kimlik doğrulama alanları ve cihaz kimliği | çözüldü (p1/p5/p6 donanımdan; p2/p3 sürücü IOCTL #11/#12 çıktısı) |
| Sunucu açık anahtarı | canlı bellekten kurtarılabilir (oracle ile doğrulandı) |
| IPC (pipe) protokolü | çözüldü, 62/62 mesaj |
| İstemci bağımlılık kapıları | çözüldü (iki formül) |
| Sanal bölümün denetim akışı | statik olarak çıkarılamıyor (ölçüldü) |
| `htt`/`gg` bütünlük alanları | doğrulandıkları kesin, türetim bilinmiyor |

## Hukuki not

Riot Games Hizmet Şartları, anti-cheat'i atlatmak amacıyla istemci değiştirmeyi ve tersine
mühendisliği yasaklar. Bu materyal savunma amaçlı araştırma ve protokol eğitimi için
yayınlanmıştır. Hiçbir kimlik bilgisi, oturum anahtarı veya hesap tanımlayıcısı içermez.
