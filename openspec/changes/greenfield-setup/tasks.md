# Tasks: Greenfield Setup

## Phase 1: Flake Foundation

- [ ] Create `flake.nix` with:
  - [ ] nixpkgs input
  - [ ] home-manager input (for home modules)
  - [ ] NixOS module output (`nixosModules.default`)
  - [ ] home-manager module output (`homeModules.default`)
  - [ ] Package output for mcp-dav (`packages.${system}.mcp-dav`)
  - [ ] Overlay output (`overlays.default`)
- [ ] Create `modules/default.nix` with option skeleton
- [ ] Create `home/default.nix` with home-manager module skeleton
- [ ] Verify `nix flake check` passes
- [ ] Create basic README.md

## Phase 2: vdirsyncer Config Generation

- [ ] Define `services.axios-dav.calendar.accounts` option type
- [ ] Implement vdirsyncer config generation:
  - [ ] `[general]` section with status_path
  - [ ] `[storage]` sections for each account
  - [ ] `[pair]` sections linking remote to local
- [ ] Support storage types:
  - [ ] `google_calendar` (OAuth)
  - [ ] `caldav` (username/password)
  - [ ] `http` (read-only ICS)
- [ ] Generate `~/.config/vdirsyncer/config` via home-manager
- [ ] Create systemd user service for `vdirsyncer sync`
- [ ] Create systemd user timer (configurable frequency)
- [ ] Create systemd service for `vdirsyncer metasync` (daily)
- [ ] Test with actual Google Calendar account

## Phase 3: khal Config Generation

- [ ] Define khal-specific options (locale, default calendar)
- [ ] Generate `~/.config/khal/config`:
  - [ ] `[calendars]` section pointing to vdirsyncer paths
  - [ ] `[locale]` section with time/date formats
  - [ ] `[default]` section with default calendar
- [ ] Verify `khal list` works with synced data
- [ ] Verify `khal new` creates events that sync

## Phase 4: Contacts Support

- [ ] Define `services.axios-dav.contacts.accounts` option type
- [ ] Add vdirsyncer config generation for contacts:
  - [ ] `google_contacts` storage
  - [ ] `carddav` storage
- [ ] Generate `~/.config/khard/config`
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

- [ ] Write comprehensive README.md:
  - [ ] Project overview
  - [ ] Installation (standalone + axios)
  - [ ] Configuration examples
  - [ ] Google OAuth setup guide
  - [ ] MCP tools reference
- [ ] Add CHANGELOG.md
- [ ] Add LICENSE (MIT or similar)
- [ ] Create GitHub Actions workflow:
  - [ ] `nix flake check`
  - [ ] Formatting check
- [ ] Create initial git tag/release

## Verification Checklist

Before marking complete:

- [ ] `nix flake check` passes
- [ ] Can sync Google Calendar with declarative config
- [ ] Can create event with `khal new` and see it sync to Google
- [ ] `khal list` shows correct events
- [ ] MCP server starts without errors
- [ ] MCP `list_events` returns synced events
- [ ] MCP `create_event` creates event that syncs
- [ ] Works without axios (standalone)
- [ ] README has complete setup instructions
