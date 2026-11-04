# Canlı bellek dökümü ve incelemesi

**Türkçe** · [English](../15-memory-capture.md)

> Bu çalışmada kullanılan bellek görüntülerinin nasıl alındığı, her yöntemin maliyeti ve dökümün
> nasıl inceleneceği. Repodaki ölçümlerin yeniden üretilebilmesi için yazıldı.
> *Vanguard Gateway — Tersine Mühendislik Notları* dizisinin parçası. Yalnız savunma amaçlı araştırma.

## 15.1 Neden bellek

İki değer diskten elde edilemiyor:

1. isteğin düz metni (çalışma anında kurulup şifreleniyor);
2. çalışma anında çözülen kod sayfaları (sanal bölüm diskte paketli).

Repodaki diğer her şey yakalanan trafikten veya statik analizden geldi. Bellek bu iki değer ve
CryptoPP anahtar nesnelerinin yerini bulmak için kullanıldı (§5).

## 15.2 Yöntem A — süreç dökümü (çalıştığında tercih edilen)

Windows sürücü olmadan süreç anlık görüntüsü veriyor:

```
OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION)
VirtualQueryEx   -> bölgeler (taban, boyut, koruma, durum)
ReadProcessMemory -> okunabilir bölgeleri 1 MB parçalarla kopyala
```

Çıktı:

```
vgc_<n>_HHMMSS.raw     bölgeler adres sırasıyla birleştirilmiş düz dosya
memmap.txt             her bölge bir satır: 0x<sanal taban> 0x<0> 0x<boyut> 0x<dosya ofseti> <ad>
```

`memmap.txt` dökümü kullanılabilir yapan şey: dosyadaki her 8 baytlık değer sanal adrese geri
eşlenebiliyor, böylece imaj içinde bulunan işaretçiler takip edilebiliyor.

**Maliyet:** sürecin özel belleğinde tek geçiş; 2,9 GB'lık süreç için birkaç saniye. Hedef küçükse
saniyede birkaç örnek alınabilir.

**Hata modu:** korumalı süreçler (PPL) `OpenProcess(PROCESS_VM_READ)` çağrısını reddediyor. Bu
durumda handle açılsa bile `ReadProcessMemory` her bölge için 0 bayt döner. Görülen kodlar: `-3`
(açma başarısız), `-4` (okunabilir bölge yok), `-5` (açıldı, okuma 0 döndü).

## 15.3 Yöntem B — fiziksel bellek görüntüsü

Süreç korumalıysa fiziksel adres uzayı alınır:

```
winpmem_x64 (imzalı) -> \\.\pmem  ->  ram.raw
```

**Maliyet:** 32 GB RAM için 33 GiB dosya; dizüstü SSD'de 10–25 dakika. Dosya ham fiziksel harita
olduğu için sanal adresler sayfa tablosu yürüyüşüyle veya bir bellek adli aracıyla (Volatility
`windows.memmap`, ayrıca memmap logu üretir) yeniden kurulur.

**Sınır:** bu süreç görüntüsü değil, fiziksel çerçeve görüntüsüdür. Çekim anında takas edilmiş
sayfalar eksik, şifreli/kırpılmış sayfalar şifreli kalır.

## 15.4 Yöntem C — çökme dökümü (son çare)

Hedef okunamıyorsa ve durdurulamıyorsa, tam çökme dökümü çekirdeğe RAM'in tamamını yazdırır:

```
HKLM\SYSTEM\CurrentControlSet\Control\CrashControl
    CrashDumpEnabled = 1            (tam bellek dökümü)
    DedicatedDumpFile = C:\dedicateddump.sys
    AlwaysKeepMemoryDump = 1

tetik: NtRaiseHardError(0xC0000420, OptionShutdownSystem)
       veya RtlSetProcessIsCritical + TerminateProcess
       veya CrashOnCtrlScroll (etkin olması için yeniden başlatma gerekir)
```

**Maliyet:** 30+ GB yazma, yeniden başlatma, birkaç dakika kesinti. `CrashOnCtrlScroll` kayıt
değişikliğinden sonra yeniden başlatılmadan çalışmaz. `NtRaiseHardError` bazı yapılandırmalarda
bugcheck üretmeden döner; `RtlSetProcessIsCritical` yolu daha güvenilir.

**Burada ne zaman işe yaradı:** gateway anahtarı için hiç (oturum anahtarı bir dakikadan kısa sürede
sıfırlanıyor), ama korumalı bir süreci seçilen anda yakalamanın tek yolu.

## 15.5 Yöntem D — mevcut mini dökümler

Windows süreç çökme klasörüne küçük döküm yazar:

```
%LOCALAPPDATA%\CrashDumps\<imaj>.<pid>.dmp          (burada her biri 3,5–4,2 MB)
```

Anti-cheat servisi için dokuz tane vardı. İçlerinde iş parçacığı yığınları ve küçük bir modül listesi
var, heap yok. Ayrıştırması ucuz (`MINIDUMP_MEMORY64_LIST`), ama yalnız "iş parçacığı neredeydi"
sorusunu yanıtlar, "bellekte ne vardı" sorusunu değil.

