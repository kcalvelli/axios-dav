# Proposal: Greenfield Setup

## Summary

Initialize cairn-dav as a functional NixOS flake with declarative vdirsyncer configuration for Google Calendar and Contacts, plus an MCP server for AI access.

## Background

This project was extracted from cairn to provide standalone CalDAV/CardDAV synchronization capabilities. The cairn project previously had:

- `home/calendar/default.nix` - systemd timers for vdirsyncer sync
- Manual `~/.vdirsyncer/config` and `~/.config/khal/config` files (not Nix-managed)
- DMS integration via khal

cairn-dav will make this declarative and add MCP capabilities.

## Goals

1. **Working flake** - `nix flake check` passes
2. **Declarative vdirsyncer** - Generate config from Nix options
3. **Declarative khal** - Generate config from Nix options
4. **Google Calendar support** - OAuth-based sync
5. **Google Contacts support** - OAuth-based sync (optional)
6. **MCP server** - Basic calendar read/write tools
7. **Documentation** - README with usage examples

## Proposed Module Interface

```nix
services.cairn-dav = {
  enable = lib.mkEnableOption "cairn-dav calendar and contacts sync";

  # Calendar configuration
  calendar = {
    enable = lib.mkEnableOption "Calendar sync via CalDAV";

    accounts = lib.mkOption {
      type = lib.types.attrsOf (lib.types.submodule {
        options = {
          type = lib.mkOption {
            type = lib.types.enum [ "google" "caldav" "http" ];
            description = "Calendar provider type";
          };

          # Google accounts
          tokenFile = lib.mkOption {
            type = lib.types.nullOr lib.types.path;
            default = null;
            description = "Path to OAuth token file";
          };
          clientId = lib.mkOption {
            type = lib.types.nullOr lib.types.str;
            default = null;
          };
          clientSecretFile = lib.mkOption {
            type = lib.types.nullOr lib.types.path;
            default = null;
          };

          # CalDAV accounts
          url = lib.mkOption {
            type = lib.types.nullOr lib.types.str;
            default = null;
          };
          username = lib.mkOption {
            type = lib.types.nullOr lib.types.str;
            default = null;
          };
          passwordFile = lib.mkOption {
            type = lib.types.nullOr lib.types.path;
            default = null;
          };

          # HTTP ICS (read-only subscriptions)
          icsUrl = lib.mkOption {
            type = lib.types.nullOr lib.types.str;
            default = null;
          };

          # Sync behavior
          readOnly = lib.mkOption {
            type = lib.types.bool;
            default = false;
            description = "If true, local changes are not synced back";
          };
        };
      });
      default = {};
    };

    # khal settings
    defaultCalendar = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      description = "Default calendar for new events";
    };

    locale = {
      timeFormat = lib.mkOption {
        type = lib.types.str;
        default = "%H:%M";
      };
      dateFormat = lib.mkOption {
        type = lib.types.str;
        default = "%Y-%m-%d";
      };
    };
  };

  # Contacts configuration
  contacts = {
    enable = lib.mkEnableOption "Contacts sync via CardDAV";

    accounts = lib.mkOption {
      type = lib.types.attrsOf (lib.types.submodule {
        options = {
          type = lib.mkOption {
            type = lib.types.enum [ "google" "carddav" ];
          };
          tokenFile = lib.mkOption {
            type = lib.types.nullOr lib.types.path;
            default = null;
          };
          # ... similar to calendar
        };
      });
      default = {};
    };
  };

  # Sync settings
  sync = {
    frequency = lib.mkOption {
      type = lib.types.str;
      default = "5m";
      description = "Sync frequency (systemd timer format)";
    };
    conflictResolution = lib.mkOption {
      type = lib.types.enum [ "remote" "local" ];
      default = "remote";
      description = "Which side wins on conflict";
    };
  };

  # MCP server
  mcp = {
    enable = lib.mkEnableOption "MCP server for AI calendar/contacts access" // {
      default = true;
    };
  };
};
```

## Example Configuration

```nix
{
  services.cairn-dav = {
    enable = true;

    calendar = {
      enable = true;
      defaultCalendar = "personal";

      accounts = {
        personal = {
          type = "google";
          tokenFile = config.age.secrets.google-calendar-token.path;
          clientId = "1234567890-abcdef.apps.googleusercontent.com";
          clientSecretFile = config.age.secrets.google-client-secret.path;
        };

        holidays = {
          type = "http";
          icsUrl = "https://calendar.google.com/calendar/ical/en.usa%23holiday/public/basic.ics";
          readOnly = true;
        };
      };
    };

    contacts = {
      enable = true;
      accounts = {
        personal = {
          type = "google";
          tokenFile = config.age.secrets.google-contacts-token.path;
          clientId = "1234567890-abcdef.apps.googleusercontent.com";
          clientSecretFile = config.age.secrets.google-client-secret.path;
        };
      };
    };

    sync.frequency = "5m";
    mcp.enable = true;
  };
}
```

## MCP Tools (Initial Set)

### Calendar Tools
- `list_events` - List events in date range
- `search_events` - Search events by text
- `create_event` - Create new event
- `get_free_busy` - Check availability

### Contacts Tools
- `list_contacts` - List all contacts
- `search_contacts` - Search by name/email
- `get_contact` - Get contact details

## Implementation Phases

### Phase 1: Flake Foundation
- [ ] `flake.nix` with basic inputs/outputs
- [ ] Module skeleton with options
- [ ] README with project overview

### Phase 2: vdirsyncer Config Generation
- [ ] Generate vdirsyncer config from Nix options
- [ ] Google Calendar storage support
- [ ] CalDAV storage support
- [ ] HTTP ICS storage support
- [ ] Systemd timer for sync

### Phase 3: khal Config Generation
- [ ] Generate khal config from Nix options
- [ ] Link to vdirsyncer-managed directories
- [ ] Locale settings

### Phase 4: Contacts Support
- [ ] Google Contacts storage in vdirsyncer
- [ ] CardDAV storage support
- [ ] khard config generation

### Phase 5: MCP Server
- [ ] Python package structure
- [ ] Calendar tools implementation
- [ ] Contacts tools implementation
- [ ] MCP server registration in home-manager

### Phase 6: Documentation & Testing
- [ ] Comprehensive README
- [ ] Google OAuth setup guide
- [ ] `nix flake check` CI
- [ ] Integration tests

## Success Criteria

1. User can configure Google Calendar sync entirely in Nix
2. vdirsyncer config is generated correctly
3. `khal list` shows synced events
4. MCP server responds to tool calls
5. Works as standalone flake (no cairn dependency)

## Dependencies

- vdirsyncer (nixpkgs)
- khal (nixpkgs)
- khard (nixpkgs)
- Python 3.11+ (for MCP server)
- mcp Python SDK

## References

- [vdirsyncer documentation](https://vdirsyncer.pimutils.org/)
- [khal documentation](https://khal.readthedocs.io/)
- [khard documentation](https://khard.readthedocs.io/)
- [MCP specification](https://modelcontextprotocol.io/)
- [cairn-mail](https://github.com/kcalvelli/cairn-mail) - sibling project pattern
