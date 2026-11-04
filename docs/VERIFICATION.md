# Verification log

**English** · [Türkçe](tr/VERIFICATION.md)

Every numeric or structural claim published in this repository, with the evidence that supports it.

**Status legend**

| Mark | Meaning |
|---|---|
| ✅ | verified against captured data or a runtime measurement |
| ➗ | derived by arithmetic from verified parts (the arithmetic is shown) |
| ⚠️ | two measurements disagree; the conservative one is published and the conflict is stated |
| ✏️ | corrected in this revision (the previous wording was wrong) |

**Evidence sources**

| Tag | Source |
|---|---|
| `CAP` | 12 captured gateway exchanges (request + response bytes) |
| `MEM` | process memory image, 2.89 GB, per-process memory map |
| `RAM` | physical memory image, 33 GiB (35.4 GB decimal) |
| `IPC` | 62 captured IPC messages from the client |
| `RUN` | runtime test on a test harness (documented in the project log) |
| `LOG` | client log lines (Riot Client / game / driver) |
| `DIS` | disassembly of the client binary |

Section references (§) point to the project working log that contains the full evidence.

---

## 1. Wire format

| ID | Claim | Value | Evidence | Status |
|---|---|---|---|---|
| P1 | Gateway path | `/vanguard/v1/gateway` | `CAP` | ✅ |
| P2 | Ports | 8443 (CDN edge), 443 (cloud edge) | `CAP`, `LOG` | ✅ |
| P3 | Outer frame | `08 <type> 12 <varint len> <envelope> 18 01` | `CAP` (§4.3) | ✅ |
| P4 | Magic | `52 47 01 00` (`RG\x01\x00`) | `CAP` (§4.4) | ✅ |
| P5 | RSA block size | 256 bytes (2048-bit) | `CAP` (§4.4) | ✅ |
| P6 | Nonce / tag | 12 B / 16 B | `CAP` (§4.4) | ✅ |
| P7 | Envelope size identity | `4 + 256 + 12 + 2683 + 16 = 2971` | `CAP` (f2=2971), `MEM` (plaintext 2683) | ➗ |
| P8 | Frame body size | 2978 B (7-byte frame header + 2971) | `CAP` (§36.1) | ➗ |
| P9 | Message types | 3 auth, 4 access, 5 token, 7 hb, 8 hb-reply, 9 task, 11 ack | `CAP` (§4.5) | ✅ |
| P10 | Session captures used | 12 connection records (`conn_001..012`) | `CAP` (§19) | ✅ |

## 2. Cryptography

| ID | Claim | Value | Evidence | Status |
|---|---|---|---|---|
| K1 | Key wrapping | RSA-OAEP, SHA-512, MGF1-SHA512, empty label | `CAP` + RTTI (§5.3, §136) | ✅ |
| K2 | Content cipher | AES-256-GCM, 96-bit nonce, 128-bit tag, no AAD | `CAP` | ✅ |
| K3 | GCM data counter | starts at `J0+1` (`AES_K(IV‖2)` for the first block) | synthetic vector + real plaintext (§57.2) | ✅ |
| K4 | Session key | 32 random bytes | `MEM` (§57) | ✅ |
| K5 | Client key | RSA-2048, **e = 17**, persistent per installation | `MEM` (§111.5) | ✅ |
| K6 | Server key | RSA-2048, **e = 65537** | `MEM` + oracle 401 (§136) | ✅ |
| K7 | OAEP `|DB|` | 191 bytes (`k − hLen − 1`) | arithmetic | ➗ |
| K8 | Session key lifetime | zeroized within ~50 s of sending | 35.4 GB scan, negative (§114.2) | ✅ |

> **K3 note.** This is the single most expensive mistake in the work: every earlier key search used
> counter 1 and therefore rejected the correct key. See `docs/08-negative-results.md` N2/N14 and
> `docs/02-crypto.md` §3.2.

