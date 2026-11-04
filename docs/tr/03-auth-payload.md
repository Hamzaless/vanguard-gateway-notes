# Kimlik Doğrulama Yükü

**Türkçe** · [English](../03-auth-payload.md)

> Alan haritası, cihaz kimliği yerleşimi, bütünlük alanı, güvenlik bayrakları.
>
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası.

## 4. Kimlik doğrulama yükü

### 4.1 Alan haritası

| Alan | İçerik | Ölçülen boyut |
|---|---|---|
| f1 | cihaz kimliği (`‖1;…‖6;`) | 895 B |
| f2 | işletim sistemi bilgisi (platform, mimari, sürüm) | 16 B |
| f4 | RSO erişim anahtarı (JWT) | 1106 karakter |
| f5 | istemci geçici açık anahtarı (SPKI base64) | 398 karakter (DER 292 B) |
| f6 | istemci sürümü `{1,19,1,18}` | 8 B |
| f7 | aynı sürüm bloğu | 8 B |
| f8 | ürün kimliği | 22 B |
| f9 | önyükleme durumu (varint 3) | 1 B |
| f13 | harici oturum kimliği (UUID) | 36 B |
| f14 | güvenlik bayrakları (5 giriş) | — |
| f15 | bütünlük haritası: `htt`, `ht`, `gg` | 3 giriş |

Toplam serileştirilmiş boyut: **2683 bayt**.

Not: `f10` (bir "geçici kimlik") bu istemci sürümünde **yoktur**, bazı yazılarda geçer.
Alan sırası byte eşitliği için önemlidir.

### 4.2 Cihaz kimliği yerleşimi

```
"‖1;<b64>‖2;<b64>‖3;<b64>‖4‖5;<b64>‖6;<b64>;<b64>;<b64>;<b64>;<b64>"
```

| Parça | Ham boyut | Kodlama | Kaynak (donanımla doğrulandı) |
|---|---|---|---|
| p1 | 16 B | 24 karakter | SMBIOS UUID (GUID little-endian) |
| p2 | 64 B | 88 karakter | **kaynağı belirlenemedi** (oturumlar arası sabit) |
| p3 | 64 B | 88 karakter | **kaynağı belirlenemedi** (oturumlar arası sabit) |
| p4 | 0 B | — | boş ayırıcı |
| p5 | 6 B | 8 karakter | varsayılan ağ geçidi MAC adresi |
| p6 | 5 × 97 B | 5 × 132 karakter | disk serisi + model, sıfır dolgulu |

Uzunluk özdeşliği: `4+24 + 4+88 + 4+88 + 3 + 4+8 + 4+664 = 895`.

p2/p3, 42 donanım/OS değerinin 234.234 hash kombinasyonuna karşı denendi (SHA-512, SHA3-512,
BLAKE2b, HMAC-SHA512, çift SHA-512, farklı ayırıcılar). Eşleşme yok. Dolayısıyla sabitler,
ancak okunabilir donanım değerlerinden türetilemiyorlar.

### 4.3 Bütünlük alanı `ht`

```
girdi = "6;" + p6 + "1;" + p1 + "2;" + p2 + "3;" + p3 + "5;" + p5 + sürüm + MAGIC
ht    = Base64( SHA1(girdi) )            # 20 bayt → 28 karakter

MAGIC = F4 AD 52 9C DE 17 0E E1 D1 02 9B 4A 3C A8 98 20      (16 ham bayt)
```

Sabit **16 ham bayt** olarak kullanılmalıdır. 32 karakterlik hex temsili farklı bir özet üretir;
bu ayrım formülün doğrulanmasında kullanılan testlerden biriydi.

### 4.4 Güvenlik bayrakları (f14)

Beş giriş, değerler 0/1. Kaynak, tepsi bileşeninin yazdığı `vgtray-settings.json` dosyasıdır;
her özelliğin "başlangıçta eksik miydi" bilgisini tutar (HVCI, IOMMU, TPM 2.0, VBS, Secure Boot).
Aynı makinede canlı registry farklı değerler verdiği için dosya daha güvenilir kaynak sayılmıştır.
