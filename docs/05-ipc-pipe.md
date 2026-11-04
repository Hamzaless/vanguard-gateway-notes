# Ipc Pipe

**English** · [Türkçe](tr/05-ipc-pipe.md)

> 26-byte IPC frame, message types, auth reply math, heartbeat, health check.
>
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research; see the repository README for scope and legal notice.

## 6. IPC protocol (anti-cheat SDK)

### 6.1 Transport and framing

The game and the anti-cheat service communicate over a named pipe with a fixed GUID.

```
[u32 type][u32 total][u16 field_count][16 × 0x00]      = 26-byte header
repeated: [u16 tag][u32 length][data]                  = 6 + length

total = 26 + Σ(6 + length)
```

This model matched **62 of 62** captured messages. The widely circulated 36- and 40-byte header
models matched **0 of 62**.

### 6.2 Message types

| Type | Meaning | Reply |
|---|---|---|
| `0x02` | Disconnect (u32 code) | none |
| `0x03` | Heartbeat request | `0x04` (40 B) |
| `0x04` | Heartbeat reply | — |
| `0x64` | Authentication request | `0x65` (1250 B) + `0x09` (40 B) |
| `0x65` | Authentication reply | — |
| `0x67` | Match start (68 B) | none |
| `0x69` | Health check (36 B) | `0x3EB` (36 B) |
| `0x66`, `0x68` | **not present** in this client build | — |

### 6.3 Authentication reply (`0x65`)

| Field | Tag | Length | Content |
|---|---|---|---|
| 1 | 0 | 36 | player id |
| 2 | 1 | 1106 | access token (JWT) |
| 3 | 2 | 22 | product id |
| 4 | 3 | 36 | session id |

`26 + 4×6 + 36 + 1106 + 22 + 36 = 1250`.

Immediately after the reply, a 40-byte `0x09` "session auth" message is sent.

### 6.4 Heartbeat semantics

The reply echoes the 8-byte counter from the request verbatim (verified on 58/58 samples).
Returning a constant value causes silent protocol drift in clients that validate the counter.

### 6.5 Health check (`0x69` → `0x3EB`)

A handler exists in the client binary that accepts a single field: `tag 0, length 4, reasons
bitmask`. `mask == 0` maps to "success", otherwise "failure". Request and reply are both 36 bytes
(request carries `0xFFFFFFFF` as the field value).

### 6.6 Frame carving results

Scanning two process dumps with the 26-byte validator produced only:

```
0x02 total=26 fields=0 · 0x03 total=26 fields=0 · 0x04 total=26 fields=0
```

No `0x65`/`0x66`/`0x67` templates are resident in client memory; `0x65` is produced only in the
service → game direction.

---
