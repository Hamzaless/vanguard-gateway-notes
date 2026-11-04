# RMS — oturum taşıyıcısı

**Türkçe** · [English](../13-rms.md)

> RMS nedir, neyi taşır, oturum ömrü için neden önemlidir.
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası. Savunma amaçlı araştırma.

## 13.1 Nedir

RMS (Riot Messaging Service), platform durumunu istemciye taşıyan bir **WebSocket push** kanalıdır.
Anti-cheat ağ geçidi değildir; oturum/parti durum değişikliklerinin geldiği taşıyıcıdır.

```
wss://<bölge>.edge.rms.si.riotgames.com/rms/v1/session?token=<token>
```

İstemci açılışta soketi açar, kaynak öneklerine abone olur ve JSON zarfları alır.

## 13.2 Zarf

```json
{"payload": {"resource": "ares-session/v1/sessions/<oyuncu>",
             "service":  "session",
             "timestamp": 1793819627653,
             "payload":  "<kaçışlı JSON dizesi>",
             "version":  "5"},
 "ts": 1793819627.653, "subject": "rms:message", "type": "push"}
```

İç `payload` **kaçışlı bir JSON dizesidir**; naif grep araçları bunu kaçırır çünkü log satırında
tırnaklar ters bölüyle kaçışlıdır.

## 13.3 Neler gelir

| Kaynak | Anlam |
|---|---|
| `ares-session/v1/sessions/<id>` | oturum durumu (`CONNECTED`/`CLOSED`), kalp atışı, loop state |
| `ares-parties/parties/v1/parties/<id>` | parti üyelik değişiklikleri |
| `ares-parties/players/<id>` | oyuncu eklendi/çıkarıldı |
| `ares-core-game/core-game/v1/matches/<id>` | maç yaşam döngüsü |

Çalışılan oturumlarda yalnız ilk ikisinin değiştiği gözlendi.

## 13.4 Gözlenen zaman çizelgesi

```
714.851  RMS: ares-core-game … matches/<id>
714.855  RMS: ares-session … serviceState = CONNECTED
715.499  product-session: Gameplay → Idle          (393 s oyundan sonra)
738.202  RMS: ares-parties/parties/v1/parties/<id>
738.930  RMS: ares-session … serviceState = CLOSED
738.933  RMS: ares-parties/players/<oyuncu>        (partiden çıkarıldı)
769      oyun: "Platform Faulted: 5 / SessionRefreshFail"
```

Oturumu **sunucu** kapattı: oyundan çıkıştan ~24 s sonra. Parti 3 ms sonra temizlendi, oyun
30 s sonra hatayı bildirdi.

## 13.5 RMS'in taşımadığı

Gözlenen tüm oturum push'larında payload içinde **Vanguard alanı, attestation sonucu veya
anti-cheat durumu yoktu**:

```
"isRestricted": false, "restrictionType": "", "shouldForceInvalidate": false
```

Kısıtlama/attestation durumu ayrı katmandadır (launch restriction / gateway).

## 13.6 Pinleme

Oyun binary'sinde `PinnedPublicKeys` mekanizması vardır; ancak yapılandırmada gözlenen tek host
paylaşılan config uç noktasıdır. RMS hostu için pin girdisi bulunmadı. Bu **statik bir gözlem**dir,
canlı test değildir; "RMS pinli değil" varsayımı doğrulanmamıştır.

## 13.7 Neden önemli

- Oturum, kalp atışı kaçtığı için ölmüyor (ölçüm: kapanıştan 22 s önce son HB, aralık 60 s).
- Sunucu `CLOSED` push'u gönderdiği için ölüyor.
- Yani soketi "sağlıklı" tutmak tek başına yetmiyor; platformun istemciyi uygun görmesi gerekiyor.
  Bu uygunluğa gateway/launch-restriction katmanı karar veriyor.
