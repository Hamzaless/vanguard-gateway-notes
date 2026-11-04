# Özet

**Türkçe** · [English](../00-summary.md)

## 1. Özet

### 1.1 Doğrulanmış bulgular

| # | Bulgu | Nasıl doğrulandı |
|---|---|---|
| F1 | Dış çerçeve `08 <tip> 12 <uzunluk> <zarf> 18 01` | 12 bağımsız oturum kaydı |
| F2 | Zarf = `RG\x01\x00` ‖ RSA-OAEP-SHA512(32 B anahtar) ‖ 12 B nonce ‖ AES-256-GCM ‖ 16 B tag | çözme + yeniden şifreleme gidiş-dönüşü |
| F3 | GCM veri akışı `J0+1`'den başlar (sayaç = 2, 1 değil) | sentetik vektör + gerçek düz metin |
| F4 | Kimlik doğrulama yükü 11 alanı dolu bir protobuf mesajı | düz metnin tamamı süreç belleğinden alındı |
| F5 | Cihaz kimliği 6 parçalı `‖1;…‖6;`; parçalar gerçek donanıma karşılık geliyor | UUID / yönlendirici MAC / disk serisi eşleşti |
| F6 | `ht` alanı, 16 baytlık ham sabit içeren bir birleşimin SHA-1'i | yeniden hesaplandı, byte-byte eşleşti |
| F7 | Sunucu RSA açık anahtarı canlı süreçten kurtarılabilir (CryptoPP nesnesi) | oracle 401 ile 400'ü ayırıyor |
| F8 | IPC çerçevesi 26 bayt: `[u32 tip][u32 toplam][u16 alan][16×0]` | 62/62 gerçek mesaj |
| F9 | Kimlik doğrulama yanıtı 1250 B, 4 alan | yeniden üretildi, üçüncü taraf kaydıyla karşılaştırıldı |
| F10 | "Yeniden başlatma gerekli" iki formülden biriyle hesaplanıyor | disassembly + canlı istemci logu |

### 1.2 Kapsam ve kapsam dışı

Bu doküman anti-cheat'i atlatmayı **anlatmaz**. Üç soruyu yanıtlar:

1. İstemcinin ağ ve IPC protokolleri byte düzeyinde nasıl görünüyor?
2. Hangi parçalar çevrimdışı yeniden üretilebilir, hangileri üretilemez?
3. Hangi istemci izleri gözlenebilir ve sunucu gerçekte neyi uyguluyor?

Üç soru **açık** kalmıştır ve tahmin edilmek yerine §11'de açıkça listelenmiştir.
