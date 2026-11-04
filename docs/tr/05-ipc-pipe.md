# IPC (Pipe)

**Türkçe** · [English](../05-ipc-pipe.md)

> 26 baytlık IPC çerçevesi, mesaj tipleri, kimlik yanıtı aritmetiği, heartbeat, sağlık kontrolü.
>
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası.

## 6. IPC protokolü (anti-cheat SDK)

### 6.1 Taşıma ve çerçeveleme

Oyun ile anti-cheat servisi, sabit GUID'li bir isimli boru (named pipe) üzerinden konuşur.

```
[u32 tip][u32 toplam][u16 alan_sayısı][16 × 0x00]      = 26 baytlık başlık
tekrar: [u16 tag][u32 uzunluk][veri]                   = 6 + uzunluk

toplam = 26 + Σ(6 + uzunluk)
```

Bu model yakalanan mesajların **62/62**'sinde tuttu. Yaygın dolaşan 36 ve 40 baytlık başlık
modelleri **0/62** tuttu.

### 6.2 Mesaj tipleri

| Tip | Anlam | Yanıt |
|---|---|---|
| `0x02` | Bağlantı kesme (u32 kod) | yok |
| `0x03` | Heartbeat isteği | `0x04` (40 B) |
| `0x04` | Heartbeat yanıtı | — |
| `0x64` | Kimlik doğrulama isteği | `0x65` (1250 B) + `0x09` (40 B) |
| `0x65` | Kimlik doğrulama yanıtı | — |
| `0x67` | Eşleşme başlangıcı (68 B) | yok |
| `0x69` | Sağlık kontrolü (36 B) | `0x3EB` (36 B) |
| `0x66`, `0x68` | bu istemci sürümünde **yok** | — |

### 6.3 Kimlik doğrulama yanıtı (`0x65`)

| Alan | Tag | Uzunluk | İçerik |
|---|---|---|---|
| 1 | 0 | 36 | oyuncu kimliği |
| 2 | 1 | 1106 | erişim anahtarı (JWT) |
| 3 | 2 | 22 | ürün kimliği |
| 4 | 3 | 36 | oturum kimliği |

`26 + 4×6 + 36 + 1106 + 22 + 36 = 1250`.

Yanıttan hemen sonra 40 baytlık `0x09` "oturum doğrulama" mesajı gönderilir.

### 6.4 Heartbeat semantiği

Yanıt, istekteki 8 baytlık sayacı aynen yansıtır (58/58 örnekte doğrulandı). Sabit değer
döndürmek, sayacı doğrulayan istemcilerde sessiz protokol kaymasına yol açar.

### 6.5 Sağlık kontrolü (`0x69` → `0x3EB`)

İstemci binary'sinde tek alan bekleyen bir işleyici vardır: `tag 0, uzunluk 4, neden maskesi`.
`maske == 0` "başarılı", aksi hâlde "başarısız" anlamına gelir. İstek ve yanıt 36 bayttır
(istek alan değeri olarak `0xFFFFFFFF` taşır).

### 6.6 Döküm üzerinde çerçeve taraması

İki süreç dökümü 26 baytlık doğrulayıcı ile tarandığında yalnızca şunlar bulundu:

```
0x02 total=26 alan=0 · 0x03 total=26 alan=0 · 0x04 total=26 alan=0
```

İstemci belleğinde `0x65`/`0x66`/`0x67` şablonu yoktur; `0x65` yalnızca servis → oyun
yönünde üretilir.
