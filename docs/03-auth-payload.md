# Auth Payload

**English** · [Türkçe](tr/03-auth-payload.md)

> Field map, device identifier layout, integrity field, security flags.
>
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research; see the repository README for scope and legal notice.

## 4. Authentication payload

### 4.1 Field map

| Field | Content | Measured size |
|---|---|---|
| f1 | device identifier (`‖1;…‖6;`) | 895 B |
| f2 | OS info (platform, arch, version string) | 16 B |
| f4 | RSO access token (JWT) | 1106 chars |
| f5 | client ephemeral public key (SPKI base64) | 398 chars (DER 292 B) |
| f6 | client version `{1,19,1,18}` | 8 B |
| f7 | same version block | 8 B |
| f8 | product id | 22 B |
| f9 | boot state (varint 3) | 1 B |
| f13 | external session id (UUID) | 36 B |
| f14 | security flags (5 entries) | — |
| f15 | integrity map: `htt`, `ht`, `gg` | 3 entries |

Total serialized size: **2683 bytes**.

Note: `f10` (an "ephemeral id") is **not present** on this client version, although some public
write-ups include it. Field ordering is significant for byte equality.

### 4.2 Device identifier layout

```
"‖1;<b64>‖2;<b64>‖3;<b64>‖4‖5;<b64>‖6;<b64>;<b64>;<b64>;<b64>;<b64>"
```

| Part | Raw size | Encoding | Source (verified against hardware) |
|---|---|---|---|
| p1 | 16 B | 24 chars | SMBIOS UUID (GUID little-endian) |
| p2 | 64 B | 88 chars | **origin not determined** (stable across sessions) |
| p3 | 64 B | 88 chars | **origin not determined** (stable across sessions) |
| p4 | 0 B | — | empty separator |
| p5 | 6 B | 8 chars | default gateway MAC address |
| p6 | 5 × 97 B | 5 × 132 chars | disk serial + model, zero padded |

Length identity: `4+24 + 4+88 + 4+88 + 3 + 4+8 + 4+664 = 895`.

p2/p3 were tested against 234,234 hash combinations of 42 hardware and OS values (SHA-512,
SHA3-512, BLAKE2b, HMAC-SHA512, double SHA-512, with several separators). No match. They are
therefore stable but not derivable from publicly readable hardware values.

### 4.3 Integrity field `ht`

```
input = "6;" + p6 + "1;" + p1 + "2;" + p2 + "3;" + p3 + "5;" + p5 + version + MAGIC
ht    = Base64( SHA1(input) )            # 20 bytes → 28 chars

MAGIC = F4 AD 52 9C DE 17 0E E1 D1 02 9B 4A 3C A8 98 20      (16 raw bytes)
```

The constant must be **16 raw bytes**. Using its 32-character hex representation produces a
different digest; that distinction was one of the checks used to confirm the formula.

### 4.4 Security flags (f14)

Five entries, values 0/1. Source is a JSON file written by the tray component
(`vgtray-settings.json`) which records whether each feature was "originally missing"
(HVCI, IOMMU, TPM 2.0, VBS, Secure Boot). Reading the live registry produced different values
than the file on the same machine, so the file is the more faithful source.

---
