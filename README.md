# Vanguard Gateway — Reverse Engineering Notes

Wire protocol, cryptography, IPC framing and client dependency gating for the Vanguard
client stack (vgc / vgk). Target versions: Vanguard 1.19.1.x, VALORANT release-13.09.

**English** · [Türkçe](README.tr.md)

Defensive security research. Protocol documentation only, no bypass tooling.
Using this material violates the Riot Games Terms of Service and results in permanent bans.
No account identifiers, credentials or session keys are included.

## Documents

| File | Contents |
|---|---|
| [docs/00-summary.md](docs/00-summary.md) | Verified findings, scope, non-goals |
| [docs/01-protocol.md](docs/01-protocol.md) | Endpoints, headers, frame, envelope layout |
| [docs/02-crypto.md](docs/02-crypto.md) | RSA-OAEP (SHA-512), AES-256-GCM, `J0+1` counter rule |
| [docs/03-auth-payload.md](docs/03-auth-payload.md) | Auth message fields, device identifier, `ht` |
| [docs/04-key-recovery.md](docs/04-key-recovery.md) | Recovering the server RSA key from a live process |
| [docs/05-ipc-pipe.md](docs/05-ipc-pipe.md) | 26-byte IPC frame, message types, replies |
| [docs/06-client-gates.md](docs/06-client-gates.md) | `restartRequired`, vgrl ordinals, Riot ID gate, product session |
| [docs/07-detection.md](docs/07-detection.md) | Ban classification and measured timing |
| [docs/08-negative-results.md](docs/08-negative-results.md) | 20 falsified hypotheses |
| [docs/09-methodology.md](docs/09-methodology.md) | Techniques, verification rule, address hierarchy |
| [docs/10-open-questions.md](docs/10-open-questions.md) | Open items, withdrawn claims |
| [docs/11-reproducibility.md](docs/11-reproducibility.md) | Reproduction notes |
| [docs/12-glossary.md](docs/12-glossary.md) | Terminology |
| [docs/13-rms.md](docs/13-rms.md) | RMS session carrier |
| [docs/14-emulator-architecture.md](docs/14-emulator-architecture.md) | Component substitution and its limits |
| [docs/VERIFICATION.md](docs/VERIFICATION.md) | Claim-by-claim verification |
| [schemas/vanguard.proto](schemas/vanguard.proto) | Field numbers recovered from traffic |
| [data/measurements.md](data/measurements.md) | Rate limits, timings, counters |
| [data/knowledge.json](data/knowledge.json) | Machine-readable knowledge base |
| [reference/](reference/) | Working reference code (request builder, IPC codec, pipe server) |

Turkish translations live under `docs/tr/`.

## Status

| Area | State |
|---|---|
| Wire format, envelope | solved, byte-exact |
| Cryptography | solved, round-trip verified |
| Auth fields, device identifier | solved except p2/p3 derivation (kernel-only) |
| Server public key | recoverable from live memory, oracle-verified |
| IPC protocol | solved, 62/62 messages |
| Client dependency gates | solved |
| RMS session carrier | mapped, close behaviour measured |
| Virtualized section CFG | not statically recoverable |
| `htt` / `gg` | validation confirmed, derivation unknown |

## Reference code

```bash
python3 reference/run_all.py     # offline self-tests, no network
```

## Legal

Riot Games prohibits client modification and anti-cheat circumvention. This material is published
for defensive research and protocol education. No credentials, session keys or account identifiers
are included.

MIT licensed.
