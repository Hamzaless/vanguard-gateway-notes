# Ek bulgular

**Türkçe** · [English](../16-additional-findings.md)

> Proje arşivinden çıkan, önceki dokümanlara sığmayan malzeme: `gg` alanı, VAN/VAL kodları,
> IOCTL işleyici yapısı, görev onay politikası, IPC envanteri, vgc log kodları.
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası. Yalnız savunma amaçlı araştırma.

## 16.1 `gg` alanı

`gg` 20 bayt, base64 ile 28 karakter, `f15` içinde `htt` ve `ht` ile birlikte taşınıyor.

| Özellik | Sonuç |
|---|---|
| Sunucu doğruluyor | orijinal `gg` → **200** (7888 B TokenResponse açıldı); rastgele 20 B → **400** |
| Cihaz kimliğine bağlı | hayır, kimlik rotasyonu geçersiz kılmıyor |
| Token / oturum kimliğine bağlı | hayır |
| Kuruluma özgü sabit | evet |
| Türetim | **bulunamadı**: 22.178 çevrimdışı kombinasyon + 3.669.312 RAM-pencere hash'i, 0 eşleşme |

İstemci tarafında yeniden üretim için tek yol: `gg` **aynen replay** edilir. Üretmek veya
rastgeleleştirmek isteği bozuyor.

Fiziksel bellek taramasında 6 isabet çıktı: 2'si gerçek kimlik doğrulama yükü, 4'ü yanlış pozitif.

## 16.2 `htt` — sızdırılmış model uymuyor

Sızdırılmış `GenerateF16Fields` şu şemayı öneriyor:

```
htt_input = oyuncu kimliği + decode(ht) + meta12 + secret16
htt       = base64( SHA1(htt_input) || meta12 )
```

Dokuz varyant denendi (oyuncu kimliği olarak oturum kimliği / token subject / tiresiz oturum
kimliği, üç sıralama). Hiçbiri gözlenen `htt` ile eşleşmedi. Girdi bileşenlerinden en az biri farklı.

`ht` birebir üretildi:

```
SHA1("6;"+p6 + "1;"+p1 + "2;"+p2 + "3;"+p3 + "5;"+p5 + "1.19.1.18" + MAGIC16)
→ 8e7a6f2c3ee27f1218dd43fd27ce099d78ca3a83
```

Altı varyant (çözülmüş parçalar, hex-string sabit, sabitsiz) eşleşmedi; girdi yukarıdaki düz birleşim.

## 16.3 VAN / VAL kodları

`VAN nnn` dizeleri istemci ikililerinde **düz metin olarak yok**. Sahada görülen eşleme kullanıcı
raporlarından geliyor, ikiliden değil.

Doğrulanmamış hipotez: `VAN nnn`, sürücünün döndürdüğü **NTSTATUS'un düşük baytı**.
Örnek: `0xE0000098` → `0x98` = 152. Aynı aritmetik `0xE0002745` → `0x45` = 69 veriyor.

`VAL 5`, oyun tarafında `PlatformFaulted` karşılığı. `EPlatformFaultReason` 13 değer taşıyor; enum
iki bağımsız kaynaktan çıkarıldı. `VAL 5`'i gateway değil oyun üretiyor.

## 16.4 IOCTL işleyici yapısı

Sürücünün cihaz denetimi dağıtımı kısmen çözüldü:

- Hesaplanmış atlamalar statik çözülebiliyor. Kural: `lea/lea/jmp` kalıbında `hedef = site + 7 + d1 − d2`.
  15/15 devam bloğunda, sonra geniş kümede doğrulandı.
- İşleyici sanılan 15 blok aslında **arama zinciri düğümleri**. Zincir yukarı doğru; 15 bağın 13'ü ölçüldü.
- Gerçek işleyici karşılaştırmanın `je` (eşitlik) dalında, fall-through tarafında değil.
- `0x22C000` (disk serileri) işleyicisi satır satır çıkarıldı: `u32 sayı` + `"C:\Serial: <seri>.<model>\0"`
  girdileri, 5 slot, toplam 485 bayt.
