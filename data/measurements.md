# Measurement tables


### A.1 Oracle status codes

| Code | Meaning |
|---|---|
| 200 | accepted, session established |
| 400 | envelope/protobuf could not be opened |
| 401 | envelope opened, token invalid or expired |
| 403 | envelope opened, account restricted |
| 429 | rate limited |

### A.2 Rate limit

```
consecutive requests, same device identity : 200 · 200 · 429 · 429 · 429 · 429
⇒ 2 requests / ~15 minutes
```

### A.3 Timings

| Quantity | Value |
|---|---|
| Client heartbeat cadence | 90 s (62 sessions) |
| Server session lifetime (observed max) | 646 s |
| Session TTL around | ~192 s |
| Product-session heartbeat | 60 s (300 s ceiling) |

### A.4 Message counters (single session)

```
inbound : 0x64 ×2 · 0x65 ×2 · 0x03 ×74 · 0x67 ×1
outbound: 0x04 ×74
```

### A.5 Authentication reply size

```
26 + 4×6 + 36 + 1106 + 22 + 36 = 1250 bytes
```

---
