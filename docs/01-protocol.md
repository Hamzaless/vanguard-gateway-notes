# Protocol

**English** · [Türkçe](tr/01-protocol.md)

> Wire protocol: endpoints, headers, frame, envelope, message types.
>
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research; see the repository README for scope and legal notice.

## 2. Protocol

### 2.1 Endpoints

```
POST https://<region>.vg.ac.pvp.net:8443/vanguard/v1/gateway
POST https://<region>2.vg.ac.pvp.net:443/vanguard/v1/gateway
GET  https://config.vg.ac.pvp.net/config/production.rito
```

Two edge deployments are used: a CDN-backed host on port 8443 and a cloud-hosted host on 443.
Observed authentication traffic in this environment went to the second one.

### 2.2 Request headers

```http
User-Agent: vanguard/<version>
Content-Type: application/x-protobuf
Accept: */*
X-VG-1: <action>          # 3 = auth, 4 = access, 7 = heartbeat, 9 = task result
X-VG-2: <player id>
X-VG-3: 1
X-VG-4: <product id>      # present on some actions
Content-Length: <n>
```

### 2.3 Frame

```
08 <type> 12 <varint length> <envelope> 18 01
```

Measured examples: request `f1=3, f2=2971, f3=1`; response `f1=5, f2=8204`.

### 2.4 Envelope

| Offset | Size | Field |
|---|---|---|
| 0 | 4 | magic `52 47 01 00` (`RG\x01\x00`) |
| 4 | 256 | RSA block (2048-bit, OAEP-SHA512) |
| 260 | 12 | nonce |
| 272 | n | AES-256-GCM ciphertext |
| 272+n | 16 | GCM tag |

Verified size identity: `4 + 256 + 12 + 2683 + 16 = 2971` for a 2683-byte plaintext.

### 2.5 Message types

| Type | Meaning | Reply |
|---|---|---|
| 3 | AuthenticationRequest | 5 (TokenResponse) |
| 4 | AccessRequest | 4 (TokenResponse) |
| 7 | Heartbeat | 8 (HeartbeatResponse) |
| 9 | TaskResult | 11 (ack) |

---
