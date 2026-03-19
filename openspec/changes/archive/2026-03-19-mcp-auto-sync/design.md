## Context

The MCP server (`pkgs/mcp-dav/src/mcp_dav/server.py`) has four mutating tools: `create_event`, `create_contact`, `update_contact`, `delete_contact`. Each writes to local `.ics`/`.vcf` files and returns a `_note` telling the caller to run `vdirsyncer sync`. The sync never happens automatically, so changes sit locally until the user intervenes.

vdirsyncer is always available on PATH when the NixOS module is active. It reads its own config and syncs bidirectionally between local storage and remote DAV servers.

## Goals / Non-Goals

**Goals:**
- Auto-sync to remote after every successful local mutation
- Report sync outcome (success or failure) in the tool response
- Never block or fail the mutation itself if sync fails — local write is always the primary success

**Non-Goals:**
- Optimizing for batch mutations (sync-once-after-many) — premature; can add later if needed
- Sync before reads (pull-before-query) — separate concern
- Making sync configurable (on/off toggle) — just do it; revisit if users ask

## Decisions

### 1. subprocess.run with capture

Run `vdirsyncer sync` via `subprocess.run()` with stdout/stderr captured and a timeout. This is the simplest approach — no async, no background threads, no new dependencies.

**Alternative considered**: `asyncio.create_subprocess_exec` — unnecessary complexity since MCP tool calls are already sequential per-request. The caller is waiting for our response anyway.

### 2. Shared helper function `_run_sync()`

A single `_run_sync() -> dict` function in `server.py` that returns `{"synced": True/False, "message": "..."}`. Each mutating tool calls it after the local write and merges the result into its response.

**Alternative considered**: Decorator pattern — over-engineered for four call sites.

### 3. Replace `_note` with `_sync` field

Instead of `_note: "Run vdirsyncer sync..."`, return `_sync: {"success": true}` or `_sync: {"success": false, "error": "..."}`. This is machine-readable and the AI agent can act on failures.

### 4. Timeout of 30 seconds

vdirsyncer sync typically completes in a few seconds. A 30-second timeout catches hung processes without being too aggressive. On timeout, treat as sync failure (local write still succeeded).

## Risks / Trade-offs

- **Added latency** → Acceptable. Users would wait for sync anyway. Typically 2-5 seconds.
- **Sync failure on every call if auth is expired** → Mitigated by non-fatal handling. The `_sync.error` message will surface the auth issue to the AI agent, which can inform the user.
- **vdirsyncer not on PATH** → Only possible if someone runs mcp-dav outside the NixOS module. `_run_sync` catches `FileNotFoundError` and returns a clear error.
- **Concurrent sync conflicts** → vdirsyncer uses lock files internally. If a systemd timer sync is already running, vdirsyncer will handle it (or we'll get a lock error, which we report as a sync warning).