## 3. Authentication payload

| ID | Claim | Value | Evidence | Status |
|---|---|---|---|---|
| A1 | Plaintext size | 2683 bytes | `MEM` (§57) | ✅ |
| A2 | Field set | f1,f2,f4,f5,f6,f7,f8,f9,f13,f14,f15 (no f10) | `MEM` (§205.3) | ✅ |
| A3 | f1 length | 895 bytes | `MEM` (§60) | ✅ |
| A4 | f4 token length | ~1106 characters | `IPC` + `MEM` (§138) | ✅ |
| A5 | f5 length | 392–398 characters (DER 292 B) | `MEM` (§205.6) | ✅ |
| A6 | f2 OS | platform 1, arch 2, version string | `MEM` (§57.1) | ✅ |
| A7 | f9 value | 3 | `MEM` (§57.1) | ✅ |
| A8 | f14 entries | 5 (HVCI, IOMMU, TPM2, VBS, SB) | `MEM` (§57.1, §265.1) | ✅ |
| A9 | f14 order | VBS, SB, TPM2, HVCI, IOMMU | `MEM` (§265.1) | ✅ |
| A10 | f15 entries | 3 (`htt` 32 B, `ht` 20 B, `gg` 20 B) | `MEM` (§265.2) | ✅ |
| A11 | `f10` presence | absent on this build | `MEM` (§205.3) | ✅ |

### 3.1 Device identifier parts

| ID | Part | Value | Evidence | Status |
|---|---|---|---|---|
| D1 | p1 | 16 B, SMBIOS UUID (GUID little-endian) | `MEM` matched BIOS UUID (§60) | ✅ |
| D2 | p2 | 64 B, **kernel driver IOCTL #11** (SHA-512 block) | driver IOCTL inventory (§73.1), stability across sessions (§60) | ✅ |
| D3 | p3 | 64 B, **kernel driver IOCTL #12** (second SHA-512 block) | same | ✅ |
| D4 | p4 | 0 B (empty separator) | `MEM` (§60) | ✅ |
| D5 | p5 | 6 B, default-gateway MAC | `MEM` matched ARP entry (§60) | ✅ |
| D6 | p6 | 5 × 97 B, disk serial + model, client reads it via WMI `Win32_DiskDrive` | `MEM` (§60); driver's `0x22C000` reply does **not** feed it (§148.5) | ✅ |
| D7 | Length identity | `4+24 + 4+88 + 4+88 + 3 + 4+8 + 4+664 = 895` | arithmetic on A3 | ➗ |
| D8 | p2/p3 not derivable in user mode | 234,234 hash combinations tried, none matched | `RAM`/`MEM` experiment (§80.4) | ✅ |

> **D2/D3/D6 were wrong in the first publication** ("origin not determined", "p6 from the driver").
> Corrected in revision 2 (see §6 of this file).

### 3.2 Integrity fields

| ID | Claim | Value | Evidence | Status |
|---|---|---|---|---|
| I1 | `ht` formula | `Base64(SHA1("6;"+p6+"1;"+p1+"2;"+p2+"3;"+p3+"5;"+p5+version+MAGIC))` | recomputed, byte-equal (§137.1) | ✅ |
| I2 | `MAGIC` | 16 **raw** bytes `F4AD529CDE170EE1D1029B4A3CA89820` | `MEM` + recompute (§137.1) | ✅ |
| I3 | `htt` / `gg` | validated but derivation unknown | random value + valid token → 400 (§264.1, §195.6) | ✅ |
| I4 | `htt`/`gg` search scale | ≈1.34 M structural combinations (953,312 + 385,160) | (§71.5, §264.4) | ➗ |

## 4. Server key recovery

