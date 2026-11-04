# Client Gates

**English** · [Türkçe](tr/06-client-gates.md)

> Restart-required formula, vgrl ordinals, Riot ID gate, product session.
>
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research; see the repository README for scope and legal notice.

## 7. Client dependency gating

### 7.1 "Restart required"

Disassembly shows two branches:

```
feature flag OFF:
    restartRequired = (vgk.StartType == SYSTEM_START) && (vgk.State != RUNNING)

feature flag ON:
    restartRequired = (VgrlQueryInstallStatus() == 2)
```

The value is **copied** from the dependency plugin's state (`[rbp+0x171] → out[0x1a1]`) rather
than computed at the call site, so there is no comparison to patch. Only the inputs can be made
consistent.

### 7.2 `vgrl` ordinal contract

The export table has `NumberOfNames = 0`; calls are made by ordinal.

| Ordinal | Meaning | Return values |
|---|---|---|
| 1342 | installation status | 0 error · 1 not installed · **2 installed** |
| 1343 | error text | string |
| 1344 | start service | bool |
| 1345 | restart-waived flags | bit0 on-demand · bit1 secure system · bit2 new install · bit3 on boot |
| 1346 | reset boot status | bool |

### 7.3 Riot ID gate

Launching the game without an active Riot ID is refused with **HTTP 467**
(`riot_id_required`). The client binary contains a developer flag that bypasses the check
(`--developer-skip-riot-id`); its presence is a fact, its use is outside this document's scope.

### 7.4 Product session

```
POST /product-session/v1/sessions
POST /product-session/v2/heartbeat/{id}
POST /product-session/v2/heartbeat-internal/{id}
POST /product-session/v1/session-heartbeats/{id}
POST /product-session/v1/external-sessions/{id}
GET  /product-session/v1/host-session/id
GET  /product-session/v1/data/path/<patchline>
```

Heartbeat interval is 60 s. A `product-session.<product>.300_sec.windows` string suggests a
300-second ceiling.

### 7.5 Session object

The platform session object has 23 fields. Two are frequently misread:

- `expiredTime` is **not** a reliable TTL: while connected it is either `0001-01-01` (unset) or
  stale from a previous connection, so `expiredTime − lastHeartbeatTime` can be negative.
  Measured real session lifetime: **646 s**.
- `isRestricted`, `restrictionType` and `shouldForceInvalidate` live in a separate layer; the
  session object does not carry restriction state.

### 7.6 Launch parameters (plaintext, from process memory)

```
-remoting-app-port=<port> -remoting-auth-token=<32 chars>
-patchline=live -subject=<player id> -ares-deployment=<region>
-config-endpoint=https://shared.<region>.a.pvp.net
-savetouserdir -culture=<locale>
-riotgamesapi-settings-token=<base64(JSON)>
```

The settings token contains an OAuth **authorization code and PKCE verifier**, which is how the
game obtains its own `valorant-client` token:

```json
{"rso_auth":{"authorization-key":"<b64({code, code_verifier})>"},
 "riotclient":{"app-port":"50900","auth-token":"<32 chars>"},
 "product-integration":{"heartbeat":"…heartbeat.json","lockfile":"…","settings":"…"}}
```

Token exchange: `grant_type=authorization_code&code=…&code_verifier=…&client_id=valorant-client`.
Codes are single-use; replaying a captured one returns `401 invalid_grant` (verified).

---
