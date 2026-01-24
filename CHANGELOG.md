# Changelog

All notable changes to axios-dav will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-24

### Added

- **NixOS Module** (`services.pim.calendar`, `services.pim.contacts`)
  - Declarative calendar account configuration (Google, CalDAV, HTTP ICS)
  - Declarative contacts account configuration (Google, CardDAV)
  - Configurable sync frequency and conflict resolution

- **Home-Manager Module**
  - Automatic vdirsyncer config generation
  - Automatic khal config generation (calendar CLI)
  - Automatic khard config generation (contacts CLI)
  - Systemd user services for periodic sync
  - Systemd timer for metasync (calendar metadata)

- **MCP Server** (`mcp-dav`)
  - `list_events` - List calendar events in date range
  - `search_events` - Search events by text
  - `create_event` - Create new calendar events
  - `get_free_busy` - Check availability/busy times
  - `list_contacts` - List contacts from address book
  - `search_contacts` - Search contacts by name/email/phone
  - `get_contact` - Get detailed contact information

- **Documentation**
  - Comprehensive README with setup instructions
  - Google OAuth setup guide with common gotchas
  - MCP server registration and usage examples
  - Options reference tables
  - Troubleshooting section

### Notes

- Requires `vdirsyncer discover` for initial OAuth setup with Google
- Google accounts require CardDAV API (not People API) for contacts
- MCP server creates local files; run `vdirsyncer sync` to push to remote

[0.1.0]: https://github.com/kcalvelli/axios-dav/releases/tag/v0.1.0
