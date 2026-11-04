# Kriptografi

**Türkçe** · [English](../02-crypto.md)

> RSA-OAEP parametreleri, AES-GCM sayaç kuralı, boyut aritmetiği, yanıt çözme.
>
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası.

## 3. Kriptografi

### 3.1 Ölçülen parametreler

| Parametre | Değer |
|---|---|
| Anahtar sarma | RSA-OAEP, SHA-512, MGF1-SHA512, etiket boş |
| Oturum anahtarı | 32 rastgele bayt, istek başına |
| İçerik şifresi | AES-256-GCM, 96-bit nonce, 128-bit tag, **AAD yok** |
| İstemci anahtarı | RSA-2048, açık üs **17**, kuruluma özgü ve kalıcı |
| Sunucu anahtarı | RSA-2048, üs 65537 (bkz. §5) |

### 3.2 GCM sayaç kuralı (sık yapılan hata)

GCM verisi `J0 + 1`'den başlayan akışla şifrelenir:

```
J0        = nonce ‖ 0x00000001
keystream = AES_K(J0+1), AES_K(J0+2), …
```

Pratik sonucu, ilk blok için:

```
AES_K(nonce ‖ 0x00000002) == C[0:16] XOR P[0:16]
```

Sayacı 1'den başlatan hiçbir arama doğru anahtarı bulamaz. Bu hata, çalışma sırasında
tam bir yanlış-negatif nesli üretmiştir; bkz. §9.

### 3.3 OAEP kodlaması (şifreleme yönü)

```
k = 256, hLen = 64 (SHA-512)
lHash   = SHA512("")
DB      = lHash ‖ PS ‖ 0x01 ‖ M        |DB| = k − hLen − 1 = 191
        = 64 + PS + 1 + |M|            ⇒ |PS| = 126 − |M|
seed    = 64 rastgele bayt
maskedDB   = DB   XOR MGF1(seed, 191)
maskedSeed = seed XOR MGF1(maskedDB, 64)
EM      = 0x00 ‖ maskedSeed ‖ maskedDB
c       = EM^e mod n
```

Bazı yayınlanmış örneklerde `|DB| = 223` kullanılır; bu, tamponu 32 bayt taşırır ve sunucunun
ayrıştıramayacağı bir blok üretir. Her denemede çözme hatası vermesi bunu doğrulamıştır.

### 3.4 Yanıtın çözülmesi

Sunucu, istemcinin gönderdiği **aynı** oturum anahtarını istemcinin `f5` alanındaki geçici açık
anahtarıyla geri sarar. Bu nedenle yanıt yalnızca eşleşen özel anahtarla okunabilir; o anahtar da
istemci sürecinde yalnızca alışveriş süresince bulunur.
