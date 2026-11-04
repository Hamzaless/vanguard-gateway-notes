# Negatif Sonuçlar

**Türkçe** · [English](../08-negative-results.md)

> Ölçek bilgisiyle birlikte yirmi çürütülmüş hipotez.
>
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası.

## 9. Negatif sonuçlar

Bunları kaydetmek tekrar eden emeği önler.

| # | Hipotez | Test ölçeği | Sonuç |
|---|---|---|---|
| N1 | Sunucu anahtarı bir yerde düz metin olarak duruyor | 340+ aday, 4 padding varyantı | hepsi 400 |
| N2 | Oturum anahtarı bellekte kalıyor | 35,4 GB RAM + 2,89 GB süreç dökümü | bulunamadı |
| N3 | `htt`/`gg` türetilebilir | ~1,3 M kombinasyon | eşleşme yok |
| N4 | `htt`/`gg` doğrulanmıyor | geçerli token + rastgele değer | reddedildi (400) |
| N5 | Modül yükü statik anahtar kullanıyor | 4 ikili üzerinde ~4,6 milyar deneme | eşleşme yok |
| N6 | Modül yükü sarmalanmış anahtar | 215 milyon deneme | eşleşme yok |
| N7 | Modül yükü PE olarak ayıklanabilir | 11,3 GB döküm | 315 PE, modül yok |
| N8 | Sanal bölümün CFG'si statik çıkarılabilir | 5 bağımsız yöntem | çıkarılamıyor |
| N9 | Lifter blokları sentetik durumla çalışır | 400 blok | 7 erişimde hata |
| N10 | Dağıtıcı GF(2) üzerinde afin | 960 birim vektör + 32 rastgele çift | afin değil |
| N11 | Dağıtıcı `ret` gibi davranıyor | 17.310 yığın örneği | 0 eşleşme |
| N12 | Blok içi sabit yayılımı hedefleri çözer | 32.605 dolaylı atlama | 0 çözüldü |
| N13 | Sanal kod 33 GB fiziksel dökümde bulunur | tam tarama | 0 imza |
| N14 | Yüksek entropili bölgeler şifreli sırdır | 3.744 blok, 7 şifre × 12 anahtar | eşleşme yok |
| N15 | Ağ geçidi oturumu uzatılabilir | auth + access + heartbeat hepsi 200 | oturum yine kapandı |
| N16 | Oturum dışarıdan yenilenebilir | heartbeat / disconnect / connect | 403 `NONSELF_OPERATION`, 404 |
| N17 | Görev kimliği anahtar tohumudur | 7/7 ölçüm | hayır — CRC32 |
| N18 | Hosts dosyası yönlendirmesi çalışır | 127.0.0.1 | istemci yok saydı |
| N19 | Sistem proxy yönlendirmesi çalışır | 8080 | tünel kullanılmadı |
| N20 | TLS anahtar günlüğü oyun TLS'ini kapsar | 93 sır / 779 el sıkışma | 0 kesişim |
