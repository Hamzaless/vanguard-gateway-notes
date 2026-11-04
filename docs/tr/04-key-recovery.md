# Anahtar Kurtarma

**Türkçe** · [English](../04-key-recovery.md)

> Sunucu açık anahtarının canlı süreçten çıkarılması; oracle ile doğrulama.
>
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası.

## 5. Sunucu açık anahtarının kurtarılması

### 5.1 Neden gerekli

RSA bloğu, rastgele 32 baytlık oturum anahtarını **sunucunun** açık anahtarıyla sarar.
Bu anahtar olmadan, düz metin ne olursa olsun biçimsel olarak geçerli bir istek üretilemez.

### 5.2 Yöntem (sürümden bağımsız)

1. `.rdata` içindeki C++ RTTI type descriptor'ları listelenir
   (`OAEP<SHA1>`, `OAEP<SHA512>`, `RSAFunction`, `GCM_Final`).
2. Her TD, **Complete Object Locator**'a çözülür (TD RVA'sına işaret eden DWORD).
3. COL'e işaret eden **vtable** bulunur.
4. Canlı süreç dökümünde bu vtable değeri (nesnenin `vptr`'si) aranır.
5. CryptoPP nesne yerleşimi okunur:

```
+0x00  vptr
+0x28  modulus kelime sayısı      +0x30  modulus işaretçisi
+0x58  üs kelime sayısı           +0x60  üs işaretçisi
```

6. `(n, e)` PEM'e çevrilir ve oracle ile doğrulanır.

### 5.3 Doğrulama

| Aday nesne | Üs | Oracle | Yorum |
|---|---|---|---|
| A | 65537 | **401** | zarf kabul edildi, kimlik reddedildi ⇒ doğru anahtar |
| B | 17 | 400 | zarf açılamadı ⇒ istemci anahtarı |

400 "çözemedi/ayrıştıramadı", 401 "çözdü, reddetti" demektir. Bu ayrım iki farklı bölgesel
uç noktada yinelenmiştir.

> RTTI ve vtable adresleri her sürümde kayar; yukarıdaki yöntem kaymaz.