| ID | Claim | Value | Evidence | Status |
|---|---|---|---|---|
| R1 | Method | RTTI TD → COL → vtable → live object | `DIS` + `MEM` (§136.1) | ✅ |
| R2 | CryptoPP layout | `+0x28` n size, `+0x30` n ptr, `+0x58` e size, `+0x60` e ptr | `MEM` (§136.1) | ✅ |
| R3 | Oracle semantics | 400 = envelope not opened, 401 = opened/rejected | `RUN` (§136.2) | ✅ |
| R4 | Key size | 2048-bit (SPKI 294 B, base64 392) | `MEM` (§136.1) | ✅ |

## 5. IPC (pipe)

| ID | Claim | Value | Evidence | Status |
|---|---|---|---|---|
| S1 | Header | 26 bytes: `[u32][u32][u16][16×0]` | `IPC` 62/62 (§177.1) | ✅ |
| S2 | Field encoding | `[u16 tag][u32 len][data]` | `IPC` | ✅ |
| S3 | Types | `0x02 0x03 0x04 0x64 0x65 0x67 0x69 0x3EB 0x09` | `IPC` + `DIS` (§151.4, §192) | ✅ |
| S4 | `0x66` / `0x68` | not produced by this build | `DIS` (§192.1) | ✅ |
| S5 | Auth reply `0x65` | 1250 B, 4 fields: 36 / 1106 / 22 / 36 | third-party trace + `RUN` (§314.1, §314.2) | ✅ |
| S6 | Size identity | `26 + 4×6 + 36 + 1106 + 22 + 36 = 1250` | arithmetic on S5 | ➗ |
| S7 | Follow-up frame | `0x09`, 40 B, right after the auth reply | third-party trace + `RUN` (§314.1) | ✅ |
| S8 | Heartbeat reply | `0x04`, 40 B, counter echoed | `IPC` 58/58 (§193.6) | ✅ |
| S9 | Health check | `0x69` (36 B) → `0x3EB` (36 B, reasons bitmask) | `DIS` handler + `RUN` (§217, §220) | ✅ |
| S10 | Disconnect | `0x02`, no reply | `DIS` (§221) | ✅ |

## 6. Client gates

| ID | Claim | Value | Evidence | Status |
|---|---|---|---|---|
| G1 | Restart-required (flag off) | `StartType == SYSTEM_START && State != RUNNING` | `DIS` (§183.1) | ✅ |
| G2 | Restart-required (flag on) | `VgrlQueryInstallStatus() == 2` | `DIS` (§183.1) | ✅ |
| G3 | Value origin | copied from plugin state (`[rbp+0x171] → out[0x1a1]`) | `DIS` (§304.1) | ✅ |
| G4 | vgrl contract | 1342 status, 1343 text, 1344 start, 1345 flags, 1346 reset | `DIS` (§179.2) | ✅ |
| G5 | Ordinal-only exports | `NumberOfNames = 0` | `DIS` (§179.2) | ✅ |
| G6 | Riot ID gate | HTTP 467 `riot_id_required` | `LOG` (§294.1, live run) | ✅ |
| G7 | Developer bypass flag exists | `--developer-skip-riot-id` | `DIS` (§191.1) | ✅ |
| G8 | Product-session endpoints | `/product-session/v1|v2/...` (7 paths) | string inventory | ✅ |
| G9 | Product-session cadence | 60 s, 300 s ceiling string | string inventory | ✅ |
| G10 | Session object | 23 fields | `MEM` (§306.4) | ✅ |
| G11 | `expiredTime` unreliable | unset/stale while connected | `MEM` (§306.4) | ✅ |
| G12 | Real session lifetime | 646 s | `LOG` RMS timeline (§306.4) | ✅ |
| G13 | Launch arguments | 9 arguments, incl. settings token | `MEM` (§312.1) | ✅ |
| G14 | Settings token content | OAuth code + PKCE verifier + local tokens | `MEM` decompressed (§312.1) | ✅ |
| G15 | Auth code single-use | replay → `401 invalid_grant` | `RUN` (§312.2) | ✅ |

