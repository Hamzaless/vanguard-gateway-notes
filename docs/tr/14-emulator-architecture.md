# Emülatör mimarisi (ne yerine ne geçiyor)

**Türkçe** · [English](../14-emulator-architecture.md)

> Bir istemci emülatörünün referans mimarisi: hangi bileşen hangi yerel bileşenin yerine geçiyor
> ve her ikame neyi yapabilir / yapamaz.
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası. Yalnız savunma amaçlı araştırma.

## 14.1 Bileşen haritası

| Yerel bileşen | İşi | İkame | Sınırı |
|---|---|---|---|
| `vgc.exe` (servis) | IPC borusunu sahiplenir, gateway trafiğini sarar, görev modüllerini çözer | IPC pipe sunucusu (`reference/pipe_server.py` deseni) | kabul edilen gateway auth üretemez (§14.4) |
| `vgk.sys` (sürücü) | cihaz kimliği parçalarını, boot seed'i, HMAC'ı, imza/sağlık kanıtını üretir | IOCTL sözleşmesini yanıtlayan sürücü | döndürdüğü değerler gerçek sürücünün değerleri değildir |
| `vgrl.dll` | başlatıcı için bağımlılık durumu (1342–1346) | ordinal-only shim DLL | yalnızca kapıyı etkiler, yaptırımı değil |
| Riot Client bağımlılık kontrolü | "kurulu / yeniden başlatma gerekli" kararı | tutarlı registry + servis durumu | formül girdi odaklıdır, yamanamaz |
| gateway oturumu | kimliği doğrular, dönen anahtarlar verir | yok | çekirdek tarafındaki kanıtı ister |

## 14.2 Sürücüden istenenler

İstemci tarafından gözlenen IOCTL sözleşmesi:

| Kod | Amaç |
|---|---|
| `0x22C000` | disk kimlikleri: `u32 sayı` + `"C:\Serial: <seri>.<model>\0"` × N (5 slot, 485 B) |
| `0x22C028` | sürücü sürüm dizesi |
| `0x22C034` | kalp atışı yükü (`0x03`/`0x67` verisi) |
| `0x22C03C` | el sıkışma |
| `0x22C04C` | opsiyonel sorgu; gerçek sürücü `0xC0000002` döner, istemci devam eder |
| `0x22C0xx` | toplam 88 kabul edilen kod (whitelist gerçek sürücüde düz metin bir switch) |

Ayrıca istemci bir **önyükleme damgası** dosyasını (tek bayt `0x01`) ve cihaz kimliği içinde
kullanılan IOCTL değerlerini okur:

```
#9   önyükleme tohumu (16 B)
#11  SHA-512 bloğu  -> cihaz kimliği p2 (64 B)
#12  SHA-512 bloğu  -> cihaz kimliği p3 (64 B)
#18  HMAC-SHA1      -> bütünlük alanı ht
```

**Asıl sınır burasıdır.** p2/p3 sürücünün içinde, kullanıcı moduna hiç çıkmayan bir sırla üretilir.
İkame bir sürücü *sabit* değerler döndürebilir (istemciyi yerelde mutlu etmeye yeter) ama bunlar
gerçek sürücünün o donanım için üreteceği değerler değildir; sunucu bunları telemetriyle
ilişkilendirir.

## 14.3 Pipe sunucusunun yanıtlaması gerekenler

```
0x64 -> 0x65 (1250 B: oyuncu kimliği, token, ürün, oturum kimliği) sonra 0x09 (40 B)
0x03 -> 0x04 (40 B, sayaç yankısı)
0x69 -> 0x3EB (36 B, reasons = 0)
0x02, 0x67, bilinmeyen -> cevap yok
```

Tam bayt düzenleri `05-ipc-pipe.md`'de; çalışan kodlayıcı `reference/pipe_proto.py`'de
(kendi testi 1250/40/36/40 boyutlarını doğrular).

## 14.4 İkame edilemeyenler

1. **Gateway kimlik doğrulaması.** RSA bloğu sunucu anahtarıyla sarılır (kurtarılabilir, §5) ama
   düz metin p2/p3 ve `ht`/`htt`/`gg` taşır. p2/p3 taklit edilemez; bu kontrolleri geçemeyen bir
   istek göndermek de başlı başına tespit sinyalidir (ölçüm: 0,5–2,7 s'de ban, §7).
2. **Attestation.** Kullanıcı modundaki hiçbir bileşen üretemez.
3. **Oturum uygunluğu.** Platforma karar verir; istemci yalnız durumu sunabilir.

## 14.5 Pratik sonuç

İstemci emülatörü **yerel** görünümü tutarlı yapabilir: oyun sağlıklı bir pipe, var olan bir sürücü,
çalışan bir servis ve başlatılabilir bir ürün görür. Bu, oyunu başlatmaya ve yerel oturum nesnesini
bir süre canlı tutmaya yeter.

Platform oturumunu **süresiz** canlı tutmaya yetmez: gözlenen üst sınır 646 s ve 429 bütçesi
(15 dakikada 2–3 auth) oturum ömründen kısa. İki kısıt kesiştiği için sürekli çalışma istemci
tarafında mümkün değildir.

## 14.6 Etik

Yukarıdakilerin tamamı protokol analizidir. Böyle bir ikameyi kurmak veya çalıştırmak Riot Games
Hizmet Şartları'nı ihlal eder, kalıcı yasakla sonuçlanır ve diğer oyuncuların deneyimini bozar.
