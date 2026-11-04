# Methodology

**English** · [Türkçe](tr/09-methodology.md)

> Techniques, verification rule, address hierarchy, offset arithmetic.
>
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research; see the repository README for scope and legal notice.

## 10. Methodology

| Technique | Use |
|---|---|
| Static analysis | section mapping, RTTI/type-descriptor extraction, RVA→file offset, disassembly |
| Dynamic instrumentation | emulation, symbolic execution (SMT), instruction tracing |
| Memory forensics | physical RAM image, per-process memory map, page-table walk |
| Protocol testing | controlled "oracle" requests, status-code discrimination |
| Network observation | TLS key log, packet capture, local redirection |
| Differential testing | generated code vs reference executor, state comparison |

**Verification rule used throughout:** every claim is supported by two independent methods,
and a claim is withdrawn when a measurement contradicts it. Two examples of withdrawn claims
are recorded in §11.

### 10.1 Address verification hierarchy

```
1. real exception directory (.pdata equivalent) — exact match
2. runtime execution trace — does the call actually go there
3. RTTI chain (TD → COL → vtable → live vptr)
4. cross-reference (RIP-relative) — weak on its own
5. byte signature — for searching only, never for confirmation
```

### 10.2 Offset arithmetic (the most expensive bug)

The virtualized section does not have `RVA == file offset`:

```
.grfn1: VirtualAddress = 0x5EB000 , PointerToRawData = 0x5DC600 , Δ = 0xEA00
correct: offset = PointerToRawData + (RVA − VirtualAddress)
wrong:   offset = RVA            → 0xEA00-shifted bytes, "desynchronized" garbage
```

Reading a section without validating `VA ≤ RVA < VA + SizeOfRawData` silently produces plausible
nonsense; a strict check is mandatory.

---
