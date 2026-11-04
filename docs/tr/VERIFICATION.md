# Doğrulama Kaydı

**Türkçe** · [English](../VERIFICATION.md)

Bu depoda yayınlanan her sayısal/yapısal iddia ve onu destekleyen kanıt.

| İşaret | Anlam |
|---|---|
| ✅ | yakalanan veri veya çalışma anı ölçümüyle doğrulandı |
| ➗ | doğrulanmış parçalardan aritmetikle türetildi (aritmetik gösterilir) |
| ⚠️ | iki ölçüm çelişiyor; temkinli olan yayınlandı, çelişki belirtildi |
| ✏️ | bu revizyonda düzeltildi |

**Kanıt kaynakları:** `CAP` (12 yakalanmış gateway alışverişi) · `MEM` (2,89 GB süreç dökümü) ·
`RAM` (33 GiB fiziksel görüntü) · `IPC` (62 IPC mesajı) · `RUN` (çalışma anı testi) ·
`LOG` (istemci logları) · `DIS` (disassembly). § işaretleri proje çalışma kaydındaki bölümlerdir.

---

## 1. Tel biçimi

| ID | İddia | Değer | Kanıt | Durum |
|---|---|---|---|---|
| P1 | Gateway yolu | `/vanguard/v1/gateway` | CAP | ✅ |
| P2 | Portlar | 8443 (CDN), 443 (bulut) | CAP, LOG | ✅ |
| P3 | Dış çerçeve | `08 <tip> 12 <varint> <zarf> 18 01` | CAP §4.3 | ✅ |
| P4 | Sihir | `52 47 01 00` | CAP §4.4 | ✅ |
| P5 | RSA blok | 256 B (2048-bit) | CAP §4.4 | ✅ |
| P6 | nonce / tag | 12 B / 16 B | CAP §4.4 | ✅ |
| P7 | Zarf boyutu | `4+256+12+2683+16 = 2971` | CAP (f2=2971) + MEM | ➗ |
| P8 | Çerçeve gövdesi | 2978 B | CAP §36.1 | ➗ |
| P9 | Tipler | 3,4,5,7,8,9,11 | CAP §4.5 | ✅ |
| P10 | Kullanılan kayıt | 12 conn (`conn_001..012`) | CAP §19 | ✅ |

## 2. Kriptografi

| ID | İddia | Değer | Kanıt | Durum |
|---|---|---|---|---|
| K1 | Anahtar sarma | RSA-OAEP-SHA512, MGF1-SHA512 | CAP + RTTI | ✅ |
| K2 | İçerik şifresi | AES-256-GCM, 96-bit nonce, AAD yok | CAP | ✅ |
| K3 | GCM sayacı | `J0+1` (ilk blok `AES_K(IV‖2)`) | sentetik + gerçek düz metin §57.2 | ✅ |
| K4 | Oturum anahtarı | 32 B | MEM §57 | ✅ |
| K5 | İstemci anahtarı | RSA-2048, **e=17**, kalıcı | MEM §111.5 | ✅ |
| K6 | Sunucu anahtarı | RSA-2048, **e=65537** | MEM + oracle 401 §136 | ✅ |
| K7 | OAEP `|DB|` | 191 B | aritmetik | ➗ |
| K8 | Anahtar ömrü | gönderimden sonra ~50 s içinde sıfırlanır | 35,4 GB tarama §114.2 | ✅ |

## 3. Kimlik doğrulama yükü

| ID | İddia | Değer | Kanıt | Durum |
|---|---|---|---|---|
| A1 | Düz metin | 2683 B | MEM §57 | ✅ |
| A2 | Alan kümesi | f1,f2,f4,f5,f6,f7,f8,f9,f13,f14,f15 (f10 yok) | MEM §205.3 | ✅ |
| A3 | f1 | 895 B | MEM §60 | ✅ |
| A4 | f4 | ~1106 karakter JWT | IPC+MEM §138 | ✅ |
| A5 | f5 | 392–398 karakter (DER 292 B) | MEM §205.6 | ✅ |
| A6 | f2 | platform 1, arch 2, sürüm | MEM §57.1 | ✅ |
| A7 | f9 | 3 | MEM §57.1 | ✅ |
| A8 | f14 | 5 giriş | MEM §57.1 | ✅ |
| A9 | f14 sırası | VBS, SB, TPM2, HVCI, IOMMU | MEM §265.1 | ✅ |
| A10 | f15 | 3 giriş: `htt` 32 B · `ht` 20 B · `gg` 20 B | MEM §265.2 | ✅ |

### 3.1 Cihaz kimliği parçaları

