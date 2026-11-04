# Tespit

**Türkçe** · [English](../07-detection.md)

> Yaptırım sınıflandırması ve ölçülen zamanlama (örneklem büyüklüğü uyarısıyla).
>
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası.

## 8. Tespit ve yaptırım

### 8.1 Sınıflandırma

Hesap durumu RSO `userinfo` uç noktasından okunur:

```
TIME_BAN       reason=THIRD_PARTY_TOOLS  scope=<ürün>   14 gün
PERMANENT_BAN  reason=THIRD_PARTY_TOOLS  scope=<ürün>   kalıcı
```

İstemcinin kendi yerelleştirme kataloğu tüm taksonomiyi içerir; burada `VANGUARD_BYPASS`
`THIRD_PARTY_TOOLS`'tan **ayrı** bir kategoridir.

### 8.2 Nedensellik ölçümü

| Gözlem | Sonuç |
|---|---|
| Cezanın veriliş zamanı (bitiş − 14 gün) | kimlik doğrulama denemeleriyle aynı dakika |
| Kimlik doğrulama isteği gönderen hesaplar | 8/8 yasaklandı, +0,5 s … +2,7 s |
| Hiç göndermeyen oturumlar | 3/3 etkilenmedi |

**Uyarı:** bunlar tek ortamdan alınmış küçük örneklemlerdir (8 ve 3). "Kimlik doğrulama isteği
tek başına yeterlidir" hipotezini destekler; genel popülasyon için bir oran kanıtlamaz.

### 8.3 Gözlenebilir istemci izleri (ölçüldü, çıkarım değil)

| İz | Kanıt |
|---|---|
| Servis tanımında standart dışı dizini gösteren ortam değişkeni | registry'deki `Environment` değeri |
| Makine geneli `SSL_CERT_FILE` / `SSL_KEYLOGFILE` benzeri değişkenler | Riot süreç ortam bloğunda mevcut |
| Servis ikilisinde sürüm kaynağı olmaması | istemci `0.0.0.0` okuyor |
| Çekirdek sürücüsünün imza kataloğunda bulunmaması | istemci log satırı |
| Cihaz kimliğinin kullanıcı modunda bulunmayan bir sırdan türetilmesi | §4.2 |

Bunlar, bir tespit sisteminin çekirdek enstrümantasyonu olmadan gözleyebileceği izlerdir.
