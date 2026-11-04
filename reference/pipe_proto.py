"""
Vanguard SDK — IPC (named pipe) frame codec  ·  REFERENCE / EDUCATIONAL
=======================================================================

Wire format (verified against 62 captured messages):

    [u32 type][u32 total][u16 field_count][16 x 0x00]      = 26-byte header
    repeated: [u16 tag][u32 length][data]                  = 6 + length
    total   = 26 + sum(6 + length)

Message types observed in the client:
    0x02 disconnect (u32 code)      -> no reply
    0x03 heartbeat request          -> 0x04 (40 B, counter echoed)
    0x64 authentication request     -> 0x65 (1250 B) then 0x09 (40 B)
    0x67 match start (68 B)         -> no reply
    0x69 health check (36 B)        -> 0x3EB (36 B, reasons bitmask)
    0x66 / 0x68                     -> not produced by this client build

No account data is included. This module only encodes/decodes bytes.
"""
import struct

HEADER = struct.Struct("<IIH16x")
FIELD = struct.Struct("<HI")

DISCONNECT, HEARTBEAT_SYN, HEARTBEAT_ACK = 0x02, 0x03, 0x04
CONNECT, LOGIN, MATCH_START = 0x64, 0x65, 0x67
HEALTH_REQ, HEALTH_RESP = 0x69, 0x3EB
SESSION_AUTH = 0x09


def build(msg_type: int, fields=()) -> bytes:
    """fields = [(tag, bytes), ...]. total = 26 + sum(6 + len)."""
    total = HEADER.size + sum(FIELD.size + len(payload) for _, payload in fields)
    out = bytearray(total)
    HEADER.pack_into(out, 0, msg_type, total, len(fields))
    off = HEADER.size
    for tag, payload in fields:
        FIELD.pack_into(out, off, tag, len(payload))
        off += FIELD.size
        out[off:off + len(payload)] = payload
        off += len(payload)
    assert off == total
    return bytes(out)


def parse(buf: bytes):
    """Return (type, fields). Raises ValueError on a malformed frame."""
    if len(buf) < HEADER.size:
        raise ValueError("short header")
    msg_type, total, count = HEADER.unpack_from(buf, 0)
    if total != len(buf):
        raise ValueError(f"total mismatch: header {total} != buffer {len(buf)}")
    if buf[10:26] != b"\x00" * 16:
        raise ValueError("header bytes 10..26 must be zero")
    fields, off = [], HEADER.size
    for _ in range(count):
        if off + FIELD.size > total:
            raise ValueError("field header out of range")
        tag, length = FIELD.unpack_from(buf, off)
        off += FIELD.size
        if off + length > total:
            raise ValueError("field payload out of range")
        fields.append((tag, buf[off:off + length]))
        off += length
    if off != total:
        raise ValueError("trailing bytes")
    return msg_type, fields


# ----------------------------------------------------------------- replies

def auth_reply(player_id: str, token: str, product: str, session_id: str) -> bytes:
    """0x64 -> 0x65.  26 + 4*6 + 36 + 1106 + 22 + 36 = 1250 bytes."""
    return build(LOGIN, [
        (0, player_id.encode()),      # 36
        (1, token.encode()),          # 1106
        (2, product.encode()),        # 22
        (3, session_id.encode()),     # 36
    ])


def session_auth() -> bytes:
    """40-byte notification sent right after the auth reply."""
    return build(SESSION_AUTH, [(0, b"\x00" * 8)])


def heartbeat_reply(counter: int) -> bytes:
    """0x03 -> 0x04. The counter is echoed verbatim (verified 58/58)."""
    return build(HEARTBEAT_ACK, [(0, struct.pack("<Q", counter & 0xFFFFFFFFFFFFFFFF))])


def health_reply(reasons: int = 0) -> bytes:
    """0x69 -> 0x3EB. reasons==0 maps to 'success' in the client handler."""
    return build(HEALTH_RESP, [(0, struct.pack("<I", reasons & 0xFFFFFFFF))])


def heartbeat_counter(fields) -> int:
    """Extract the u64 counter from a 0x03 request, if present."""
    for tag, payload in fields:
        if tag == 0 and len(payload) >= 8:
            return struct.unpack_from("<Q", payload)[0]
    return 0


def describe(msg_type: int, fields) -> str:
    sizes = ", ".join(f"[{t}]{len(p)}B" for t, p in fields)
    return f"type=0x{msg_type:02X} fields={len(fields)} {sizes}"


if __name__ == "__main__":
    # self-test: encode -> decode -> rebuild
    frame = auth_reply("0" * 8 + "-0000-0000-0000-" + "0" * 12,
                       "x" * 1106, "com.riotgames.valorant",
                       "0" * 8 + "-0000-0000-0000-" + "0" * 12)
    print(f"auth reply   : {len(frame)} bytes (expect 1250)")
    t, f = parse(frame)
    print("parsed       :", describe(t, f))
    assert len(frame) == 1250 and t == 0x65 and len(f) == 4

    for counter in (1, 21, 58):
        hb = heartbeat_reply(counter)
        t2, f2 = parse(hb)
        assert len(hb) == 40 and heartbeat_counter(f2) == counter
    print("heartbeat    : 40 bytes, counter echo ok")

    hr = health_reply()
    print(f"health reply : {len(hr)} bytes (expect 36)")
    print(f"session auth : {len(session_auth())} bytes (expect 40)")
