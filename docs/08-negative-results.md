# Negative Results

**English** · [Türkçe](tr/08-negative-results.md)

> Twenty falsified hypotheses with test scale.
>
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research; see the repository README for scope and legal notice.

## 9. Negative results

Recording these prevents duplicated effort.

| # | Hypothesis | Scale tested | Result |
|---|---|---|---|
| N1 | Server key is stored in plaintext somewhere | 340+ candidates, 4 padding variants | all 400 |
| N2 | Session key survives in memory | 33 GiB RAM (35.4 GB decimal) + 2.89 GB process dump | not found |
| N3 | `htt`/`gg` can be derived | ≈1.34 M combinations (953,312 + 385,160) | no match |
| N4 | `htt`/`gg` are not validated | random values with a valid token | rejected (400) |
| N5 | Module payload uses a static key | ~4.6 B attempts over 4 binaries | no match |
| N6 | Module payload is a wrapped key | 215 M attempts | no match |
| N7 | Module payload can be carved as PE | 11.3 GB of dumps | 315 PE images, no module |
| N8 | Virtual section CFG is statically recoverable | 5 independent methods | not recoverable |
| N9 | Lifted blocks execute with synthetic state | 400 blocks | fault after 7 accesses |
| N10 | Dispatch is affine over GF(2) | 960 unit vectors + 32 random pairs | not affine |
| N11 | Dispatch behaves like `ret` | 17,310 stack samples | 0 matches |
| N12 | Intra-block constant propagation resolves targets | 32,605 indirect jumps | 0 resolved |
| N13 | Virtual code is resident in a 33 GiB physical dump | full scan | 0 signature hits |
| N14 | High-entropy regions are encrypted secrets | 3,744 blocks, 7 ciphers × 12 keys | no match |
| N15 | Gateway session can be extended | auth + access + heartbeat all 200 | session still closed |
| N16 | Session can be refreshed from outside | heartbeat / disconnect / connect | 403 `NONSELF_OPERATION`, 404 |
| N17 | Task id doubles as a key seed | 7/7 measured | no — it is CRC32 |
| N18 | Hosts-file redirection works | 127.0.0.1 | client ignored it |
| N19 | System proxy redirection works | 8080 | tunnel not used |
| N20 | TLS key log covers game TLS | 93 secrets vs 779 handshakes | 0 intersection |

---
