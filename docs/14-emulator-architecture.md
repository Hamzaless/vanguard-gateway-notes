# Emulator architecture (what replaces what)

**English** · [Türkçe](tr/14-emulator-architecture.md)

> Reference architecture of a client-side emulator: which component substitutes which native
> component, and what each substitution can and cannot achieve.
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research only.

## 14.1 Component map

| Native component | What it does | Substitute | Limits |
|---|---|---|---|
| `vgc.exe` (service) | owns the IPC pipe, wraps gateway traffic, decrypts task modules | IPC pipe server (`reference/pipe_server.py` pattern) | cannot produce accepted gateway auth (§14.4) |
| `vgk.sys` (driver) | produces device identifier parts, boot seed, HMAC, signature/health evidence | driver that answers the IOCTL contract | values it returns are not the values the real driver would return |
| `vgrl.dll` | dependency status for the launcher (ordinals 1342–1346) | ordinal-only shim DLL | only affects gating, not enforcement |
| Riot Client dependency check | decides "installed / restart required" | consistent registry + service state | formula is input-driven, not patchable |
| gateway session | verifies identity, issues rotated keys | none | requires the kernel-side evidence |

## 14.2 What the driver is asked for

The IPC/IOCTL contract observed from the client side:

| Code | Purpose |
|---|---|
| `0x22C000` | disk identifiers: `u32 count` + `"C:\Serial: <serial>.<model>\0"` × N (5 slots, 485 B) |
| `0x22C028` | driver version string |
| `0x22C034` | heartbeat payload (`0x03`/`0x67` data) |
| `0x22C03C` | handshake |
| `0x22C04C` | optional query; real driver answers `0xC0000002` and the client proceeds |
| `0x22C0xx` | 88 accepted codes in total (whitelist is a plaintext switch in the real driver) |

Additionally the client reads a **boot status stamp** file (one byte `0x01`) and a set of
IOCTL-derived values used inside the device identifier:

```
#9   boot seed (16 B)
#11  SHA-512 block  -> device id part p2 (64 B)
#12  SHA-512 block  -> device id part p3 (64 B)
#18  HMAC-SHA1      -> integrity field ht
```

**This is the hard limit.** p2/p3 are produced inside the driver from a secret that never reaches
user mode. A substitute driver can return *stable* values (enough to keep a client happy locally)
but they are not the values the real driver would return for that hardware, and the server
compares/ties them to telemetry.

## 14.3 What the pipe server must answer

```
0x64 -> 0x65 (1250 B: player id, token, product, session id) then 0x09 (40 B)
0x03 -> 0x04 (40 B, counter echoed)
0x69 -> 0x3EB (36 B, reasons = 0)
0x02, 0x67, unknown -> no reply
```

Exact byte layouts are in `05-ipc-pipe.md`; a working encoder is in `reference/pipe_proto.py`
(self-test asserts 1250/40/36/40).

## 14.4 What cannot be substituted

1. **Gateway authentication.** The RSA block is wrapped with the server key (recoverable, §5) but
   the plaintext carries p2/p3 and `ht`/`htt`/`gg`. p2/p3 cannot be forged, and sending a request
   that fails these checks is itself a detection signal (measured: bans in 0.5–2.7 s, §7).
2. **Attestation.** No user-mode component can produce it.
3. **Session eligibility.** The platform decides; the client can only present state.

## 14.5 Practical consequence

A client-side emulator can make the **local** view consistent: the game sees a healthy pipe, a
present driver, a running service, and a launchable product. That is enough to start the game and
to keep the local session object alive for a while.

It is **not** enough to keep the platform session alive indefinitely: the observed ceiling was
646 s, and the 429 budget (2–3 auths per 15 min) is shorter than the session lifetime. The two
constraints cross, which means continuous operation is not achievable client-side.

## 14.6 Ethics

Everything above is protocol analysis. Building or running such a substitute violates the Riot
Games Terms of Service and results in permanent bans; it also degrades the game for other players.