## 7. Detection

| ID | Claim | Value | Evidence | Status |
|---|---|---|---|---|
| T1 | Ban types | `TIME_BAN` + `PERMANENT_BAN`, reason `THIRD_PARTY_TOOLS`, scope product | RSO `userinfo` (§310.1) | ✅ |
| T2 | Ban duration | 14 days (time ban) | `expirationMillis` arithmetic (§310.1) | ➗ |
| T3 | Ban issue time | matches the AUTH attempts within the same minute | two independent reads (§310.1) | ✅ |
| T4 | Accounts banned after AUTH | 8 of 8, +0.5 … +2.7 s | `LOG` correlation (§230.1) | ✅ |
| T5 | Accounts unaffected without AUTH | 3 of 3 | `LOG` (§230.1) | ✅ |
| T6 | Penalty taxonomy | 359 localisation keys; `VANGUARD_BYPASS` separate | `MEM` string scan (§311.6) | ✅ |
| T7 | Client traces | 5 measured traces (env vars, version resource, driver signature, device id) | `LOG` + `MEM` (§311.8) | ✅ |

> **T4/T5 caveat.** Samples of 8 and 3, single environment. This supports a causal hypothesis,
> not a rate for the general population. Published as such.

## 8. Measurements

| ID | Claim | Value | Evidence | Status |
|---|---|---|---|---|
| M1 | AUTH response | 200, 8193 B (TokenResponse 7900 B) | `RUN` (§137.2, §296.1) | ✅ |
| M2 | Token in TokenResponse | 6167 B | `RUN` (§137.3) | ✅ |
| M3 | ACCESS response | 200, 6923 B (plain 6630 B) | `RUN` (§296.1) | ✅ |
| M4 | Heartbeat response | 200, 39.5–88.7 MB, 4–11 tasks | `RUN` (§158, §289.1) | ✅ |
| M5 | TaskResult response | 200, 293 B, type 11, empty body | `RUN` (§158.1) | ✅ |
| M6 | Heartbeat cadence | 90 s | `LOG` 62 sessions (§195.6) | ✅ |
| M7 | Session TTL | ~192 s | `RUN` (§139.4) | ✅ |
| M8 | AUTH budget | **2 requests / ~15 min** | `RUN` (§307.3) | ⚠️ |
| M9 | Full-RAM scan size | 33 GiB = 35.4 GB decimal | file size | ⚠️ unit clarity |

> **M8 ambiguity.** An earlier measurement recorded `3 / ~13 min` (§146.2); a later controlled run
> produced `200 · 200 · 429 · 429 · 429 · 429`, i.e. 2 per window (§307.3). This repository
> publishes the conservative figure (2) and states both. Treat the budget as "2–3 per 15 minutes,
> assume 2".
>
> **M9.** The image is 33.0 GiB on disk; the same file is 35.4 GB in decimal. Both numbers appear
> in the project log. This repository writes "33 GiB (35.4 GB)".

## 9. Negative results (cross-check)

