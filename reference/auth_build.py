"""
Vanguard gateway — request builder / response reader  ·  REFERENCE / EDUCATIONAL
================================================================================
Implements the wire format documented in ../../docs/01-protocol.md and
../../docs/03-auth-payload.md:

    frame   : 08 <type> 12 <varint len> <envelope> 18 01
    envelope: "RG\x01\x00" | RSA-OAEP-SHA512(32B key) | nonce12 | AES-256-GCM | tag16

IMPORTANT LIMITS (measured, see docs/10-open-questions.md)
----------------------------------------------------------
* Two device-id parts (p2/p3, 64 bytes each) are produced by a secret that never
  leaves kernel mode. They cannot be derived from readable hardware, so a request
  built from p1/p5/p6 alone will be rejected. This file shows the exact mechanics;
  it does not provide those values.
* Sending an authentication request is itself a detection signal. Accounts that
  sent one were banned within 0.5-2.7 s (8/8, small sample).

Requires: cryptography >= 41   (pip install cryptography)
"""
import base64
import hashlib
import os
import struct
import urllib.request

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = bytes.fromhex("F4AD529CDE170EE1D1029B4A3CA89820")   # 16 RAW bytes
CLIENT_VERSION = (1, 19, 1, 18)
PRODUCT_ID = "com.riotgames.valorant"

TYPE_AUTH, TYPE_ACCESS, TYPE_HEARTBEAT, TYPE_TASK_RESULT = 3, 4, 7, 9
HOST_EU = "eu.vg.ac.pvp.net"


# --------------------------------------------------------------- protobuf

def varint(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        out.append(byte | (0x80 if value else 0))
        if not value:
            return bytes(out)


def field(number: int, wire: int, payload: bytes) -> bytes:
    """wire 0 = varint, 2 = length-delimited."""
    head = varint((number << 3) | wire)
    return head + (varint(len(payload)) + payload if wire == 2 else varint(int.from_bytes(payload, "little")))


def f_bytes(number: int, value: bytes) -> bytes:
    return field(number, 2, value)


def f_str(number: int, value: str) -> bytes:
    return field(number, 2, value.encode())


def f_int(number: int, value: int) -> bytes:
    return field(number, 0, value.to_bytes(max(1, (value.bit_length() + 7) // 8), "little"))


# ------------------------------------------------------------- identity

def machine_id(p1: bytes, p2: bytes, p3: bytes, p5: bytes, p6_blocks) -> bytes:
    """p1 16 B · p2/p3 64 B · p5 6 B · p6 = five 97-byte blocks. Result: 895 bytes."""
    b64 = lambda b: base64.b64encode(b)
    p6 = b";".join(b64(block) for block in p6_blocks)
    return (b"||1;" + b64(p1) + b"||2;" + b64(p2) + b"||3;" + b64(p3) +
            b"||4" + b"||5;" + b64(p5) + b"||6;" + p6)


def integrity_ht(mid: bytes) -> bytes:
    """ht = Base64(SHA1("6;"+p6 + "1;"+p1 + "2;"+p2 + "3;"+p3 + "5;"+p5 + version + MAGIC))."""
    parts = {}
    for chunk in mid.split(b"||"):
        if not chunk:
            continue
        key, _, value = chunk.partition(b";")
        parts[key] = value
    version = b".".join(str(n).encode() for n in CLIENT_VERSION)
    material = (b"6;" + parts[b"6"] + b"1;" + parts[b"1"] + b"2;" + parts[b"2"] +
                b"3;" + parts[b"3"] + b"5;" + parts[b"5"] + version + MAGIC)
    return base64.b64encode(hashlib.sha1(material).digest())


def os_info(version="10.0.19045") -> bytes:
    return f_int(1, 1) + f_int(2, 2) + f_str(4, version)


def version_block() -> bytes:
    major, minor, patch, build = CLIENT_VERSION
    return f_int(1, major) + f_int(2, minor) + f_int(3, patch) + f_int(4, build)


def flags_block(flags=None) -> bytes:
    flags = flags or {"IOMMU": 1, "TPM2": 1, "VBS": 1, "SB": 0, "HVCI": 1}
    return b"".join(f_str(1, name) + f_int(2, int(value)) for name, value in flags.items())


def integrity_block(htt_b64: str, ht_b64: bytes, gg_b64: str) -> bytes:
    entries = [(b"htt", htt_b64.encode()), (b"ht", ht_b64), (b"gg", gg_b64.encode())]
    return b"".join(f_str(1, name.decode()) + f_str(2, value.decode()) for name, value in entries)


# ---------------------------------------------------------------- message

def build_auth(mid: bytes, token: str, client_public_b64: str, sid: str,
               ht_b64: bytes, htt_b64: str, gg_b64: str) -> bytes:
    """Serialized AuthenticationRequest (2683 bytes with real data)."""
    return b"".join([
        f_str(1, mid.decode()),
        f_bytes(2, os_info()),
        f_str(4, token),
        f_str(5, client_public_b64),
        f_bytes(6, version_block()),
        f_bytes(7, version_block()),
        f_str(8, PRODUCT_ID),
        f_int(9, 3),
        f_str(13, sid),
        f_bytes(14, flags_block()),
        f_bytes(15, integrity_block(htt_b64, ht_b64, gg_b64)),
    ])


# --------------------------------------------------------------- envelope

def envelope(msg_type: int, plaintext: bytes, server_key) -> bytes:
    session_key = os.urandom(32)
    wrapped = server_key.encrypt(
        session_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA512()),
                     algorithm=hashes.SHA512(), label=None))
    nonce = os.urandom(12)
    body = AESGCM(session_key).encrypt(nonce, plaintext, None)   # ct || tag
    env = b"RG\x01\x00" + wrapped + nonce + body
    return b"\x08" + bytes([msg_type]) + b"\x12" + varint(len(env)) + env + b"\x18\x01"


def open_response(client_private, frame: bytes) -> bytes:
    """Reverse of envelope(): unwrap key with the client private key, then GCM-decrypt."""
    assert frame[0] == 0x08          # frame: 08 <type> 12 <varint len> <envelope> 18 01
    pos = 2
    assert frame[pos] == 0x12, "expected 0x12 (length tag)"
    pos += 1
    length, shift = 0, 0
    while True:
        byte = frame[pos]; pos += 1
        length |= (byte & 0x7F) << shift
        shift += 7
        if not byte & 0x80:
            break
    env = frame[pos:pos + length]
    assert env[:4] == b"RG\x01\x00"
    wrapped, nonce, body = env[4:260], env[260:272], env[272:]
    session_key = client_private.decrypt(
        wrapped, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA512()),
                              algorithm=hashes.SHA512(), label=None))
    return AESGCM(session_key).decrypt(nonce, body, None)


