# Açık Sorular

**Türkçe** · [English](../10-open-questions.md)

> Çözülmemiş maddeler, geri çekilen iddialar ve sonuçlandırılamayanlar.
>
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası.

## 11. Sınırlar ve açık sorular

### 11.1 Açık sorular (bu dokümanda tahmin edilmemiştir)

1. **p2/p3'ün kaynağı.** Oturumlar arası sabit, okunabilir donanımdan türetilemiyor.
   Aday kaynaklar (çekirdek sürücüsü, TPM) doğrulanmadı.
2. **`htt` ve `gg` türetimi.** Doğrulama kesin (rastgele değerler reddediliyor), formül bilinmiyor;
   ~1,3 milyon yapısal kombinasyon başarısız oldu.
3. **Modül yükünün şifresi.** Statik anahtar değil, basit sarma değil, bilinen bir konteyner değil.
   Düz metin yalnızca anahtarın bulunduğu yerde elde edilebilir.
4. **Sanal bölümün denetim akışı.** Hedefler canlı yazmaç durumuna bağlı; statik çıkarım bu
   tehdit modelinde "zor" değil, **imkânsız** olarak gösterildi.
5. **Oturum ömrü sınırı.** 646 s gözlendi; mekanizma (sunucu tarafı uygulama) izole edilemedi.

### 11.2 Çalışma sırasında geri çekilen iddialar

- *"`expiredTime − lastHeartbeatTime` bir TTL metriğidir."* Geri çekildi: bağlıyken değerler
  atanmamış ya da bayat; metrik bu durumda anlamsız.
- *"`restartRequired` oturum ömrüyle korele."* Geri çekildi: örneklem karışıktı — hayatta kalan
  oturumlar hiç eşleşmeye girmemişti.

Geri çekilen iddiaları kaydetmek yöntemin parçasıdır: üzerlerine bina yapılmasını önler.

### 11.3 Sonuçlandırılamayan

Bu doküman, kalıcı ve yasaksız bir oturum elde etmenin yolunu göstermez. Ölçümler tersini
işaret eder: kimlik doğrulama, kullanıcı modu dışında üretilen bir kanıta karşı doğrulanır ve
isteği göndermek kendi başına tespit edilen ve uygulanan bir sinyaldir.
