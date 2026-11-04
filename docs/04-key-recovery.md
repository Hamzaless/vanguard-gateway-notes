# Key Recovery

**English** · [Türkçe](tr/04-key-recovery.md)

> RTTI → COL → vtable → live object; oracle verification.
>
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research; see the repository README for scope and legal notice.

## 5. Recovering the server public key

### 5.1 Why it is needed

The RSA block wraps a random 32-byte session key with the **server's** public key. Without that
key, no syntactically valid request can be produced, regardless of what the plaintext contains.

### 5.2 Method (version independent)

1. Enumerate C++ RTTI type descriptors in `.rdata` (`OAEP<SHA1>`, `OAEP<SHA512>`, `RSAFunction`,
   `GCM_Final`).
2. Resolve each type descriptor to its **Complete Object Locator** (a DWORD referencing the TD RVA).
3. Find the **vtable** that points at the COL.
4. Search a live process dump for that vtable value (the object's `vptr`).
5. Read the CryptoPP object layout:

```
+0x00  vptr
+0x28  modulus word count          +0x30  modulus pointer
+0x58  exponent word count         +0x60  exponent pointer
```

6. Convert `(n, e)` to PEM and validate with the oracle.

### 5.3 Verification

| Candidate object | Exponent | Oracle | Interpretation |
|---|---|---|---|
| A | 65537 | **401** | envelope accepted, credentials rejected ⇒ correct key |
| B | 17 | 400 | envelope could not be opened ⇒ client key |

400 means "could not decrypt/parse"; 401 means "decrypted, rejected". This distinction was
reproduced on two different regional endpoints.

> RTTI and vtable addresses shift on every release; the method above does not.

---