| ID | Parça | Değer | Kanıt | Durum |
|---|---|---|---|---|
| D1 | p1 | 16 B, SMBIOS UUID | MEM (BIOS ile eşleşti) §60 | ✅ |
| D2 | p2 | 64 B, **sürücü IOCTL #11** (SHA-512) | §73.1 + sabitlik §60 | ✅ |
| D3 | p3 | 64 B, **IOCTL #12** | aynı | ✅ |
| D4 | p4 | 0 B | MEM §60 | ✅ |
| D5 | p5 | 6 B, ağ geçidi MAC | MEM (ARP ile eşleşti) §60 | ✅ |
| D6 | p6 | 5×97 B, disk serisi+model; istemci **WMI `Win32_DiskDrive`** ile okur | MEM §60; sürücü `0x22C000` bu alanı beslemez §148.5 | ✅ |
| D7 | Uzunluk | `4+24+4+88+4+88+3+4+8+4+664 = 895` | aritmetik | ➗ |
| D8 | p2/p3 türetilemez | 234.234 kombinasyon, eşleşme yok | §80.4 | ✅ |

### 3.2 Bütünlük alanları

| ID | İddia | Değer | Kanıt | Durum |
|---|---|---|---|---|
| I1 | `ht` | `Base64(SHA1("6;"+p6+…+sürüm+MAGIC))` | yeniden hesaplandı §137.1 | ✅ |
| I2 | `MAGIC` | 16 **ham** bayt | MEM + hesap §137.1 | ✅ |
| I3 | `htt`/`gg` | doğrulanıyor, türetimi bilinmiyor | rastgele + geçerli token → 400 §264.1 | ✅ |
| I4 | Arama ölçeği | ≈1,34 M (953.312 + 385.160) | §71.5, §264.4 | ➗ |

## 4. Sunucu anahtarı

| ID | İddia | Değer | Kanıt | Durum |
|---|---|---|---|---|
| R1 | Yöntem | TD → COL → vtable → canlı nesne | DIS+MEM §136.1 | ✅ |
| R2 | Yerleşim | `+0x28/+0x30` (n), `+0x58/+0x60` (e) | MEM §136.1 | ✅ |
| R3 | Oracle | 400 açılmadı, 401 açıldı/reddedildi | RUN §136.2 | ✅ |
| R4 | Boyut | 2048-bit (SPKI 294 B) | MEM §136.1 | ✅ |

## 5. IPC

| ID | İddia | Değer | Kanıt | Durum |
|---|---|---|---|---|
| S1 | Başlık | 26 B | IPC 62/62 §177.1 | ✅ |
| S2 | Alan | `[u16 tag][u32 len]` | IPC | ✅ |
| S3 | Tipler | 0x02/03/04/64/65/67/69/3EB/09 | IPC+DIS | ✅ |
| S4 | 0x66 / 0x68 | bu sürümde yok | DIS §192.1 | ✅ |
| S5 | 0x65 yanıtı | 1250 B, 4 alan (36/1106/22/36) | üçüncü taraf kaydı + RUN §314 | ✅ |
| S6 | Boyut | `26+4×6+36+1106+22+36 = 1250` | aritmetik | ➗ |
| S7 | 0x09 | 40 B, auth yanıtından hemen sonra | §314.1 | ✅ |
| S8 | 0x04 | 40 B, sayaç yankısı | IPC 58/58 §193.6 | ✅ |
| S9 | 0x69 → 0x3EB | 36 B, reasons maskesi | DIS işleyici §217, §220 | ✅ |
| S10 | 0x02 | cevap yok | DIS §221 | ✅ |

## 6. İstemci kapıları

| ID | İddia | Değer | Kanıt | Durum |
|---|---|---|---|---|
| G1 | restartRequired (bayrak kapalı) | `StartType==SYSTEM_START && State!=RUNNING` | DIS §183.1 | ✅ |
| G2 | restartRequired (bayrak açık) | `VgrlQueryInstallStatus()==2` | DIS §183.1 | ✅ |
| G3 | Değerin kaynağı | eklenti durumundan **kopya** | DIS §304.1 | ✅ |
| G4 | vgrl ordinal'ları | 1342/1343/1344/1345/1346 | DIS §179.2 | ✅ |
| G5 | İsimsiz dışa aktarım | `NumberOfNames=0` | DIS §179.2 | ✅ |
| G6 | 467 | `riot_id_required` | LOG §294.1 | ✅ |
| G7 | Geliştirici bayrağı | `--developer-skip-riot-id` | DIS §191.1 | ✅ |
| G8 | product-session | 7 uç nokta | string envanteri | ✅ |
| G9 | Kadans | 60 s; 300 s dizesi | string envanteri | ✅ |
| G10 | Oturum nesnesi | 23 alan | MEM §306.4 | ✅ |
| G11 | `expiredTime` | TTL olarak güvenilmez | MEM §306.4 | ✅ |
| G12 | Gerçek ömür | 646 s | LOG §306.4 | ✅ |
| G13 | Başlatma argümanları | 9 argüman | MEM §312.1 | ✅ |
| G14 | settings-token | OAuth kodu + PKCE | MEM §312.1 | ✅ |
| G15 | Kod tek kullanımlık | tekrar → 401 `invalid_grant` | RUN §312.2 | ✅ |