- Sanal bağlam çerçevesi lifted kodda `[rsp+0x228]` olarak geçiyor.

Görülen obfuscator deyimleri: adres gizleme (`lea rip+d` + aritmetik), sabit bölme (magic multiply),
maske sabitleri (`0xF0F0F0F0…`, `0x1E1E1E1E…`, `0x87878787…`). Hiçbiri kalıp eşleştirmeyle
çözülmüyor; canlı yazmaç değeri gerekiyor.

## 16.5 Görev onay politikası

Aynı oturumda ölçülen A/B:

| Gönderilen onay | Sonraki heartbeat |
|---|---|
| 0 | 200 |
| 1 (gerçek görev kimliği, sahte hash) | 200 |
| 4–5 (sahte hash) | **401** — oturum düştü |

Sahte modül hash'i ile onay göndermek oturumu bitiriyor. Onay göndermemek oturumu yaşatıyor;
sunucu görevleri sonraki heartbeat'te geri çekiyor (yük 68 MB → 35 MB).
Kural: gerçekten çalıştırılmamış görev sonucu onaylanmaz.

## 16.6 IPC envanteri (tam arşiv)

| Tip | Ad | Örnek | Boyut | Alan |
|---|---|---|---|---|
| `0x03` | HeartbeatSyn | 275 | 40 | 1 |
| `0x04` | HeartbeatAck | 2 | 40 | 1 |
| `0x64` | Connect | 36 | 103 | 2 |
| `0x65` | Login | 32 | 1250 | 4 |
| `0x67` | MatchStart | 23 | 68 | 1 |

Gerçek trafikte bulunmayanlar: `0x02`, `0x66`, `0x68`.

`0x03` sayaç değerleri: en küçük 1, en büyük 58, 275 örnekte 58 farklı değer. Sayaç bağlantı
başına sıfırlanıyor.

## 16.7 vgc log kodları ve oturum sonları

Servis numaralı log kayıtları yazıyor. Kayıt `191` biçimi `IOCTL kodu ; NTSTATUS`. 62 çözülmüş logda
görülen tek değer:

```
191: 0022C04C ; c0000002
```

Yani çalışma anında istemci tek bir IOCTL kodu gönderiyor (`0x22C04C`), gerçek sürücü bunu
`STATUS_NOT_IMPLEMENTED` ile reddediyor ve istemci devam ediyor. Sürücünün 88 kodluk whitelist'i
ayrı, statik bir yüzey.

Aynı build'de üç farklı oturum sonu:

```
200 : 0 108 286 58 52 54 16 286 90 141 181 91 67 191 155 208×5 70 71 72 71 69 164 79 80 160 …
403 : 0 108 286 58 52 54 16 286 90 141 181 91 67 191 155 208×5 70 71 68 192 16 27 28 286
ölü : 0 108 218 16 27 28 286
```

Ayrışma gateway kayıtlarından sonra (72/68 ve 218). Ölü oturum gateway kayıtlarına hiç ulaşmıyor.

## 16.8 vgk açılış kontrol listesi

Sürücü deterministik 37 adımlı açılış dizisi yazıyor. İki sonuç:

- Bazı adımlar `STATUS_NOT_IMPLEMENTED` (`0xC0000002`) döndürüyor ve istemci devam ediyor; bunlar
  istemci açısından opsiyonel (`0x22C04C` bunlardan biri).
- Servis öldüğünde sürücü logundaki son kayıt aşamayı gösteriyor. Görülen kodlar: `0xC0000365`
  (sürücü girişi başarısız), `0xC0000429` (yetkin değil), bir de temiz çıkış yolu.

Analiz açısından: "sürücü yok" ile "sürücü yüklendi sonra düştü" ayrımı servis durumundan değil,
son kayıt ve çıkış kodundan anlaşılıyor.

## 16.9 Platform hata taksonomisi

