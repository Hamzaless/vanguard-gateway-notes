# Yeniden Üretilebilirlik

**Türkçe** · [English](../11-reproducibility.md)

> Ölçümleri yeniden üretmek için işletim notları.
>
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası.

## 12. Yeniden üretim notları

- Oracle sonuçları yalnızca durum kodundan okunur; yan etkisi yoktur.
- Protokol testleri tek bağlantıda sıralı yapılmalıdır; eşzamanlı bağlantılar sayaç yansıtma
  davranışını bozar.
- Fiziksel bellek görüntüleri, hedef süreç **etkinken** alınmalıdır; aksi hâlde sanal sayfalar
  dökümde bulunmaz (doğrulandı: 33 GB'lık görüntüde 0 imza).
- Her anahtar aramasında GCM sayaç kuralı (`J0+1`) uygulanmalıdır; aksi hâlde doğru anahtar elenir.
- Adres eşlerken okumadan önce bölüm aralığını doğrulayın (bkz. §10.2).