## 7. Tespit

| ID | İddia | Değer | Kanıt | Durum |
|---|---|---|---|---|
| T1 | Ceza türleri | TIME_BAN + PERMANENT_BAN, `THIRD_PARTY_TOOLS` | userinfo §310.1 | ✅ |
| T2 | Süre | 14 gün | `expirationMillis` aritmetiği | ➗ |
| T3 | Veriliş anı | AUTH penceresiyle aynı dakika | iki bağımsız okuma §310.1 | ✅ |
| T4 | AUTH sonrası ban | 8/8, +0,5…+2,7 s | LOG §230.1 | ✅ |
| T5 | AUTH'suz | 3/3 temiz | LOG §230.1 | ✅ |
| T6 | Ceza kataloğu | 359 anahtar; `VANGUARD_BYPASS` ayrı | MEM §311.6 | ✅ |

> **T4/T5 uyarısı:** 8 ve 3 örneklem, tek ortam. Nedensellik göstergesi; oran iddiası değil.

## 8. Ölçümler

| ID | İddia | Değer | Kanıt | Durum |
|---|---|---|---|---|
| M1 | AUTH | 200, 8193 B (TokenResponse 7900) | RUN §137.2 | ✅ |
| M2 | Token | 6167 B | RUN §137.3 | ✅ |
| M3 | ACCESS | 200, 6923 B (düz 6630) | RUN §296.1 | ✅ |
| M4 | HB | 200, 39,5–88,7 MB, 4–11 görev | RUN §158 | ✅ |
| M5 | TaskResult | 200, 293 B, tip 11, boş gövde | RUN §158.1 | ✅ |
| M6 | HB kadansı | 90 s | LOG 62 oturum §195.6 | ✅ |
| M7 | Oturum TTL | ~192 s | RUN §139.4 | ✅ |
| M8 | AUTH bütçesi | **2 istek / ~15 dk** | RUN §307.3 | ⚠️ |
| M9 | RAM boyutu | 33 GiB = 35,4 GB (ondalık) | dosya boyutu | ⚠️ |

> **M8:** daha eski bir ölçüm `3 / ~13 dk` (§146.2); sonraki kontrollü koşu `200·200·429…` (§307.3).
> Yayınlanan değer temkinli olan: **2**. Bütçeyi "15 dakikada 2–3, hesapta 2" kabul edin.
>
> **M9:** görüntü diskte 33,0 GiB; aynı dosya ondalık olarak 35,4 GB.

## 9. Bu revizyonda düzeltilenler

| # | Önce yayınlanan | Doğrusu | Kanıt |
|---|---|---|---|
| 1 | p2/p3 "kaynağı belirlenemedi" | p2 = IOCTL #11, p3 = IOCTL #12 (SHA-512 blokları) | §73.1, §60 |
| 2 | p6 "sürücüden geliyor" | p6 istemcinin **WMI** sorgusundan; sürücü `0x22C000` yansıtır ama beslemez | §148.5 |
| 3 | Kota "2/15 dk" tek değer | 2–3/15 dk; güvenli kabul 2 (iki ölçüm listelendi) | §146.2, §307.3 |
| 4 | "35.4 GB RAM" birimsiz | "33 GiB (35,4 GB ondalık)" | dosya boyutu |
| 5 | `htt`/`gg` "~1,3 M" | "≈1,34 M (953.312 + 385.160)" | §71.5, §264.4 |

## 10. Proje kaydından doğrulanamayan iddialar

| İddia | Neden |
|---|---|
| `f15` giriş sırası (`htt`,`ht`,`gg`) | tek düz metinde gözlendi; sunucu sıra şartı test edilmedi |
| `TokenResponse` f3/f8/f9 anlamı | değerler gözlendi, anlam bilinmiyor |
| `product-session` 300 s üst sınırı | string dizesinden çıkarım, ölçüm değil |
| `0x66`/`0x68` yokluğu | yalnız bu build'in statik taraması |
| Ceza "14 gün" | tek zaman banından türetildi; politikaya göre değişebilir |

## 11. Doğrulamayı yeniden koşma

```bash
python3 reference/pipe_proto.py     # 1250 / 40 / 36 / 40 boyut özdeşlikleri
python3 reference/auth_build.py     # 895 bayt kimlik, ht, zarf gidiş-dönüşü
```
