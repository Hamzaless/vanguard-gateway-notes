# Arşiv bulguları: düzeltmeler, anti-debug, log dilbilgisi

**Türkçe** · [English](../17-archive-findings.md)

> Kalan proje notlarından çıkanlar: yanlış çıkan kabuller, `.riot0` kapsama ölçümleri,
> anti-debug envanteri ve log satır dilbilgisi.
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası. Yalnız savunma amaçlı araştırma.

## 17.1 Yanlış çıkan kabuller

Tekrar edilmemesi için kayıtlı:

| Kabul | Ölçüm |
|---|---|
| `.riot0` şifreli VM verisi | kod ve yükleyici verisi; alt bölge entropisi düşük, 7,3 üstünde 4 KiB pencere yok |
| `.grfn1` `.riot1`'i 496 kez çağırıyor | sayı ham `E8` bayt deseninden geliyordu; doğrulama sonrası doğrudan çağrı sayısı 0 |
| IAT slotlarını lifted kod yazıyor | slotlar 46 sitede yalnızca okunuyor; hepsi `.grfn1` içinde, yazan bölge yok |

## 17.2 `.riot0` kapsaması

```
alt bölge entropisi  başlık 0.854 · istisna dizini 7.170 · kuyruk tablo 0.476
4 KiB dağılımı       ortalama 4,94 · min 0,000 · max 7,013
                     H<3: 31 blok · 3–6,5: 82 blok · >6,5: 25 blok
yüksek entropi (>7,3) pencere: 0     -> bölüm içinde şifreli blob yok
```

Çeviri kapsaması:

```
9.834 blok   477.799 bayt = %29,4   (üç tur, örtüşen tohumlar)
49.095 blok  582.038 bayt = %35,8   (monoton, çakışmasız)
tohum: 78.799 iç dal hedefi + 10.297 -> 89.096
not: .riot0'da istisna dizini yok; doğrusal tarama gürültülü
```

`.riot0`'dan ulaşılan ilk `.text` hedefi: `0x35B838` (normal kod, kripto değil).

## 17.3 Anti-debug envanteri

`.pdata` ile doğrulanmış fonksiyon sınırlarında ölçüldü:

| Primitif | Sayı |
|---|---|
| `int 2d` | 0 |
| tespit amaçlı `int 3` | 0 |
| `KUSER_SHARED_DATA.KdDebuggerEnabled` okuması (`0x7ffe02d4`) | bulunan tek gerçek tespit primitifi |
| `rdtsc` | 378 (sürücüde) |
| `cpuid` | 226 |
| `xgetbv` | 1 |

Sonuçlar:

- Klasik debugger tuzakları yok. Anti-debug maliyeti ikilide değil.
- Zaman ve CPUID kullanımı yoğun; emülasyon için `rdtsc`/`rdtscp`, `cpuid` (yaprak tablosu ve
  hypervisor biti temiz) ve `xgetbv` doğru uygulanmalı. Çalışan bir Unicorn koşusu için toplam
  yedi stub gerekti.
- Statik analiz için bunların hiçbiri engel değil: debugger bağlanmadıkça tetiklenmiyor.

## 17.4 Log satır dilbilgisi

Servis logları `pvpv` konteynerinde UTF-16LE satırlar. Çözüldükten sonra dilbilgisi:

```
[<pid>][<AA/GG/YY SS:DD:SS>][<seviye>]: <kod>: <alanlar " ; " ile>
```

Örnek:

```
[16948][10/17/26 13:18:15][i]: 141: eu.vg.ac.pvp.net:8443;eu2.vg.ac.pvp.net:443
```

Görülen seviye karakterleri: `[i]` bilgi, `[!]` hata, `[-]` iz. Kod küçük bir tamsayı; alan sayısı
ve anlamı koda göre değişiyor (proje notlarında 60 kod kataloglu). Kayıt `191` `IOCTL kodu ; NTSTATUS`
taşıyor, kayıt `141` gateway uç listesini.

Zaman damgaları yerel saat; başka loglarla korelasyon için aynı saat ve saat dilimi gerekir.

## 17.5 Bu neyi ekliyor

- Önceki notlardaki üç kabul açıkça çürütüldü; ikisi kodun nerede durduğu ve IAT değerlerinin
  nereden geldiğiyle ilgiliydi.
