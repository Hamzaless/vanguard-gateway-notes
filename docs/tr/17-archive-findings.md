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
