"""
Vanguard SDK — minimal named-pipe server  ·  REFERENCE / EDUCATIONAL
====================================================================
Serves the IPC endpoint the client expects and answers with the frames
documented in pipe_proto.py. Windows only (uses the Win32 pipe API).

Identity data is NOT hardcoded. Provide a JSON file:

    { "player_id": "<uuid>", "token": "<jwt>",
      "product": "com.riotgames.valorant", "session_id": "<uuid>" }

Start:  python pipe_server.py identity.json

Without that file the server still answers 0x03 and 0x69, but replies to
0x64 with nothing (there is no valid identity to report).
"""
import ctypes
import ctypes.wintypes as w
import json
import sys

import pipe_proto as P

PIPE_NAME = r"\\.\pipe\933823D3-C77B-4BAE-89D7-A92B567236BC"
PIPE_ACCESS_DUPLEX = 0x00000003
PIPE_TYPE_MESSAGE = 0x00000004
PIPE_READMODE_MESSAGE = 0x00000002
PIPE_WAIT = 0x00000000
PIPE_UNLIMITED_INSTANCES = 255
ERROR_PIPE_CONNECTED = 535
BUFSIZE = 65536

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.CreateNamedPipeW.restype = w.HANDLE
k32.CreateNamedPipeW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, w.DWORD,
                                 w.DWORD, w.DWORD, w.DWORD, w.LPVOID]
k32.ConnectNamedPipe.argtypes = [w.HANDLE, w.LPVOID]
k32.ReadFile.argtypes = [w.HANDLE, w.LPVOID, w.DWORD, ctypes.POINTER(w.DWORD), w.LPVOID]
k32.WriteFile.argtypes = [w.HANDLE, w.LPCVOID, w.DWORD, ctypes.POINTER(w.DWORD), w.LPVOID]
k32.FlushFileBuffers.argtypes = [w.HANDLE]
k32.DisconnectNamedPipe.argtypes = [w.HANDLE]
k32.CloseHandle.argtypes = [w.HANDLE]


def load_identity(path):
    if not path:
        return None
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    for key in ("player_id", "token", "session_id"):
        if not data.get(key):
            raise SystemExit(f"identity file is missing '{key}'")
    data.setdefault("product", "com.riotgames.valorant")
    return data


def handle_request(buf: bytes, identity):
    """Return a list of frames to write back (empty list = no reply)."""
    try:
        msg_type, fields = P.parse(buf)
    except ValueError as exc:
        print("  malformed frame:", exc)
        return []

    if msg_type == P.HEARTBEAT_SYN:
        counter = P.heartbeat_counter(fields)
        print(f"  0x03 heartbeat counter={counter}")
        return [P.heartbeat_reply(counter)]

    if msg_type == P.HEALTH_REQ:
        print("  0x69 health check")
        return [P.health_reply(0)]

    if msg_type == P.AUTH_REQUEST:
        if not identity:
            print("  0x64 auth request (no identity configured -> no reply)")
            return []
        print("  0x64 auth request -> 0x65 + 0x09")
        return [P.auth_reply(identity["player_id"], identity["token"],
                             identity["product"], identity["session_id"]),
                P.session_auth()]

    # 0x02 disconnect, 0x67 match start, unknown types: no reply by design
    print(f"  0x{msg_type:02X} ({len(buf)} B) -> no reply")
    return []


def serve(slot: int, identity):
    while True:
        handle = k32.CreateNamedPipeW(PIPE_NAME, PIPE_ACCESS_DUPLEX,
                                      PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
                                      PIPE_UNLIMITED_INSTANCES, BUFSIZE, BUFSIZE, 0, None)
        if handle == w.HANDLE(-1).value:
            print(f"[slot {slot}] CreateNamedPipe failed: {ctypes.get_last_error()}")
            return
        ok = k32.ConnectNamedPipe(handle, None)
        if not ok and ctypes.get_last_error() != ERROR_PIPE_CONNECTED:
            k32.CloseHandle(handle)
            continue
        print(f"[slot {slot}] client connected")
        buf = ctypes.create_string_buffer(BUFSIZE)
        read = w.DWORD(0)
        while k32.ReadFile(handle, buf, BUFSIZE, ctypes.byref(read), None):
            if read.value == 0:
                break
            for reply in handle_request(buf.raw[:read.value], identity):
                written = w.DWORD(0)
                k32.WriteFile(handle, reply, len(reply), ctypes.byref(written), None)
            k32.FlushFileBuffers(handle)
        k32.DisconnectNamedPipe(handle)
        k32.CloseHandle(handle)
        print(f"[slot {slot}] client disconnected")


def main():
    if sys.platform != "win32":
        raise SystemExit("this server uses the Win32 pipe API; run it on Windows")
    identity = load_identity(sys.argv[1] if len(sys.argv) > 1 else None)
    print("listening:", PIPE_NAME, "· identity:", "yes" if identity else "no")
    for slot in range(6):
        import threading
        threading.Thread(target=serve, args=(slot, identity), daemon=True).start()
    import time
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