- `.riot0` şifreli yük içermiyor; %35,8 kapsama bir ölçüm, çaba sınırı değil.
- Bu ikilide anti-debug engel değil; engel zaman ve CPUID stub'ları.
- Konteyner çözüldükten sonra log ayrıştırma mekanik; yukarıdaki dilbilgisi parser yazmaya yetiyor.

## 17.6 Zarf protobuf'u ve başlık eşleşmesi

Gövde kendisi protobuf ve alan numaraları biliniyor:

```
Envelope {
  1: uint32  message_type
  2: bytes   zarf baytları     ("RG\x01\x00" | RSA | nonce | şifreli metin | tag)
  3: uint32  1                 (opsiyonel kuyruk; sunucu yokluğunu da kabul ediyor)
}
```

Boyut örneği: gövde `2960 B` = `08 03` (2) + `12 89 17` (3) + `2953` + `18 01` (2) ve
`2953 = 4 + 256 + 12 + 2665 + 16`. Aynı aritmetik 2683 baytlık düz metinle 2971 veriyor; ikisi de
gözlendi, fark yalnızca düz metin uzunluğu.

Başlık eşleşmesi, ikisi de test edildi:

| Başlık | Kural |
|---|---|
| `X-VG-1` | zarfın `message_type` değerine eşit olmalı; uyuşmazsa **400** |
| `X-VG-2` | kimlik doğrulama için **gerekli değil**; gönderilmemesi sonucu değiştirmiyor |
| `X-VG-3` | sabit `1` |

Padding kanıtı: sızdırılmış uygulama `BCRYPT_OAEP_PADDING_INFO.pszAlgId` alanını
`BCRYPT_SHA512_ALGORITHM` yapıyor; oracle'ın kabul ettiği SHA-512 padding ile uyuşuyor.

Tip numaralandırması düzeltmesi: "AUTH = 1, ACCESS = 3" yanlış. Doğrulanmış değerler AUTH = 3,
ACCESS = 4, heartbeat = 7, cevap = 5. Kayıtlarda iki değer daha göründü: boş/keepalive olarak `10`
ve tek bir bootstrap benzeri mesajda `1` (288 baytlık zarf); rolü doğrulanmadı.

## 17.7 İki ayrı heartbeat formatı (düzeltme)

Sızdırılmış kaynaklarda iki ilgisiz heartbeat kurucusu var. Farklı kanallara aitler ve tek şemada
birleştirilmemeli:

| Kaynak | Kanal | Alanlar |
|---|---|---|
| `EncodeHeartbeatRequest` | gateway HTTP | `f1` token, `f2` zaman, `f4 = 1`, `f5` ×2, `f6 = 1` — başka alan yok |
| `…WithTasks` | gateway HTTP | yukarıdakiler + `f7` görevler, `f12` modül ×3, `f16 {f1=1, f2=0}` |
| `heartbeat_payload` (referans emülatörde) | **sürücü IOCTL yanıtı** (`0x22C034`) | bayt odaklı, protobuf değil: `0x0C`/`0x10` düz yazılıyor, uzunluklar big-endian; `f16 = {eph, secret16, htt}` yalnız burada |

Bu çalışma için sonucu: canlı testlerde kullanılan heartbeat isteği iki sızdırılmış kurucudan da
farklı bir alan kümesi taşıyordu ve yine de kabul edildi (200). Yani kabul, alan kümesini kanıtlamıyor;
yalnızca cevap ayrıştırma tam olarak gözleme dayanıyor.

## 17.8 Oyun logu koşu istatistikleri

On bir yakalanmış istemci koşusu tablolandı (yalnız süreler, kimlik yok):

| Metrik | Değer |
|---|---|
| koşu süresi | 33 s … 210 s |
| ana menüye ulaşan | 11'de 1 |
| oyun içi duruma ulaşan | 11'de 1 |
| ilk hata | çoğunda `VanguardFail`, bazılarında `SessionRefreshFail` |
| oturum bağlantısından ilk hataya | 3 s … 190 s |

Okuma: yerel parçalar tutarlıyken istemci menüye ve oyuna ulaşabiliyor, ancak platform oturumu kısa
süre sonra düşüyor. Bu, §16.9'daki iki hata adının ayrı olduğu gözlemiyle tutarlı.
