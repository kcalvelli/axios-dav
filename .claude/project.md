# axios-dav Project Context

## OpenSpec SDD Workflow

**IMPORTANT**: This project follows a **Spec-Driven Development (SDD)** workflow using **OpenSpec**. All work must be planned as a delta before implementation.

### Source of Truth Documentation

**Primary Reference**: The `openspec/` directory contains the authoritative state of the project:

- **[project.md](../openspec/project.md)** - Project goals, tech stack, and the Constitution (rules).
- **[AGENTS.md](../openspec/AGENTS.md)** - Specific instructions for AI agents.
- **[specs/](../openspec/specs/)** - Modular specifications for all system features.
- **[glossary.md](../openspec/glossary.md)** - Domain terminology and NixOS concepts.
- **[discovery/](../openspec/discovery/)** - Historical discovery reports and tracked unknowns.

### Workflow for Changes (The Delta Process)

**1. Discovery & Planning:**
- Read `openspec/specs/` to understand the current state.
- Create a new directory in `openspec/changes/[change-name]/`.
- Stage updated spec files and a `tasks.md` implementation plan.

**2. Implementation:**
- Execute the tasks defined in `tasks.md`.
- Ensure all code complies with the Constitution in `openspec/project.md`.

**3. Finalization:**
- Merge the delta specs into the main `openspec/specs/` directory.
- Move the change directory to `openspec/changes/archive/`.

### Quick Reference for AI Assistants

When asked to work on axios-dav:
- **Core Rules & Goals** → `openspec/project.md`
- **Your Workflow** → `openspec/AGENTS.md`
- **Feature Specs** → `openspec/specs/[feature]/spec.md`
- **Terminology** → `openspec/glossary.md`

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

## Common Operations

### Adding a New Feature

1. Create proposal in `openspec/changes/[feature-name]/`
2. Write `proposal.md` and `tasks.md`
3. Implement according to tasks
4. Update specs and archive proposal

### Testing Locally

```bash
# Build and test
nix flake check

# Test in a NixOS VM (future)
nix run .#vm-test
```

## Notes for AI Assistants

### CRITICAL: OpenSpec Consultation REQUIRED

**BEFORE taking ANY action in this repository, you MUST:**
1. **STOP** - Do not proceed without consulting `openspec/`.
2. **READ** `openspec/project.md` and `openspec/AGENTS.md`.
3. **PLAN** your change as a delta in `openspec/changes/`.

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
