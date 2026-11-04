# Vanguard Gateway — Reverse Engineering Notes

**English** · [Türkçe](README.tr.md)

> Defensive security research. Protocol documentation only; no bypass tooling.
> Using any of this violates the Riot Games Terms of Service and results in permanent bans.

**Start here:** [`docs/01-protocol.md`](docs/01-protocol.md)


## Documents

| File | Contents |
|---|---|
| [`docs/00-summary.md`](docs/00-summary.md) | Verified findings, scope, non-goals |
| [`docs/01-protocol.md`](docs/01-protocol.md) | Endpoints, headers, 26/2971-byte framing, envelope layout |
| [`docs/02-crypto.md`](docs/02-crypto.md) | RSA-OAEP (SHA-512), AES-256-GCM, `J0+1` counter rule, size identities |
| [`docs/03-auth-payload.md`](docs/03-auth-payload.md) | 11-field auth message, device identifier arithmetic, `ht` formula |
| [`docs/04-key-recovery.md`](docs/04-key-recovery.md) | Recovering the server RSA key from a live process; 401/400 oracle |
| [`docs/05-ipc-pipe.md`](docs/05-ipc-pipe.md) | 26-byte pipe frame, `0x64→0x65` (1250 B), heartbeat, health check |
| [`docs/06-client-gates.md`](docs/06-client-gates.md) | `restartRequired`, `vgrl` ordinals, Riot ID gate, product session |
| [`docs/07-detection.md`](docs/07-detection.md) | Enforcement classification and measured timing |
| [`docs/08-negative-results.md`](docs/08-negative-results.md) | 20 falsified hypotheses (do not repeat) |
| [`docs/09-methodology.md`](docs/09-methodology.md) | Techniques, verification rule, address hierarchy |
| [`docs/10-open-questions.md`](docs/10-open-questions.md) | Open items, withdrawn claims, limits |
| [`docs/11-reproducibility.md`](docs/11-reproducibility.md) | Reproduction notes |
| [`docs/12-glossary.md`](docs/12-glossary.md) | Terminology |
| [`schemas/vanguard.proto`](schemas/vanguard.proto) | **Verified** field numbers recovered from plaintext |
| [`data/measurements.md`](data/measurements.md) | Rate limits, timings, counters, oracle codes |
| [`reference/auth_build.py`](reference/auth_build.py) | Request builder + envelope round-trip (self-test) |
| [`reference/pipe_proto.py`](reference/pipe_proto.py) | IPC frame codec + reply builders (self-test) |
| [`reference/pipe_server.py`](reference/pipe_server.py) | Minimal Windows named-pipe server |
| [`reference/README.md`](reference/README.md) | Requirements, usage, and hard limits |

## Status

| Area | State |
|---|---|
| Wire format & envelope | solved, byte-exact |
| Cryptography (OAEP-SHA512 + AES-256-GCM) | solved, round-trip verified |
| Auth payload fields & device id | solved (two 64-byte parts: origin not determined) |
| Server public key | recoverable from live memory (oracle-verified) |
| IPC (pipe) protocol | solved, 62/62 messages |
| Client dependency gates | solved (two formulas) |
| Virtualized section CFG | not statically recoverable (measured, §09/§10) |
| Integrity fields `htt`/`gg` | validation confirmed, derivation unknown |

## Legal

Riot Games Terms of Service prohibit client modification and reverse engineering for the purpose
of circumventing anti-cheat. This material is published for defensive research and protocol
education. No credentials, session keys, or account identifiers are included.