| ID | Claim | Value | Evidence | Status |
|---|---|---|---|---|
| N-1 | Server key candidates | 340+ candidates, all 400 | `RUN` (§101) | ✅ |
| N-2 | Session key in memory | 35.4 GB RAM + 2.89 GB process dump → not found | `RAM`/`MEM` (§114.2) | ✅ |
| N-3 | `htt`/`gg` derivation | ≈1.34 M combinations, no match | (§71.5, §264.4) | ✅ |
| N-4 | `htt`/`gg` validation | random + valid token → 400 | `RUN` (§264.1) | ✅ |
| N-5 | Module payload static key | ~4.6 B attempts, 4 binaries | `RUN` (§246.4) | ✅ |
| N-6 | Module payload wrapped key | 215 M attempts | `RUN` (§240.1) | ✅ |
| N-7 | Module carve | 11.3 GB dumps → 315 PE images, no module | `MEM` (§243.2) | ✅ |
| N-8 | Virtual CFG static recovery | 5 independent methods failed | `DIS` (§108.4) | ✅ |
| N-9 | Synthetic-state execution | 400 blocks → fault after 7 memory accesses | `RUN` (§97.1) | ✅ |
| N-10 | Dispatch affinity | 960 unit vectors + 32 random pairs → not affine | `RUN` (§120.1) | ✅ |
| N-11 | Dispatch returns like `ret` | 17,310 stack samples → 0 | `DIS` (§120.2) | ✅ |
| N-12 | Intra-block constant propagation | 32,605 indirect jumps → 0 resolved | `DIS` (§120.3) | ✅ |
| N-13 | Virtual code in physical dump | 33 GiB scan → 0 signature hits | `RAM` (§315) | ✅ |
| N-14 | High-entropy blobs decoded | 2,678 + 1,066 = 3,744 blocks, 7 ciphers × 12 keys → no match | `MEM` (§311.4) | ➗ |
| N-15 | Gateway session extension | auth + access + heartbeat 200 → session still closed | `RUN` (§296.1) | ✅ |
| N-16 | External session refresh | heartbeat/disconnect → 403 `NONSELF_OPERATION`, connect → 404 | `RUN` (§306.1) | ✅ |
| N-17 | Task id as key seed | 7/7 measured → it is CRC32 | `RUN` (§162.1) | ✅ |
| N-18 | Hosts-file redirection | client ignored it | `LOG`/`CAP` (§7.2) | ✅ |
| N-19 | System proxy redirection | tunnel not used | `LOG` (§7.2) | ✅ |
| N-20 | TLS key log covers game TLS | 93 secrets vs 779 handshakes → 0 | `RUN` (§293.1) | ✅ |

## 10. Corrections applied in this revision

| # | Was published | Correct | Evidence |
|---|---|---|---|
| 1 | p2/p3 "origin not determined" | p2 = driver IOCTL #11, p3 = IOCTL #12 (SHA-512 blocks) | §73.1, §60 |
| 2 | p6 "comes from the driver" | p6 is read by the client via WMI `Win32_DiskDrive`; the driver's `0x22C000` reply mirrors the layout but does not feed it | §148.5, §60 |
| 3 | Rate limit "2 per 15 min" (single figure) | published as 2–3 per 15 min, assume 2; both measurements listed | §146.2, §307.3 |
| 4 | "35.4 GB RAM scan" without unit note | "33 GiB (35.4 GB decimal)" | file size |
| 5 | `htt`/`gg` "~1.3 M" | "≈1.34 M (953,312 + 385,160)" | §71.5, §264.4 |

## 11. Claims that are **not** verifiable from the project record

These are stated as observations in the documents and are flagged here so they are not treated as
established facts:

| Claim | Why it is not verifiable |
|---|---|
| Ordering of `f15` entries (`htt`, `ht`, `gg`) | observed in one plaintext; server-side ordering requirement untested |
| Meaning of `TokenResponse` f3 / f8 / f9 | values observed repeatedly, semantics unknown |
| `product-session` 300 s ceiling | inferred from a string literal, not measured |
| `0x66`/`0x68` absence | based on static scan of this build only |
| Penalty "14 days" | derived from one time ban; policy may vary per case |

---

## 12. How to re-run the verification

```bash
# 1. structural checks that need no network
python3 reference/pipe_proto.py        # 1250 / 40 / 36 / 40 byte identities
python3 reference/auth_build.py        # 895-byte machine id, ht, envelope round-trip

# 2. cross-check published numbers against the project log (if you have it)
grep -n "2971\|2683\|895\|1250\|62/62\|58/58" AGENTS.md

# 3. sizes of the raw evidence
ls -l ram.raw                          # 33 GiB  (35.4 GB decimal)
```

---

*End of verification log.*
