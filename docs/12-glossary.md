# Glossary

**English** · [Türkçe](tr/12-glossary.md)


| Term | Meaning |
|---|---|
| Envelope | magic ‖ RSA-wrapped key ‖ nonce ‖ AES-GCM ciphertext ‖ tag |
| Device identifier | 6-part hardware fingerprint (`‖1;…`) |
| `ht` | SHA-1 integrity field over device identifier + version |
| `htt`, `gg` | Additional integrity fields (validation confirmed, derivation unknown) |
| Oracle | querying the real server and reading the status code as a verdict |
| Virtual section | MBA-obfuscated, virtualized code section |
| Context | virtual register file + flags (536 bytes) |
| Dispatcher | code that computes an indirect branch target; here register-dependent |
| MBA | mixed boolean-arithmetic expression |
| Product session | Riot Client ownership record for a launched product |
| Attestation | hardware evidence produced in kernel mode |
