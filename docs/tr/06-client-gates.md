# İstemci Kapıları

**Türkçe** · [English](../06-client-gates.md)

> Yeniden başlatma formülü, vgrl ordinal'ları, Riot ID kapısı, ürün oturumu.
>
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası.

## 7. İstemci bağımlılık kapıları

### 7.1 "Yeniden başlatma gerekli"

Disassembly iki dal gösterir:

```
özellik bayrağı KAPALI:
    restartRequired = (vgk.StartType == SYSTEM_START) && (vgk.State != RUNNING)

özellik bayrağı AÇIK:
    restartRequired = (VgrlQueryInstallStatus() == 2)
```

Değer, çağrı yerinde hesaplanmaz; bağımlılık eklentisinin durumundan **kopyalanır**
(`[rbp+0x171] → çıktı[0x1a1]`). Bu nedenle yamanacak bir karşılaştırma yoktur; yalnızca
girdiler tutarlı hâle getirilebilir.

### 7.2 `vgrl` ordinal sözleşmesi

Dışa aktarım tablosunda `NumberOfNames = 0`; çağrılar ordinal ile yapılır.

| Ordinal | Anlam | Dönüş değerleri |
|---|---|---|
| 1342 | kurulum durumu | 0 hata · 1 kurulu değil · **2 kurulu** |
| 1343 | hata metni | dize |
| 1344 | servisi başlat | bool |
| 1345 | yeniden başlatma muafiyeti | bit0 talep üzerine · bit1 güvenli sistem · bit2 yeni kurulum · bit3 açılışta |
| 1346 | önyükleme damgasını sıfırla | bool |

### 7.3 Riot ID kapısı

Etkin bir Riot ID yoksa oyunun başlatılması **HTTP 467** (`riot_id_required`) ile reddedilir.
İstemci binary'sinde bu kontrolü atlayan bir geliştirici bayrağı bulunur
(`--developer-skip-riot-id`); varlığı bir olgudur, kullanımı bu dokümanın kapsamı dışındadır.

### 7.4 Ürün oturumu

```
POST /product-session/v1/sessions
POST /product-session/v2/heartbeat/{id}
POST /product-session/v2/heartbeat-internal/{id}
POST /product-session/v1/session-heartbeats/{id}
POST /product-session/v1/external-sessions/{id}
GET  /product-session/v1/host-session/id
GET  /product-session/v1/data/path/<patchline>
```

Heartbeat aralığı 60 s'dir. `product-session.<ürün>.300_sec.windows` dizesi 300 saniyelik bir
üst sınıra işaret eder.

### 7.5 Oturum nesnesi

Platform oturum nesnesi 23 alana sahiptir. İkisi sık yanlış okunur:

- `expiredTime` güvenilir bir TTL **değildir**: bağlıyken ya `0001-01-01` (atanmamış) ya da
  önceki bağlantıdan bayattır; bu yüzden `expiredTime − lastHeartbeatTime` negatif çıkabilir.
  Ölçülen gerçek oturum ömrü: **646 s**.
- `isRestricted`, `restrictionType` ve `shouldForceInvalidate` ayrı bir katmandadır; oturum
  nesnesi kısıtlama durumunu taşımaz.

### 7.6 Başlatma parametreleri (süreç belleğinden, düz metin)

```
-remoting-app-port=<port> -remoting-auth-token=<32 karakter>
-patchline=live -subject=<oyuncu kimliği> -ares-deployment=<bölge>
-config-endpoint=https://shared.<bölge>.a.pvp.net
-savetouserdir -culture=<yerel ayar>
-riotgamesapi-settings-token=<base64(JSON)>
```

Settings token'ı, oyunun kendi `valorant-client` anahtarını aldığı OAuth **yetkilendirme kodu ve
PKCE doğrulayıcısını** içerir:

```json
{"rso_auth":{"authorization-key":"<b64({code, code_verifier})>"},
 "riotclient":{"app-port":"50900","auth-token":"<32 karakter>"},
 "product-integration":{"heartbeat":"…heartbeat.json","lockfile":"…","settings":"…"}}
```

Token alışverişi: `grant_type=authorization_code&code=…&code_verifier=…&client_id=valorant-client`.
Kodlar tek kullanımlıktır; yakalanmış bir kod tekrar kullanıldığında `401 invalid_grant` döner
(doğrulandı).
