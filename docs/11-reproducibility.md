# Reproducibility

**English** · [Türkçe](tr/11-reproducibility.md)

> Operational notes for reproducing the measurements.
>
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research; see the repository README for scope and legal notice.

## 12. Reproducibility notes

- Oracle results are read from status codes only; no side effects.
- Protocol tests must be sequential on a single connection; concurrent connections break
  counter-echo behaviour.
- Physical memory images must be taken while the target process is **active**; otherwise the
  virtualized pages are absent (verified: 0 signature hits in a 33 GB image).
- Apply the GCM counter rule (`J0+1`) in every key search, or the correct key is discarded.
- When mapping addresses, validate the section range before reading (see §10.2).

---