# ------------------------------------------------------------------ send

def post(frame: bytes, player_id: str, host: str = HOST_EU, port: int = 8443, timeout: int = 25):
    req = urllib.request.Request(
        f"https://{host}:{port}/vanguard/v1/gateway", data=frame, method="POST",
        headers={"Content-Type": "application/x-protobuf",
                 "X-VG-1": str(frame[1]), "X-VG-2": player_id, "X-VG-3": "1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:          # 400/401/403/429 are meaningful
        return exc.code, exc.read()


def load_key(path, private=False):
    data = open(path, "rb").read()
    return (serialization.load_pem_private_key(data, None) if private
            else serialization.load_pem_public_key(data))


if __name__ == "__main__":
    # Offline self-test: build a dummy request and verify the size identities.
    p1, p2, p3, p5 = os.urandom(16), os.urandom(64), os.urandom(64), os.urandom(6)
    p6 = [os.urandom(97) for _ in range(5)]
    mid = machine_id(p1, p2, p3, p5, p6)
    ht = integrity_ht(mid)

    # NOTE: the real client key uses public exponent 17. The `cryptography` library
    # refuses to generate e=17 keys, so it must be built from explicit p/q
    # (RSAPrivateNumbers). 65537 is used here only so the self-test runs.
    client_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    spki = client_key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)

    msg = build_auth(mid, "x" * 1106, base64.b64encode(spki).decode(), "0" * 36,
                     ht, base64.b64encode(os.urandom(32)).decode(),
                     base64.b64encode(os.urandom(20)).decode())

    print(f"machine_id : {len(mid)} bytes (expect 895)")
    print(f"ht         : {ht.decode()} ({len(ht)} chars)")
    print(f"auth plain : {len(msg)} bytes (2683 with real token/keys)")

    # envelope round-trip with a throwaway server key
    server = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    frame = envelope(TYPE_AUTH, msg, server.public_key())
    print(f"frame      : {len(frame)} bytes")
    assert open_response(server, frame) == msg
    print("round-trip : ok")
