# axios-dav

Declarative CalDAV/CardDAV synchronization for NixOS with MCP integration.

## Features

- **Declarative Configuration** - No manual config files; everything in Nix
- **Google Calendar & Contacts** - First-class OAuth support
- **CalDAV/CardDAV** - Works with any standard provider (Fastmail, Nextcloud, etc.)
- **MCP Server** - AI agents can read/create calendar events and search contacts
- **Standalone or Integrated** - Use independently or as part of [axios](https://github.com/kcalvelli/axios)

## Installation

### Standalone (any NixOS system)

```nix
# flake.nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    axios-dav.url = "github:kcalvelli/axios-dav";
  };

  outputs = { self, nixpkgs, axios-dav, ... }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      modules = [
        axios-dav.nixosModules.default
        ./configuration.nix
      ];
    };
  };
}
```

### As part of axios

axios imports axios-dav automatically when PIM features are enabled.

## Configuration

### Google Calendar

```nix
{
  services.axios-dav = {
    enable = true;

    calendar = {
      enable = true;
      defaultCalendar = "personal";

      accounts = {
        personal = {
          type = "google";
          tokenFile = config.age.secrets.google-calendar-token.path;
          clientId = "your-client-id.apps.googleusercontent.com";
          clientSecretFile = config.age.secrets.google-client-secret.path;
        };
      };
    };

    sync.frequency = "5m";
  };
}
```

### CalDAV (Fastmail, Nextcloud, etc.)

```nix
{
  services.axios-dav = {
    enable = true;

    calendar = {
      enable = true;

      accounts = {
        fastmail = {
          type = "caldav";
          url = "https://caldav.fastmail.com/dav/calendars/user/me@fastmail.com/";
          username = "me@fastmail.com";
          passwordFile = config.age.secrets.fastmail-password.path;
        };
      };
    };
  };
}
```

### Read-only ICS Subscriptions

```nix
{
  services.axios-dav.calendar.accounts.holidays = {
    type = "http";
    icsUrl = "https://calendar.google.com/calendar/ical/en.usa%23holiday/public/basic.ics";
    readOnly = true;
  };
}
```

### Contacts

```nix
{
  services.axios-dav.contacts = {
    enable = true;

    accounts = {
      personal = {
        type = "google";
        tokenFile = config.age.secrets.google-contacts-token.path;
        clientId = "your-client-id.apps.googleusercontent.com";
        clientSecretFile = config.age.secrets.google-client-secret.path;
      };
    };
  };
}
```

## Google OAuth Setup

To sync with Google Calendar/Contacts, you need to create OAuth credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable the **CalDAV API** (not "Google Calendar API")
4. Enable the **CardDAV API** (not "Google Contacts API")
5. Go to **Credentials** → **Create Credentials** → **OAuth Client ID**
6. Choose **Desktop application**
7. Note your `client_id` and `client_secret`

Store credentials securely with agenix:

```bash
# Store client secret
echo "your-client-secret" | agenix -e secrets/google-client-secret.age

# Token file will be created on first sync
# Run: vdirsyncer discover
# Follow OAuth flow in browser
```

## CLI Usage

After configuration, use standard tools:

```bash
# List today's events
khal list

# Create new event
khal new 2025-01-25 14:00 15:00 "Meeting with Bob"

# Interactive calendar
ikhal

# List contacts
khard list

# Search contacts
khard search "john"

# Force sync
vdirsyncer sync
```

## MCP Tools

When `mcp.enable = true` (default), these tools are available to AI agents:

### Calendar Tools
- `list_events` - List events in date range
- `search_events` - Search events by text
- `create_event` - Create new calendar event
- `get_free_busy` - Check availability

### Contacts Tools
- `list_contacts` - List all contacts
- `search_contacts` - Search by name/email
- `get_contact` - Get contact details

## Development

```bash
# Enter dev shell
nix develop

# Check flake
nix flake check

# Format code
nix fmt
```

## Related Projects

- [axios](https://github.com/kcalvelli/axios) - Modular NixOS distribution
- [axios-ai-mail](https://github.com/kcalvelli/axios-ai-mail) - AI-powered email for NixOS
- [vdirsyncer](https://vdirsyncer.pimutils.org/) - Underlying sync engine
- [khal](https://khal.readthedocs.io/) - CLI calendar application
- [khard](https://khard.readthedocs.io/) - CLI contacts application

## License

MIT
