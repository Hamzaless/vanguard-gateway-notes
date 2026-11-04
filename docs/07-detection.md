# Detection

**English** · [Türkçe](tr/07-detection.md)

> Ban classification and measured timing (with sample-size caveats).
>
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research; see the repository README for scope and legal notice.

## 8. Detection and enforcement

### 8.1 Classification

Account state is readable from the RSO `userinfo` endpoint:

```
TIME_BAN       reason=THIRD_PARTY_TOOLS  scope=<product>   expires 14 days
PERMANENT_BAN  reason=THIRD_PARTY_TOOLS  scope=<product>   permanent
```

The client's own localization catalogue contains the whole taxonomy, in which
`VANGUARD_BYPASS` is a **separate** category from `THIRD_PARTY_TOOLS`.

### 8.2 Causal measurement

| Observation | Result |
|---|---|
| Time the ban was issued (expiry − 14 days) | coincides with the authentication attempts |
| Accounts that sent an authentication request | 8 of 8 banned, +0.5 s … +2.7 s |
| Sessions that never sent one | 3 of 3 unaffected |

**Caveat:** these are small samples (8 and 3) from a single environment. They support the
hypothesis that sending the authentication request is sufficient on its own; they do not prove
a rate for the general population.

### 8.3 Observable client traces (measured, not inferred)

| Trace | Evidence |
|---|---|
| Service definition carries an environment variable pointing at a non-standard directory | service registry `Environment` value |
| Machine-wide `SSL_CERT_FILE` / `SSL_KEYLOGFILE` style variables | present in the Riot process environment block |
| Service binary has no version resource | client reads `0.0.0.0` |
| Kernel driver not present in the signature catalogue | client log message |
| Device identifier derived from a secret not available in user mode | §4.2 |

These are the traces that a detection system can observe without kernel instrumentation.

---
