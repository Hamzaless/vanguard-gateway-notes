# Additional findings

**English** · [Türkçe](tr/16-additional-findings.md)

> Material recovered from the project archive that did not fit the earlier documents:
> integrity field `gg`, VAN/VAL error codes, IOCTL handler structure, task acknowledgement policy.
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research only.

## 16.1 Integrity field `gg`

`gg` is 20 bytes, base64 encoded to 28 characters, carried in `f15` next to `htt` and `ht`.

Measured properties:

| Property | Result |
|---|---|
| Server validates it | original `gg` → **200** (TokenResponse decrypted, 7888 B); random 20 B → **400** |
| Bound to device identifier | no — rotating the device identity does not invalidate it |
| Bound to token / session id | no |
| Stable per installation | yes |
| Derivation | **not found**: 22,178 offline combinations + 3,669,312 RAM-window hashes, 0 matches |

Consequence for any client-side reproduction: `gg` must be **replayed verbatim**. Generating or
randomising it breaks the request. This is an operational constraint, not a preference.

The archive search also produced 6 hits inside a physical memory image; 2 were real authentication
payloads, 4 were false positives (same byte pattern in unrelated heap).

## 16.2 `htt` — leaked model does not fit

The leaked `GenerateF16Fields` implementation proposes:

```
htt_input = player_id + decode(ht) + meta12 + secret16
htt       = base64( SHA1(htt_input) || meta12 )
```

Nine variants were tested (player id as session id / token subject / session id without dashes,
three orderings each). None matched the observed `htt`. At least one input component is different.

`ht` itself was reproduced exactly:

```
SHA1("6;"+p6 + "1;"+p1 + "2;"+p2 + "3;"+p3 + "5;"+p5 + "1.19.1.18" + MAGIC16)
→ 8e7a6f2c3ee27f1218dd43fd27ce099d78ca3a83   (matches f15["ht"])
```

Six variants (decoded parts, hex-string constant, no constant) did not match, so the input is the
literal concatenation shown above.

## 16.3 VAN / VAL error codes

`VAN nnn` strings are **not** present as literals in the client binaries. The mapping used in the
field therefore comes from user reports, not from the binary.

Working hypothesis, not confirmed: `VAN nnn` is the **low byte of an NTSTATUS** returned by the
driver. Example: `0xE0000098` → `0x98` = 152, matching a reported `VAN 152`. The same arithmetic
gives `0xE0002745` → `0x45` = 69.

`VAL 5` maps to `PlatformFaulted` on the game side. `EPlatformFaultReason` has 13 values; the enum
was recovered from two independent sources (game binary and log strings). `VAL 5` is produced by the
game after the platform session fails, not by the gateway.

## 16.4 IOCTL handler structure

The driver's device-control dispatch was partially recovered:

- The **computed jumps are statically solvable**. Rule: `target = site + 7 + d1 − d2` for the
  `lea/lea/jmp` pattern. Verified on 15 of 15 continuation blocks, then on the wider set.
- The 15 blocks that were assumed to be handlers are **nodes of a search chain**, not handlers.
  The chain runs upward; 13 of 15 links were measured.
- The real handler sits on the `je` (equality) branch of the comparison, not on the fall-through.
- `0x22C000` (disk serials) handler was reconstructed line by line; the reply layout is
  `u32 count` followed by `"C:\Serial: <serial>.<model>\0"` entries, 5 slots, 485 bytes total.
- The virtual context frame is referenced as `[rsp+0x228]` inside the lifted code.

Obfuscator idioms observed in the lifted code:

| Idiom | Appearance |
|---|---|
| address hiding | `lea rax,[rip+d]` then arithmetic on the result before use |
| constant division | magic multiply + shift instead of `div` |
| mask constants | `0xF0F0F0F0…`, `0x1E1E1E1E…`, `0x87878787…`, `0x33333333…` |

None of these can be resolved by pattern matching; the address forms require evaluating the
arithmetic with live register values (§10 of the protocol notes).

## 16.5 Task acknowledgement policy

Measured A/B on the same session:

| Acknowledgement sent | Next heartbeat |
|---|---|
| 0 | 200 |
| 1 (real task id, fake hashes) | 200 |
| 4–5 (fake hashes) | **401** — session dropped |

Sending an acknowledgement with fabricated module hashes ends the session. Not acknowledging leaves
the session alive; the server withdraws the tasks on a later heartbeat (payload shrinks from ~68 MB
to ~35 MB). Practical rule: do not acknowledge task results that were not actually executed.

