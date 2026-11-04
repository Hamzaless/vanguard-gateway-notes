# Protokol

**Türkçe** · [English](../01-protocol.md)

> Tel protokolü: uç noktalar, başlıklar, çerçeve, zarf, mesaj tipleri.
>
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası.
> Savunma amaçlı araştırma; kapsam ve hukuki not için depo README'sine bakın.

## 2. Protokol

### 2.1 Uç noktalar

```
POST https://<bölge>.vg.ac.pvp.net:8443/vanguard/v1/gateway
POST https://<bölge>2.vg.ac.pvp.net:443/vanguard/v1/gateway
GET  https://config.vg.ac.pvp.net/config/production.rito
```

İki kenar dağıtımı kullanılır: 8443'te CDN tabanlı, 443'te bulut sağlayıcı üzerinde.
Bu ortamda gözlenen kimlik doğrulama trafiği ikincisine gitmiştir.

### 2.2 İstek başlıkları

```http
User-Agent: vanguard/<sürüm>
Content-Type: application/x-protobuf
Accept: */*
X-VG-1: <aksiyon>          # 3 = auth, 4 = access, 7 = heartbeat, 9 = task result
X-VG-2: <oyuncu kimliği>
X-VG-3: 1
X-VG-4: <ürün kimliği>     # bazı aksiyonlarda bulunur
Content-Length: <n>
```

### 2.3 Çerçeve

```
08 <tip> 12 <varint uzunluk> <zarf> 18 01
```

Ölçülen örnekler: istek `f1=3, f2=2971, f3=1`; yanıt `f1=5, f2=8204`.

### 2.4 Zarf

| Ofset | Boyut | Alan |
|---|---|---|
| 0 | 4 | sihir `52 47 01 00` (`RG\x01\x00`) |
| 4 | 256 | RSA bloğu (2048-bit, OAEP-SHA512) |
| 260 | 12 | nonce |
| 272 | n | AES-256-GCM şifreli metin |
| 272+n | 16 | GCM tag |

Doğrulanmış boyut özdeşliği: 2683 baytlık düz metin için `4 + 256 + 12 + 2683 + 16 = 2971`.

### 2.5 Mesaj tipleri

| Tip | Anlam | Yanıt |
|---|---|---|
| 3 | AuthenticationRequest | 5 (TokenResponse) |
| 4 | AccessRequest | 4 (TokenResponse) |
| 7 | Heartbeat | 8 (HeartbeatResponse) |
| 9 | TaskResult | 11 (ack) |