Oyun logunda iki farklı hata adı var ve birbirinin yerine kullanılamaz:

| | `SessionRefreshFail` | `VanguardFail` |
|---|---|---|
| olay sayısı | 8 | 6 |
| `Platform Faulted: 5` eşlik ediyor | 8/8, aynı milisaniye | 0/6 |
| ardından `we were kicked` | 3/8 (9–34 ms) | 0/6 |
| öncesinde HTTP hatası | yok | yok |

`VAL 5`'i `SessionRefreshFail` üretiyor. `VanguardFail` ayrı bir yol ve `VAL 5` üretmiyor.
İkisini karıştırmak hangi bileşenin düştüğü konusunda yanlış sonuç veriyor.

## 16.10 Ban zaman çizelgesi yöntemi

Ban anları, kısıtlamayı taşıyan RMS push'unun sunucu zaman damgasından saniye hassasiyetinde
çıkarılabiliyor. Push'u yakalanmış üç vaka kesin; yakalanmamış vakalar "çıkarımsal" işaretli ve
güven gücü düşük.

Kontrol grubu: kimlik doğrulama isteği göndermeyen oturumlarda ban çıkmadı, 3/3.

## 16.11 RTTI envanteri (yöntem referansı)

İstemcinin kullandığı CryptoPP sınıfları için tam type-descriptor / COL / vtable envanteri çıkarıldı
(OAEP varyantları, RSAFunction, GCM_Final, tamsayı ve hash primitifleri). `04-key-recovery.md`
yöntemini yeniden üretilebilir kılan bu: tanımlayıcı sınıfı, COL vtable'ı veriyor, canlı nesne o
vtable işaretçisi aranarak bulunuyor.

Envanter makineye özgü; adresler build ile kayıyor. Kararlı olan tek şey zincir:
isim → TD → COL → vtable → nesne.

## 16.12 vgk log konteyneri ve kayıt kodları

Sürücü logları düz metin değil. Platformun `pvpv` konteynerinde, maskeli RC4 anahtarıyla saklanıyor;
çözücü istemcide bulunuyor. Çözüldükten sonra kayıtlar UTF-16LE satırlar: zaman damgası,
önem derecesi (`[!]` hata, `[i]` bilgi, `[-]` iz) ve sayısal kod.

Tespit analizi için önemli kodlar:

| Kod | İçerik | Anlam |
|---|---|---|
| `B0000041` | `özne ; nesne ; istenen erişim ; verilen erişim` | bir süreç diğerine handle açtı |
| `B000003C` | `pid ; eprocess ; 1 ; 0 ; imaj adı` | süreç oluştu |
| `B000003B` | `pid ; eprocess ; 1 ; 0 ; imaj adı ; çıkış kodu` | süreç bitti |
| `B00000DE` | `adres ; RiotClientServ…` | başlatıcı ile ilgili bildirim |

Sonuç: handle erişim maskeleri süreç çifti bazında kaydediliyor. Anti-cheat servisine tam erişimle
handle açan bir araç, başka hiçbir şey ters gitmese de bu logda görünüyor. Bu bir hipotez değil,
kayıtlı bir iz.

## 16.13 `.riot0` bölümü ve dosya başına RVA eşlemesi

`.riot0` (1,6 MB) şifreli kod değil. Alt bölge entropisi paketli değerin belirgin altında ve içinde
yükleyici yapıları var: istisna dizini, TLS, dışa aktarımlar (`vg`), import tablosu ve IAT. Onu
çözülecek bir yük sanmak sonuç vermiyor.

İkinci tuzak: RVA → dosya ofseti kuralı ikiliye ve bölüme göre değişiyor. Aynı ürünün iki imajı
aynı bölümü farklı ham ofsetlere koyabiliyor; birinden türetilen eşleme diğerinde sessizce bozuk
okuma üretiyor. Okumadan önce her dosyada `VA ≤ RVA < VA + SizeOfRawData` doğrulanmalı
(bkz. `09-methodology.md` §10.2).
