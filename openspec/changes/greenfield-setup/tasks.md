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

- [x] Define `services.axios-dav.calendar.accounts` option type
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
- [ ] Test with actual Google Calendar account

## Phase 3: khal Config Generation

- [x] Define khal-specific options (locale, default calendar)
- [x] Generate `~/.config/khal/config`:
  - [x] `[calendars]` section pointing to vdirsyncer paths
  - [x] `[locale]` section with time/date formats
  - [x] `[default]` section with default calendar
- [ ] Verify `khal list` works with synced data
- [ ] Verify `khal new` creates events that sync

## Phase 4: Contacts Support

- [x] Define `services.axios-dav.contacts.accounts` option type
- [x] Add vdirsyncer config generation for contacts:
  - [x] `google_contacts` storage
  - [x] `carddav` storage
- [x] Generate `~/.config/khard/config`
- [ ] Verify `khard list` works with synced data

## Phase 5: MCP Server

- [ ] Create `pkgs/mcp-dav/default.nix` package definition
- [ ] Create Python MCP server structure:
  - [ ] `src/mcp_dav/__init__.py`
  - [ ] `src/mcp_dav/server.py` - main MCP server
  - [ ] `src/mcp_dav/calendar.py` - calendar tools
  - [ ] `src/mcp_dav/contacts.py` - contacts tools
- [ ] Implement calendar tools:
  - [ ] `list_events` - parse .ics files, return events
  - [ ] `search_events` - filter events by query
  - [ ] `create_event` - create .ics file, trigger sync
  - [ ] `get_free_busy` - calculate busy times
- [ ] Implement contacts tools:
  - [ ] `list_contacts` - parse .vcf files
  - [ ] `search_contacts` - filter by name/email
  - [ ] `get_contact` - get single contact details
- [ ] Add MCP server to home-manager config
- [ ] Test with mcp-cli / Claude Code

## Phase 6: Documentation & Polish

- [x] Write comprehensive README.md:
  - [x] Project overview
  - [x] Installation (standalone + axios)
  - [x] Configuration examples
  - [x] Google OAuth setup guide
  - [x] MCP tools reference
- [ ] Add CHANGELOG.md
- [ ] Add LICENSE (MIT or similar)
- [ ] Create GitHub Actions workflow:
  - [ ] `nix flake check`
  - [ ] Formatting check
- [ ] Create initial git tag/release

## Verification Checklist

Before marking complete:

- [x] `nix flake check` passes
- [ ] Can sync Google Calendar with declarative config
- [ ] Can create event with `khal new` and see it sync to Google
- [ ] `khal list` shows correct events
- [ ] MCP server starts without errors
- [ ] MCP `list_events` returns synced events
- [ ] MCP `create_event` creates event that syncs
- [ ] Works without axios (standalone)
- [x] README has complete setup instructions
