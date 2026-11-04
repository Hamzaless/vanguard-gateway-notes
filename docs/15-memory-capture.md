# Live memory capture and analysis

**English** · [Türkçe](tr/15-memory-capture.md)

> How the memory images used in this research were taken, what each method costs, and how to
> analyse them. Written so the measurements in this repository can be reproduced.
> Part of the *Vanguard Gateway — Reverse Engineering Notes*. Defensive research only.

## 15.1 Why memory at all

Two values cannot be obtained from disk:

1. the plaintext of a request (assembled at runtime, then encrypted);
2. runtime-decrypted code pages (the virtualized section is packed on disk).

Everything else in this repository was recovered from captured traffic or static analysis. Memory
was used for the remaining two, plus for locating the CryptoPP key objects (§5).

## 15.2 Method A — per-process dump (preferred when it works)

Windows exposes a process snapshot without any driver:

```
OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION)
VirtualQueryEx   -> enumerate regions (base, size, protection, state)
ReadProcessMemory -> copy readable regions in 1 MB chunks
```

Output of this work:

```
vgc_<n>_HHMMSS.raw     flat file, regions concatenated in address order
memmap.txt             one line per region: 0x<virtual base> 0x<0> 0x<size> 0x<file offset> <name>
```

`memmap.txt` is what makes the dump usable: every 8-byte value in the file can be mapped back to a
virtual address, so pointers found inside the image can be followed.

**Cost:** one pass over the process private memory; for a 2.9 GB process, a few seconds.
Several samples per second are possible when the target is small.

**Failure mode:** protected processes (PPL) reject `OpenProcess` with `PROCESS_VM_READ`. In that
case `ReadProcessMemory` returns zero bytes for every region even when the handle opens. Error codes
seen: `-3` (open failed), `-4` (no readable regions), `-5` (open ok, reads returned 0).

## 15.3 Method B — physical memory image

When the process is protected, capture the physical address space:

```
winpmem_x64 (signed) -> \\.\pmem  ->  ram.raw
```

**Cost:** 33 GiB for 32 GB of RAM; 10–25 minutes on a laptop SSD. The file is a raw physical map,
so virtual addresses must be reconstructed with a page-table walk or with a memory forensics tool
(Volatility `windows.memmap` per process, which also produces a `memmap` log).

**Caveat:** this is a snapshot of physical frames, not of a process. Pages that were paged out at
capture time are missing, and encrypted/trimmed pages stay encrypted.

## 15.4 Method C — crash dump (last resort)

If the target cannot be read and cannot be paused, a complete crash dump forces the kernel to write
all of RAM:

```
HKLM\SYSTEM\CurrentControlSet\Control\CrashControl
    CrashDumpEnabled = 1            (complete memory dump)
    DedicatedDumpFile = C:\dedicateddump.sys
    AlwaysKeepMemoryDump = 1

trigger: NtRaiseHardError(0xC0000420, OptionShutdownSystem)
         or  RtlSetProcessIsCritical + TerminateProcess
         or  CrashOnCtrlScroll (requires reboot to take effect)
```

**Cost:** 30+ GB write, a reboot, and a few minutes of downtime. `CrashOnCtrlScroll` does not work
until the machine has rebooted after the registry change. `NtRaiseHardError` may return without a
bugcheck on some configurations; the `RtlSetProcessIsCritical` path is more reliable.

**When it was useful here:** never for the gateway key (the session key is zeroized in under a
minute), but it is the only way to capture a *protected* process at a chosen moment.

## 15.5 Method D — existing minidumps

Windows writes a small dump into the process crash folder:

```
%LOCALAPPDATA%\CrashDumps\<image>.<pid>.dmp          (here: 3.5–4.2 MB each)
```

Nine of these existed for the anti-cheat service. They contain thread stacks and a small module
list, no heap. Parsing them is cheap (`MINIDUMP_MEMORY64_LIST`), but they only answer "where was the
thread", not "what was in memory".

## 15.6 Method E — virtual machine pause (not used, recommended)

Run the component inside a VM, pause it at the moment of interest, then dump guest RAM from the
hypervisor:

```
(qemu) stop
(qemu) pmemsave 0 <size> guest.raw
```

This is the only method that gives an **atomic** snapshot: no sampling gap, no cooperative
behaviour from the target. The cost is the VM setup and the fact that some software refuses to run
in a virtual machine.

## 15.7 Turning a dump into answers

### 15.7.1 Address mapping

```python
regions = []          # from memmap.txt
def read_va(fh, va, n):
    for base, size, off in regions:
        if base <= va < base + size:
            fh.seek(off + (va - base))
            return fh.read(min(n, base + size - va))
    return b""
```

Never index the flat file by virtual address directly; the file is a concatenation, not a VA map.

### 15.7.2 Strings

```bash
strings -a -n 10 vgc.raw | sort -u > strings.txt
```

Two traps:

- **Dictionary false positives.** A word like `gobbledygook` appears in an embedded English word
  list, which looks like a device name until you check the neighbours. Always print ±200 bytes of
  context before believing a hit.
- **Escaped payloads.** JSON carried inside logs is stored with `\"` escapes; plain `grep '"'`
  misses it. Search for the unescaped form as well.

### 15.7.3 Carving images and structures

- **PE images:** `MZ` + `0x40 ≤ e_lfanew < 0x400` + `PE\0\0` + valid section count. 315 images were
  carved from an 11.3 GB dump; the target module was not among them, which is itself a result.
- **IPC frames:** validate rather than search. A frame is `[u32 type][u32 total][u16 fields][16×0]`
  followed by `[u16 tag][u32 len][data]` entries that must sum exactly to `total`. This validator
  found three frames and rejected thousands of look-alikes.
- **Entropy:** 4 KiB blocks, Shannon entropy `H = −Σ p·log2 p`; printable ratio below 0.85 filters
  string regions. Values around 8.000 with zero repeated 16-byte blocks over hundreds of KB mean
  random or stream-encrypted data, not compression.

### 15.7.4 Confirming a hit

A plaintext found in memory is only a claim until it is matched against captured bytes. In this work
the check was:

```
memory:   plaintext at one address, envelope 0x1370 bytes later, ciphertext right after it
capture:  same envelope magic, same nonce, same ciphertext
=> the plaintext belongs to the captured request
```

Without that triple match, a string that "looks like a request" proves nothing.

## 15.8 What memory capture did **not** give

| Target | Result |
|---|---|
| session key (32 B) | absent — zeroized within ~50 s; full RAM scan negative |
| server public key | absent from static dumps; present only as a live CryptoPP object in a running process |
| virtualized code | absent from a 33 GiB physical image (0 signature hits) — process was not running |
| live execution context | absent from idle dumps; needs capture at the moment of use (§15.6) |

## 15.9 Practical checklist

```
1. decide the question (plaintext? code? structure?)
2. prefer Method A (process dump) - cheap, repeatable, gives memmap
3. if protected -> Method B (physical) + page-table walk
4. if timing-critical -> Method E (VM pause), not C
5. always validate structures with a validator, never with a substring
6. confirm every hit against captured traffic
7. record offsets and sizes in the notes; a hit without an offset is not reproducible
```

## 15.10 Ethics

Capturing memory of software you do not own may violate local law and the product's terms.
Everything here was done on a machine owned by the author, for analysis of that machine's own
traffic. Do not apply these techniques to third-party systems.
