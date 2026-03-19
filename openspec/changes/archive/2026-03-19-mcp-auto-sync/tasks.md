## 1. Add sync helper

- [x] 1.1 Add `import subprocess` to `server.py`
- [x] 1.2 Create `_run_sync() -> dict` function in `server.py` that runs `vdirsyncer sync` with 30s timeout, captures output, and returns `{"success": bool, "error": str|None}`
- [x] 1.3 Handle `FileNotFoundError` (vdirsyncer not on PATH), `subprocess.TimeoutExpired`, and general exceptions in `_run_sync()`

## 2. Wire sync into mutating tools

- [x] 2.1 Update `create_event` to call `_run_sync()` and replace `_note` with `_sync` field
- [x] 2.2 Update `create_contact` to call `_run_sync()` and replace `_note` with `_sync` field
- [x] 2.3 Update `update_contact` to call `_run_sync()` and replace `_note` with `_sync` field
- [x] 2.4 Update `delete_contact` to call `_run_sync()` and replace `_note` with `_sync` field

## 3. Update tool docstrings

- [x] 3.1 Remove "run vdirsyncer sync" from `create_event`, `create_contact`, `update_contact`, `delete_contact` docstrings
