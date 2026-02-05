# axios-dav Project Context

## Overview

axios-dav is a **declarative NixOS/home-manager module** for CalDAV and CardDAV synchronization. It provides:

- **Declarative vdirsyncer configuration** - Nix-managed sync config (no manual `~/.vdirsyncer/config`)
- **Calendar integration** - khal CLI/TUI with MCP server for AI access
- **Contacts integration** - khard CLI with MCP server for AI access
- **Google OAuth management** - Secure credential handling via agenix
- **Standalone or integrated** - Use independently or as part of axios

**Key Philosophy**: This is a library/module, not a personal configuration. Can be used by any NixOS user, not just axios users.

## Project Structure

```
axios-dav/
├── flake.nix              # Main flake with inputs and outputs
├── flake.lock             # Locked dependency versions
├── modules/               # NixOS modules
│   ├── default.nix        # Module registry
│   ├── calendar/          # Calendar sync and khal
│   └── contacts/          # Contacts sync and khard
├── home/                  # home-manager modules
│   ├── default.nix        # Home module registry
│   ├── calendar/          # User-level calendar config
│   └── contacts/          # User-level contacts config
├── pkgs/                  # Custom packages
│   └── mcp-dav/           # MCP server for calendar/contacts
└── openspec/              # Specifications and proposals
```

## Key Design Decisions

### 1. vdirsyncer as the Sync Engine

vdirsyncer handles both CalDAV (calendars) and CardDAV (contacts) with a unified configuration model. We generate `~/.config/vdirsyncer/config` from Nix options.

### 2. Google Support via DAV Endpoints

Google exposes CalDAV and CardDAV endpoints. We use vdirsyncer's `google_calendar` and `google_contacts` storage types.

**Note**: Google's CardDAV is reportedly unreliable. Future enhancement may add Google People API as an alternative backend.

### 3. MCP Server for AI Integration

The `mcp-dav` server exposes calendar and contacts tools:
- `list_events`, `create_event`, `search_events` (calendar)
- `list_contacts`, `search_contacts`, `get_contact` (contacts)

### 4. Modular Enable Flags

Users enable only what they need:
```nix
services.axios-dav = {
  calendar.enable = true;   # Just calendar
  contacts.enable = false;  # No contacts
};
```

## Testing Locally

```bash
# Build and test
nix flake check

# Test in a NixOS VM (future)
nix run .#vm-test
```

## Notes for AI Assistants

### Git Workflow

Always push commits before asking the user to test - they pull from remote, not your local changes.

```bash
git add <files> && git commit -m "message" && git push
```

### Confidence Markers

Use these when updating docs:
- `[EXPLICIT]` - Found directly in code/documentation
- `[INFERRED]` - Derived from code patterns with high confidence
- `[ASSUMED]` - Best guess based on standard conventions
- `[TBD]` - Insufficient evidence, requires human input
