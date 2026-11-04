# Crypto

**English** · [Türkçe](tr/02-crypto.md)

> RSA-OAEP parameters, AES-GCM counter rule, size arithmetic, response decryption.
>
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research; see the repository README for scope and legal notice.

## 3. Cryptography

### 3.1 Measured parameters

| Parameter | Value |
|---|---|
| Key wrapping | RSA-OAEP, SHA-512, MGF1-SHA512, empty label |
| Session key | 32 random bytes, per request |
| Content cipher | AES-256-GCM, 96-bit nonce, 128-bit tag, **no AAD** |
| Client key | RSA-2048, public exponent **17**, persistent per installation |
| Server key | RSA-2048, exponent 65537 (see §5) |

### 3.2 GCM counter rule (common pitfall)

GCM data is encrypted with the keystream starting at `J0 + 1`:

```
J0        = nonce ‖ 0x00000001
keystream = AES_K(J0+1), AES_K(J0+2), …
```

Practical consequence: for the first block,

```
AES_K(nonce ‖ 0x00000002) == C[0:16] XOR P[0:16]
```

Any key search that starts at counter 1 will reject the correct key. This mistake produced
a full generation of false negatives during this work; see §9.

### 3.3 OAEP encoding (encryption direction)

```
k = 256, hLen = 64 (SHA-512)
lHash   = SHA512("")
DB      = lHash ‖ PS ‖ 0x01 ‖ M        with |DB| = k − hLen − 1 = 191
        = 64 + PS + 1 + |M|            ⇒ |PS| = 126 − |M|
seed    = 64 random bytes
maskedDB   = DB   XOR MGF1(seed, 191)
maskedSeed = seed XOR MGF1(maskedDB, 64)
EM      = 0x00 ‖ maskedSeed ‖ maskedDB
c       = EM^e mod n
```

Using a DB length of 223 (as some published snippets do) overflows the buffer by 32 bytes and
produces a block the server cannot parse. This was confirmed by decoding failure on every attempt.

### 3.4 Response decryption

The server re-wraps the **same** session key the client sent, using the client's ephemeral public
key from field `f5`. Therefore responses are only readable with the matching private key, which
exists in the client process only for the duration of the exchange.

---
