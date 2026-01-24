# Tasks: Greenfield Setup

## Phase 1: Flake Foundation

- [x] Create `flake.nix` with:
  - [x] nixpkgs input
  - [x] home-manager input (for home modules)
  - [x] NixOS module output (`nixosModules.default`)
  - [x] home-manager module output (`homeModules.default`)
  - [x] Package output for mcp-dav (`packages.${system}.mcp-dav`)
  - [x] Overlay output (`overlays.default`)
- [x] Create `modules/default.nix` with option skeleton
- [x] Create `home/default.nix` with home-manager module skeleton
- [x] Verify `nix flake check` passes
- [x] Create basic README.md
- [x] Create GitHub repository

## Phase 2: vdirsyncer Config Generation

- [x] Define `services.pim.calendar.accounts` option type (renamed from axios-dav)
- [x] Implement vdirsyncer config generation:
  - [x] `[general]` section with status_path
  - [x] `[storage]` sections for each account
  - [x] `[pair]` sections linking remote to local
- [x] Support storage types:
  - [x] `google_calendar` (OAuth)
  - [x] `caldav` (username/password)
  - [x] `http` (read-only ICS)
- [x] Generate `~/.config/vdirsyncer/config` via home-manager
- [x] Create systemd user service for `vdirsyncer sync`
- [x] Create systemd user timer (configurable frequency)
- [x] Create systemd service for `vdirsyncer metasync` (daily)
- [x] Test with actual Google Calendar account

## Phase 3: khal Config Generation

- [x] Define khal-specific options (locale, default calendar)
- [x] Generate `~/.config/khal/config`:
  - [x] `[calendars]` section pointing to vdirsyncer paths
  - [x] `[locale]` section with time/date formats
  - [x] `[default]` section with default calendar
- [x] Fix date format quoting for comma-containing formats
- [x] Fix HTTP ICS subscriptions (no type=discover, no glob)
- [x] Verify `khal list` works with synced data
- [x] Verify `khal new` creates events that sync

## Phase 4: Contacts Support

- [x] Define `services.pim.contacts.accounts` option type
- [x] Add vdirsyncer config generation for contacts:
  - [x] `google_contacts` storage
  - [x] `carddav` storage
- [x] Generate `~/.config/khard/config`
- [x] Fix Google Contacts "default" subdirectory path
- [x] Verify `khard list` works with synced data

## Phase 5: MCP Server

- [x] Create `pkgs/mcp-dav/default.nix` package definition (in flake.nix)
- [x] Create Python MCP server structure:
  - [x] `src/mcp_dav/__init__.py`
  - [x] `src/mcp_dav/server.py` - main MCP server
  - [x] `src/mcp_dav/calendar.py` - calendar tools
  - [x] `src/mcp_dav/contacts.py` - contacts tools
- [x] Implement calendar tools:
  - [x] `list_events` - parse .ics files, return events
  - [x] `search_events` - filter events by query
  - [x] `create_event` - create .ics file, trigger sync
  - [x] `get_free_busy` - calculate busy times
- [x] Implement contacts tools:
  - [x] `list_contacts` - parse .vcf files
  - [x] `search_contacts` - filter by name/email
  - [x] `get_contact` - get single contact details
- [x] Add MCP server to home-manager config
- [x] Test with mcp-cli / Claude Code (requires system rebuild)

## Phase 6: Documentation & Polish

- [x] Write comprehensive README.md:
  - [x] Project overview
  - [x] Installation (standalone + axios)
  - [x] Configuration examples
  - [x] Google OAuth setup guide (detailed with gotchas)
  - [x] CLI usage (khal, khard, vdirsyncer)
  - [x] Systemd services documentation
  - [x] Migration guide from manual config
  - [x] Troubleshooting section
  - [x] Options reference tables
  - [x] MCP tools reference (placeholder)
- [ ] Add CHANGELOG.md
- [x] Add LICENSE (MIT)
- [ ] Create GitHub Actions workflow:
  - [ ] `nix flake check`
  - [ ] Formatting check
- [ ] Create initial git tag/release

## axios Integration

- [x] Remove old `home/calendar` module from axios
- [x] Remove vdirsyncer from `modules/pim` (axios-dav handles it)
- [x] Remove calendar import from desktop sharedModules
- [x] Add documentation pointers to axios-dav

## Verification Checklist

Before marking complete:

- [x] `nix flake check` passes
- [x] Can sync Google Calendar with declarative config
- [x] Can create event with `khal new` and see it sync to Google
- [x] `khal list` shows correct events (Google + HTTP ICS)
- [x] `khard list` shows synced contacts
- [x] MCP server starts without errors
- [x] MCP `list_events` returns synced events
- [x] MCP `create_event` creates event that syncs (local file created, sync requires vdirsyncer)
- [ ] Works without axios (standalone)
- [x] README has complete setup instructions