## 15.6 Yöntem E — sanal makine duraklatma (kullanılmadı, önerilen)

Bileşeni VM içinde çalıştır, ilgilenilen anda duraklat, guest RAM'i hypervisor'dan al:

```
(qemu) stop
(qemu) pmemsave 0 <boyut> guest.raw
```

**Atomik** anlık görüntü veren tek yöntem: örnekleme boşluğu yok, hedeften işbirliği gerekmiyor.
Maliyeti VM kurulumu ve bazı yazılımların sanal makinede çalışmayı reddetmesi.

## 15.7 Dökümü cevaba çevirmek

### 15.7.1 Adres eşleme

```python
regions = []          # memmap.txt'den
def read_va(fh, va, n):
    for base, size, off in regions:
        if base <= va < base + size:
            fh.seek(off + (va - base))
            return fh.read(min(n, base + size - va))
    return b""
```

Düz dosyayı sanal adresle doğrudan indeksleme; dosya bir birleşim, VA haritası değil.

### 15.7.2 String çıkarma

```bash
strings -a -n 10 vgc.raw | sort -u > strings.txt
```

İki tuzak:

- **Sözlük yanlış pozitifi.** `gobbledygook` gibi bir kelime gömülü İngilizce kelime listesinde
  geçer; komşusuna bakmadan cihaz adı sanılır. Bir isabete inanmadan önce ±200 bayt bağlam yazdır.
- **Kaçışlı yük.** Log içindeki JSON `\"` ile kaçışlı saklanır; düz `grep '"'` kaçırır. Kaçışsız
  biçimi de ara.

### 15.7.3 İmaj ve yapı ayıklama

- **PE imajları:** `MZ` + `0x40 ≤ e_lfanew < 0x400` + `PE\0\0` + geçerli bölüm sayısı. 11,3 GB'lık
  dökümden 315 imaj çıktı; hedef modül aralarında yoktu, bu da bir sonuç.
- **IPC çerçeveleri:** arama değil doğrulama. Çerçeve `[u32 tip][u32 toplam][u16 alan][16×0]` ve
  ardından gelen `[u16 tag][u32 uzunluk][veri]` girdileri toplamı tam olarak `toplam`'a eşit olmalı.
  Bu doğrulayıcı üç çerçeve buldu, binlerce benzerini reddetti.
- **Entropi:** 4 KiB bloklar, Shannon entropisi `H = −Σ p·log2 p`; yazdırılabilir oran 0,85'in
  altındaysa string bölgesi elenir. Yüzlerce KB boyunca 8.000 civarı ve tekrar eden 16 baytlık blok
  yoksa veri rastgele veya akış-şifreli, sıkıştırılmış değil.

### 15.7.4 İsabeti doğrulamak

Bellekte bulunan bir düz metin, yakalanan baytlarla eşleşene kadar iddia değil. Bu çalışmada kontrol:

```
bellek:  bir adreste düz metin, 0x1370 bayt sonra zarf, hemen ardından şifreli metin
kayıt:   aynı zarf sihri, aynı nonce, aynı şifreli metin
=> düz metin yakalanan isteğe ait
```

Üçlü eşleşme olmadan "istek gibi görünen" bir string hiçbir şey kanıtlamaz.

## 15.8 Bellek dökümünün vermediği

| Hedef | Sonuç |
|---|---|
| oturum anahtarı (32 B) | yok — ~50 s içinde sıfırlanıyor; tam RAM taraması negatif |
| sunucu açık anahtarı | statik dökümlerde yok; yalnız çalışan süreçte CryptoPP nesnesi olarak var |
| sanal kod | 33 GiB fiziksel görüntüde yok (0 imza) — süreç çalışmıyordu |
| canlı yürütme bağlamı | boşta alınan dökümlerde yok; kullanım anında çekim gerekir (§15.6) |

## 15.9 Uygulama kontrol listesi

```
1. soruyu belirle (düz metin mi, kod mu, yapı mı)
2. önce Yöntem A (süreç dökümü) - ucuz, tekrarlanabilir, memmap verir
3. korumalıysa -> Yöntem B (fiziksel) + sayfa tablosu yürüyüşü
4. zaman kritikse -> Yöntem E (VM duraklatma), Yöntem C değil
5. yapıları her zaman doğrulayıcıyla doğrula, substring ile değil
6. her isabeti yakalanan trafikle karşılaştır
7. offset ve boyutları nota yaz; offset'siz isabet yeniden üretilemez
```

## 15.10 Etik

Sahibi olmadığın yazılımın belleğini almak yerel hukuku ve ürün şartlarını ihlal edebilir.
Buradaki her şey yazarın kendi makinesinde, o makinenin kendi trafiği için yapıldı. Bu teknikleri
üçüncü taraf sistemlere uygulamayın.
