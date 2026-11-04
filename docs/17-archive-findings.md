# Archive findings: corrections, anti-debug, log grammar

**English** · [Türkçe](tr/17-archive-findings.md)

> Items recovered from the remaining project notes: corrected assumptions, `.riot0` coverage
> measurements, anti-debug inventory, and the exact log line grammar.
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research only.

## 17.1 Assumptions that were wrong

Recorded so they are not repeated:

| Assumption | Measurement |
|---|---|
| `.riot0` is encrypted VM data | it is code and loader data; entropy per sub-region is low, no 4 KiB window above 7.3 |
| `.grfn1` calls `.riot1` 496 times | the count came from raw `E8` byte patterns, not from decoded calls; after validation the direct call count is 0 |
| IAT slots are written by the lifted code | the slots are **read** from 46 sites, all inside `.grfn1`; no converted region writes them |

## 17.2 `.riot0` coverage

Measurements from the sweep work:

```
sub-region entropy   header 0.854 · exception directory 7.170 · tail table 0.476
4 KiB distribution   mean 4.94 · min 0.000 · max 7.013
                     H<3: 31 blocks · 3–6.5: 82 blocks · >6.5: 25 blocks
high-entropy (>7.3) windows: 0        -> no encrypted blob inside the section
```

Translation coverage of the section:

```
9,834 blocks  477,799 bytes = 29.4%   (three passes, overlapping seeds)
49,095 blocks 582,038 bytes = 35.8%   (monotonic, non-overlapping)
seed sources: 78,799 internal branch targets + 10,297 -> 89,096 seeds
note: .riot0 has no exception directory; linear sweep is noisy there
```

First `.text` target reached from `.riot0`: `0x35B838` (ordinary code, not crypto).

## 17.3 Anti-debug inventory

Measured on the unpacked images with `.pdata`-validated function boundaries:

| Primitive | Count |
|---|---|
| `int 2d` | 0 |
| `int 3` used as detection | 0 |
| `KUSER_SHARED_DATA.KdDebuggerEnabled` read (`0x7ffe02d4`) | the only real detection primitive found |
| `rdtsc` | 378 (in the driver) |
| `cpuid` | 226 |
| `xgetbv` | 1 |

Consequences:

- Classic debugger traps are effectively absent. The cost of anti-debug is not in the binary.
- Timing and CPUID usage is heavy; for emulation this means the emulator must implement
  `rdtsc`/`rdtscp`, `cpuid` (with a leaf table and the hypervisor bit cleared) and `xgetbv`
  correctly, or the code takes wrong branches. Seven stubs in total were required for a working
  Unicorn run.
- For static analysis none of this matters: nothing is triggered unless a debugger is attached.

## 17.4 Log line grammar

Service logs are `pvpv` containers holding UTF-16LE lines. After decoding, the grammar is:

```
[<pid>][<MM/DD/YY HH:MM:SS>][<level>]: <code>: <fields separated by " ; ">
```

Example:

```
[16948][10/17/26 13:18:15][i]: 141: eu.vg.ac.pvp.net:8443;eu2.vg.ac.pvp.net:443
```

Level characters observed: `[i]` info, `[!]` error, `[-]` trace. Code is a small integer; field count
and meaning depend on the code (60 codes are catalogued in the project notes). Record `191` carries
`IOCTL code ; NTSTATUS`, and record `141` carries the gateway endpoint list.

Timestamps are local time; correlation with other logs requires the same clock and time zone.

## 17.5 What this adds

- Three assumptions in the earlier notes are now explicitly falsified; two of them concerned where
  code lives and where IAT values come from.
- `.riot0` is a code/data section with no encrypted payload; the coverage ceiling (35.8%) is a
  measurement, not a limitation of effort.
- Anti-debug is not the obstacle in this binary; emulation stubs for time and CPUID are.
- Log parsing is mechanical once the container is decoded; the grammar above is enough to write a
  parser.

## 17.6 Envelope protobuf and header coupling

The frame body is itself protobuf, and the field numbers are known:

```
Envelope {
  1: uint32  message_type
  2: bytes   envelope bytes     ("RG\x01\x00" | RSA | nonce | ciphertext | tag)
  3: uint32  1                  (optional trailer, server accepts its absence)
}
```

Size example from a capture: body `2960 B` = `08 03` (2) + `12 89 17` (3) + `2953` + `18 01` (2), and
`2953 = 4 + 256 + 12 + 2665 + 16`. The same arithmetic with a 2683-byte plaintext gives 2971; both
were observed, they differ only by plaintext length.

Header coupling, both tested:

| Header | Requirement |
|---|---|
| `X-VG-1` | must equal the envelope `message_type`; mismatch returns **400** |
| `X-VG-2` | **not required** for authentication; omitting it does not change the result |
| `X-VG-3` | constant `1` |

Padding evidence: the leaked implementation sets `BCRYPT_OAEP_PADDING_INFO.pszAlgId` to
`BCRYPT_SHA512_ALGORITHM`, which matches the SHA-512 padding that the oracle accepts.

Type numbering correction: "AUTH = 1, ACCESS = 3" is wrong. Verified values are AUTH = 3,
ACCESS = 4, heartbeat = 7, reply = 5. Two further values appeared in captures: `10` as an empty or
keepalive message, and `1` in a single bootstrap-like message (288-byte envelope) whose role was
never confirmed.

## 17.7 Two different heartbeat formats (correction)

Leaked sources contain two unrelated heartbeat builders. They belong to different channels and
must not be merged into one schema:

| Source | Channel | Fields |
|---|---|---|
| `EncodeHeartbeatRequest` | gateway HTTP | `f1` token, `f2` timestamp, `f4 = 1`, `f5` ×2, `f6 = 1` — no other fields |
| `…WithTasks` | gateway HTTP | the above plus `f7` tasks, `f12` module ×3, `f16 {f1=1, f2=0}` |
| `heartbeat_payload` (in the reference emulator) | **driver IOCTL reply** (`0x22C034`) | byte-oriented, not protobuf: `0x0C`/`0x10` written literally, lengths big-endian; `f16 = {eph, secret16, htt}` exists only here |

Consequence for this work: the heartbeat request used in the live tests carried a different field
set from both leaked builders and was still accepted (200). Acceptance therefore does not prove the
field set; only the reply parsing (§ response schema) is fully constrained by observation.

## 17.8 Game-log run statistics

Eleven captured runs of the client were tabulated (timings only, no identifiers):

| Metric | Value |
|---|---|
| run duration | 33 s … 210 s |
| reached main menu | 1 of 11 |
| reached in-game state | 1 of 11 |
| first fault | `VanguardFail` (most runs), `SessionRefreshFail` (some) |
| time from session connect to first fault | 3 s … 190 s |

Read as: the client can reach the menu and enter a game when the local pieces are consistent, but
the platform session fails shortly after, consistent with §16.9 (the two failure names are distinct).
