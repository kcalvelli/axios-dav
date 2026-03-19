## Why

When MCP tools modify local data (create event, create/update/delete contact), the changes exist only on disk until the user manually runs `vdirsyncer sync`. This creates a gap where the AI agent reports success but the change hasn't actually reached the remote server. Users shouldn't need to remember to sync after every mutation — the MCP server should handle it.

## What Changes

- Add a helper function to `server.py` that runs `vdirsyncer sync` as a subprocess after mutations
- Call auto-sync after `create_event`, `create_contact`, `update_contact`, and `delete_contact`
- Replace the `_note` "run vdirsyncer sync" message with sync result status (success or failure details)
- If sync fails (network, auth), still return the local mutation as successful with a warning about sync failure

## Capabilities

### New Capabilities
- `mcp-auto-sync`: Automatic vdirsyncer sync after MCP write operations, with graceful failure handling

### Modified Capabilities
- `contacts-write`: Write tool responses will now include sync status instead of manual sync instructions

## Impact

- **Code**: `pkgs/mcp-dav/src/mcp_dav/server.py` — all mutating tool handlers
- **Dependencies**: Requires `vdirsyncer` on PATH (already guaranteed by the NixOS module)
- **Performance**: Each mutation adds network latency for the sync call; acceptable since user would sync manually anyway
- **Risk**: Low — local write succeeds independently of sync; sync failure is reported but non-fatal
