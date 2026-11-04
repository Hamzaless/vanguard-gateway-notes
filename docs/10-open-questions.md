# Open Questions

**English** · [Türkçe](tr/10-open-questions.md)

> Unresolved items, withdrawn claims, and what cannot be concluded.
>
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research; see the repository README for scope and legal notice.

## 11. Limitations and open questions

### 11.1 Open questions (not guessed in this document)

1. **Derivation inside p2/p3.** The values are outputs of the kernel driver (IOCTL #11 and #12,
   64-byte SHA-512 blocks) and are stable across sessions. What the driver mixes into them — a
   build-time secret, a TPM value, or a combination — is **not** determined.
2. **Derivation of `htt` and `gg`.** Validation is confirmed (random values are rejected), the
   formula is not known; ~1.3 M structural combinations failed.
3. **Module payload cipher.** Not a static key, not a simple wrap, not a known container. The
   plaintext is only obtainable where the key exists.
4. **Virtual section control flow.** Targets depend on live register state; static recovery was
   shown impossible under this threat model, not merely difficult.
5. **Session lifetime cap.** 646 s observed; the mechanism (server-side enforcement) was not
   isolated.

### 11.2 Claims withdrawn during the work

- *"`expiredTime − lastHeartbeatTime` is a TTL metric."* Withdrawn: values are unset or stale
  while connected; the metric is meaningless in that state.
- *"Restart-required correlates with session survival."* Withdrawn: the sample was confounded —
  the sessions that survived had never entered matchmaking.

Recording withdrawn claims is part of the method: it prevents building on them.

### 11.3 What cannot be concluded

Nothing in this document shows how to obtain a persistent, unbanned session. The measurements
indicate the opposite: authentication is verified against evidence generated outside user mode,
and sending it is itself a detectable, enforced signal.

---
