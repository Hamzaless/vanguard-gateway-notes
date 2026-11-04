# RMS — the session carrier

**English** · [Türkçe](tr/13-rms.md)

> What RMS is, what it carries, and why it matters for session lifetime.
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research.

## 13.1 What it is

RMS (Riot Messaging Service) is a **WebSocket push channel** that carries platform state to the
client. It is not the anti-cheat gateway; it is the transport over which session/party state
changes arrive.

```
wss://<region>.edge.rms.si.riotgames.com/rms/v1/session?token=<token>
```

The client opens the socket at start-up, subscribes to resource prefixes, and receives JSON
envelopes.

## 13.2 Envelope

```json
{"payload": {"resource": "ares-session/v1/sessions/<player id>",
             "service":  "session",
             "timestamp": 1793819627653,
             "payload":  "<escaped JSON string>",
             "version":  "5"},
 "ts": 1793819627.653,
 "subject": "rms:message",
 "type": "push"}
```

The inner `payload` is an **escaped JSON string**; naive grep tools miss it because the quotes are
backslash-escaped inside a log line.

## 13.3 What arrives on it

| Resource | Meaning |
|---|---|
| `ares-session/v1/sessions/<id>` | session state (`CONNECTED` / `CLOSED`), heartbeat time, loop state |
| `ares-parties/parties/v1/parties/<id>` | party membership changes |
| `ares-parties/players/<id>` | player removed / added |
| `ares-core-game/core-game/v1/matches/<id>` | match lifecycle |

Only the first two were observed changing in the studied sessions.

## 13.4 Observed session timeline

```
714.851  RMS: ares-core-game … matches/<id>
714.855  RMS: ares-session … serviceState = CONNECTED
715.499  product-session: Gameplay → Idle        (after 393 s of gameplay)
738.202  RMS: ares-parties/parties/v1/parties/<id>
738.930  RMS: ares-session … serviceState = CLOSED
738.933  RMS: ares-parties/players/<player id>  (player removed from party)
769      game client: "Platform Faulted: 5 / SessionRefreshFail"
```

The session was closed by the **server** ~24 s after the client left gameplay; the party was
cleaned 3 ms later; the game reported the failure 30 s after that.

## 13.5 What RMS does **not** carry

In every observed session push, the payload contained **no** Vanguard field, no attestation
result, and no anti-cheat state:

```
"isRestricted": false, "restrictionType": "", "shouldForceInvalidate": false
```

Restriction/attestation state lives in a different layer (launch restriction / gateway).

## 13.6 Pinning

The game binary contains a `PinnedPublicKeys` mechanism, but the only host observed inside that
configuration is the shared config endpoint. No pin entry for the RMS host was found in the
analysed binaries. This is a **static observation**, not a live test: an untested assumption is
that RMS itself is not pinned. Treat it as unverified.

## 13.7 Why it matters

- A session does not die because heartbeats are missed (measured: last heartbeat 22 s before the
  close, interval 60 s).
- It dies because the server pushes `CLOSED`.
- Therefore, keeping the socket "healthy" is not sufficient by itself; the platform must also
  consider the client eligible. That eligibility is what the gateway/launch-restriction layer
  decides.