## 16.6 What this adds to the earlier documents

- `gg` is validated and installation-stable, so it is a replay-only value (§5 of the auth document
  should be read with this in mind).
- `htt` derivation remains unknown, and the leaked implementation is not the one in use.
- VAN codes are a mapping hypothesis, not a decoded table.
- Driver dispatch is partly readable: computed jumps resolve, handler boundaries do not follow the
  obvious layout.
- Task acknowledgements are a session-lifetime lever, independent of authentication.

## 16.7 IPC message inventory (full archive)

Counts over the complete captured set (lifetime of the archive, not one session):

| Type | Name | Samples | Size | Fields |
|---|---|---|---|---|
| `0x03` | HeartbeatSyn | 275 | 40 | 1 |
| `0x04` | HeartbeatAck | 2 | 40 | 1 |
| `0x64` | Connect | 36 | 103 | 2 |
| `0x65` | Login | 32 | 1250 | 4 |
| `0x67` | MatchStart | 23 | 68 | 1 |

Not present in real traffic: `0x02` (disconnect), `0x66`, `0x68`.

`0x03` counter values: min 1, max 58, 58 distinct values across 275 samples. The counter is
per-connection and resets, which is why an earlier session showed 58 messages with counters 1..58.

## 16.8 vgc log message codes and session outcomes

The service writes numbered log records. Record `191` has the form `IOCTL code ; NTSTATUS`; across
62 decrypted logs the only value observed is:

```
191: 0022C04C ; c0000002
```

So at runtime the client issues exactly one IOCTL code (`0x22C04C`), which the real driver rejects
with `STATUS_NOT_IMPLEMENTED`, and the client continues. The 88-code whitelist of the driver is a
separate, static surface.

Three distinct session outcomes appear in the same build:

```
200 : 0 108 286 58 52 54 16 286 90 141 181 91 67 191 155 208×5 70 71 72 71 69 164 79 80 160 …
403 : 0 108 286 58 52 54 16 286 90 141 181 91 67 191 155 208×5 70 71 68 192 16 27 28 286
dead: 0 108 218 16 27 28 286
```

The sequence diverges at record 72/68 and 218, i.e. after the gateway exchange. A dead session never
reaches the gateway records.

## 16.9 vgk startup checklist

The driver writes a deterministic 37-step startup sequence. Two facts are useful:

- Some steps return `STATUS_NOT_IMPLEMENTED` (`0xC0000002`) and the client continues; these steps are
  optional from the client's point of view (`0x22C04C` is one of them).
- When the service dies, the last record in the driver log identifies the stage. Observed codes:
  `0xC0000365` (driver entry failed), `0xC0000429` (not capable), plus a clean exit path.

For analysis this means: a missing driver is distinguishable from a driver that loads and then
fails, by the last record and the exit code, not by the service state alone.

## 16.10 Platform fault taxonomy

Two failure names appear in the game log and they are not interchangeable:

| | `SessionRefreshFail` | `VanguardFail` |
|---|---|---|
| occurrences | 8 | 6 |
| accompanied by `Platform Faulted: 5` | 8/8, same millisecond | 0/6 |
| followed by `we were kicked` | 3/8 (9–34 ms later) | 0/6 |
| preceded by an HTTP error | no | no |

`VAL 5` is produced by `SessionRefreshFail`. `VanguardFail` is a different path and does not raise
`VAL 5`. Conflating the two leads to wrong conclusions about which component failed.

## 16.11 Ban timeline method

Ban moments can be dated from the RMS push that carries the restriction. Three cases had a captured
push with a server timestamp, which gives the issue time to the second; the emulator state at that
second is known from the same session log. Cases without a captured push are marked as inferred and
carry lower confidence.

Control group: sessions that never sent an authentication request produced no ban — 3 of 3 in the
same environment.

## 16.12 RTTI inventory (method reference)

The full type-descriptor / Complete Object Locator / vtable inventory was extracted for the
CryptoPP classes used by the client (OAEP variants, RSAFunction, GCM_Final, integer and hash
primitives). This is what makes the key-recovery method in `04-key-recovery.md` reproducible: the
descriptors give class identity, the COL gives the vtable, and the live object is found by searching
for that vtable pointer.

The inventory is machine-specific: addresses shift per build. Only the chain (name → TD → COL →
vtable → object) is stable.
