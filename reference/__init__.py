"""Reference implementations for the Vanguard gateway / IPC protocols.

Modules:
    auth_build  -- request construction, envelope wrap/unwrap
    pipe_proto  -- 26-byte IPC frame codec and reply builders
    pipe_server -- Windows named-pipe server (uses pipe_proto)

Educational reference only. See README.md in this directory for the hard limits.
"""
