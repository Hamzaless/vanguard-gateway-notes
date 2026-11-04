# Summary

**English** · [Türkçe](tr/00-summary.md)

## 1. Summary

### 1.1 Verified findings

| # | Finding | How it was verified |
|---|---|---|
| F1 | Outer frame is `08 <type> 12 <len> <envelope> 18 01` | 12 independent session captures |
| F2 | Envelope = `RG\x01\x00` ‖ RSA-OAEP-SHA512(32 B key) ‖ 12 B nonce ‖ AES-256-GCM ‖ 16 B tag | decrypt + re-encrypt round trip |
| F3 | GCM data keystream starts at `J0+1` (counter = 2, not 1) | synthetic vector + real plaintext |
| F4 | Authentication payload is a protobuf message with 11 populated fields | full plaintext recovered from process memory |
| F5 | Device identifier is a 6-part `‖1;…‖6;` string; parts map to real hardware | UUID / router MAC / disk serial matched |
| F6 | Integrity field `ht` is SHA-1 over a concatenation with a 16-byte raw constant | recomputed and matched byte-for-byte |
| F7 | Server RSA public key can be recovered from a live process (CryptoPP object) | oracle distinguishes 401 vs 400 |
| F8 | IPC frame is 26 bytes: `[u32 type][u32 total][u16 fields][16×0]` | 62/62 real messages |
| F9 | Authentication reply is 1250 B with 4 fields | reconstructed and compared with a third-party trace |
| F10 | "Restart required" is computed by one of two formulas, driven by stored state | disassembly + live client log |

### 1.2 Scope and non-goals

This document does **not** describe bypassing anti-cheat. It answers three questions:

1. What do the client's network and IPC protocols look like, byte for byte?
2. Which parts can be reproduced offline, and which cannot?
3. What client-side traces are observable, and what does the server actually enforce?

Three questions remain **open** and are listed explicitly in §11 rather than guessed.

---
