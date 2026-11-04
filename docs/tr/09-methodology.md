# Metodoloji

**Türkçe** · [English](../09-methodology.md)

> Teknikler, doğrulama kuralı, adres hiyerarşisi, ofset aritmetiği.
>
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası.

## 10. Metodoloji

| Teknik | Kullanım |
|---|---|
| Statik analiz | bölüm haritalama, RTTI/type-descriptor çıkarımı, RVA→dosya ofseti, disassembly |
| Dinamik enstrümantasyon | emülasyon, sembolik yürütme (SMT), komut izleme |
| Bellek adli analizi | fiziksel RAM görüntüsü, süreç bellek haritası, sayfa tablosu yürüyüşü |
| Protokol testi | kontrollü "oracle" istekleri, durum kodu ayrımı |
| Ağ gözlemi | TLS anahtar günlüğü, paket yakalama, yerel yönlendirme |
| Diferansiyel test | üretilen kod ile referans yürütücü arasında durum karşılaştırması |

**Çalışma boyunca uygulanan doğrulama kuralı:** her iddia iki bağımsız yöntemle desteklenir ve
bir ölçüm iddiayı çürütürse iddia geri çekilir. Geri çekilmiş iki örnek §11'de kayıtlıdır.

### 10.1 Adres doğrulama hiyerarşisi

```
1. gerçek istisna dizini (.pdata eşdeğeri) — tam eşleşme
2. çalışma anı yürütme izi — çağrı gerçekten oraya gidiyor mu
3. RTTI zinciri (TD → COL → vtable → canlı vptr)
4. çapraz referans (RIP-göreli) — tek başına zayıf
5. byte imzası — yalnızca arama için, doğrulama için asla
```

### 10.2 Ofset aritmetiği (en pahalı hata)

Sanal bölümde `RVA == dosya ofseti` **değildir**:

```
.grfn1: VirtualAddress = 0x5EB000 , PointerToRawData = 0x5DC600 , Δ = 0xEA00
doğru: ofset = PointerToRawData + (RVA − VirtualAddress)
yanlış: ofset = RVA            → 0xEA00 kaydırılmış baytlar, "desenkron" görünen çöp
```

Bir bölümü `VA ≤ RVA < VA + SizeOfRawData` kontrolü olmadan okumak, sessizce makul görünen
anlamsız veri üretir; katı kontrol zorunludur.
