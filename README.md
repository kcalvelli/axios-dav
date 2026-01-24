# axios-dav

Declarative CalDAV/CardDAV synchronization for NixOS with MCP integration.

## Features

- **Declarative Configuration** - No manual config files; everything in Nix
- **Google Calendar & Contacts** - First-class OAuth support
- **CalDAV/CardDAV** - Works with any standard provider (Fastmail, Nextcloud, etc.)
- **HTTP/ICS Subscriptions** - Read-only calendar feeds (holidays, sports, etc.)
- **MCP Server** - AI agents can read/create calendar events and search contacts
- **Standalone or Integrated** - Use independently or as part of [axios](https://github.com/kcalvelli/axios)

## Quick Start

### 1. Add to your flake

```nix
# flake.nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    home-manager.url = "github:nix-community/home-manager";
    axios-dav.url = "github:kcalvelli/axios-dav";
  };

  outputs = { self, nixpkgs, home-manager, axios-dav, ... }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      specialArgs = { inherit inputs; };
      modules = [
        axios-dav.nixosModules.default
        home-manager.nixosModules.home-manager
        ./configuration.nix
      ];
    };
  };
}
```

### 2. Configure NixOS module

```nix
# configuration.nix
{ inputs, ... }:
{
  # Import axios-dav NixOS module (provides services.pim.* options)
  imports = [ inputs.axios-dav.nixosModules.default ];

  services.pim.calendar = {
    enable = true;
    defaultCalendar = "Family";

    accounts = {
      google = {
        type = "google";
        tokenFile = "/home/youruser/.vdirsyncer/google_token.json";
        clientId = "your-client-id.apps.googleusercontent.com";
        clientSecretFile = "/run/agenix/google-client-secret";  # Or any secrets manager
      };
    };

    sync = {
      frequency = "5m";
      conflictResolution = "remote";  # Google wins on conflict
    };
  };
}
```

### 3. Configure home-manager module

```nix
# In your home-manager config
{ inputs, ... }:
{
  imports = [ inputs.axios-dav.homeModules.default ];

  # The home module reads services.pim.* from NixOS config
  # and generates vdirsyncer, khal, and khard configurations
}
```

### 4. Initial setup

After rebuilding your system:

```bash
# Discover and authorize calendars (opens browser for OAuth)
vdirsyncer discover

# Initial sync
vdirsyncer sync

# Verify with khal
khal list
```

## Configuration Reference

### Google Calendar (Two-way sync)

```nix
services.pim.calendar = {
  enable = true;
  defaultCalendar = "Family";  # Default for new events

  accounts.google = {
    type = "google";
    tokenFile = "/home/user/.vdirsyncer/google_token.json";  # Must be writable for token refresh
    clientId = "123456789-abc.apps.googleusercontent.com";
    clientSecretFile = "/run/agenix/google-client-secret";
    localPath = "~/.calendars/";  # Optional: custom path (default: ~/.calendars/google/)
    readOnly = false;  # Two-way sync (default)
  };

  sync = {
    frequency = "5m";           # Sync interval
    conflictResolution = "remote";  # "remote" or "local" wins on conflict
  };
};
```

### CalDAV (Fastmail, Nextcloud, etc.)

```nix
services.pim.calendar.accounts.fastmail = {
  type = "caldav";
  url = "https://caldav.fastmail.com/dav/calendars/user/me@fastmail.com/";
  username = "me@fastmail.com";
  passwordFile = "/run/agenix/fastmail-password";
};
```

### HTTP/ICS Subscriptions (Read-only)

```nix
services.pim.calendar.accounts.orthodox = {
  type = "http";
  icsUrl = "https://orthocal.info/api/gregorian/ical/";
  localPath = "~/.calendars-external/orthodox/";  # Keep separate from writable calendars
  readOnly = true;
};

services.pim.calendar.accounts.holidays = {
  type = "http";
  icsUrl = "https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics";
  readOnly = true;
};
```

### Google Contacts

```nix
services.pim.contacts = {
  enable = true;

  accounts.google = {
    type = "google";
    tokenFile = "/home/user/.vdirsyncer/google_contacts_token.json";  # Separate from calendar!
    clientId = "123456789-abc.apps.googleusercontent.com";  # Same as calendar
    clientSecretFile = "/run/agenix/google-client-secret";   # Same as calendar
  };
};
```

### CardDAV (Fastmail, Nextcloud, etc.)

```nix
services.pim.contacts.accounts.fastmail = {
  type = "carddav";
  url = "https://carddav.fastmail.com/dav/addressbooks/user/me@fastmail.com/";
  username = "me@fastmail.com";
  passwordFile = "/run/agenix/fastmail-password";
};
```

## Google OAuth Setup (Detailed)

Google Calendar and Contacts require OAuth credentials. Here's the complete setup process:

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., "vdirsyncer")
3. Note the **Project Number** (needed later to verify you're in the right project)

### Step 2: Enable Required APIs

**IMPORTANT:** You need the *DAV APIs, not the regular Calendar/Contacts APIs!

1. Go to **APIs & Services** → **Library**
2. Search and enable: **CalDAV API** (for calendars)
3. Search and enable: **CardDAV API** (for contacts)

Do NOT use "Google Calendar API" or "Google People API" - those are different APIs that vdirsyncer doesn't use.

### Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** (or Internal if using Google Workspace)
3. Fill in required fields:
   - App name: "vdirsyncer" (or anything)
   - User support email: your email
   - Developer contact: your email
4. Skip scopes (vdirsyncer requests them automatically)
5. Add your Google account as a **Test user**

### Step 4: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop application**
4. Name: "vdirsyncer" (or anything)
5. Click **Create**
6. Note your **Client ID** and **Client Secret**

### Step 5: Store Credentials Securely

Using agenix (recommended):

```bash
# Store the client secret
echo "your-client-secret" | agenix -e secrets/google-client-secret.age

# In your NixOS config
age.secrets.google-client-secret = {
  file = ./secrets/google-client-secret.age;
  owner = "youruser";
  mode = "0400";
};
```

### Step 6: Initial Authorization

After NixOS rebuild:

```bash
# This will open your browser for OAuth authorization
vdirsyncer discover

# For calendar: authorize access to Google Calendar
# For contacts: authorize access to Google Contacts (separate authorization)

# After authorizing, token files are created automatically
# First sync
vdirsyncer sync
```

### Important Notes

- **Separate Token Files**: Calendar and Contacts need SEPARATE token files because they use different API scopes
- **Token Location**: Token files must be writable (for refresh tokens). Don't put them in /nix/store
- **Project Consistency**: Make sure your Client ID is from the same project where you enabled CalDAV/CardDAV APIs
- **Test Users**: If your OAuth app is in "Testing" mode, your Google account must be added as a test user

## CLI Usage

### Calendar (khal)

```bash
# List upcoming events
khal list

# List events in date range
khal list today 7d
khal list 2025-01-25 2025-02-01

# Create new event
khal new 2025-01-25 14:00 15:00 "Meeting with Bob"
khal new 2025-01-25 "All day event"  # All-day event
khal new tomorrow 10:00 11:00 "Morning standup" -a Family  # Specify calendar

# Interactive calendar UI
ikhal

# Show all calendars
khal printcalendars

# Search events
khal search "meeting"
```

### Contacts (khard)

```bash
# List all contacts
khard list

# Search contacts
khard list "calvelli"
khard list "john"

# Show contact details
khard show "John Smith"

# Edit contact (opens $EDITOR)
khard edit "John Smith"

# Create new contact (opens $EDITOR)
khard new

# Export contact as vCard
khard export "John Smith"
```

### Sync (vdirsyncer)

```bash
# Sync all calendars and contacts
vdirsyncer sync

# Sync specific pair
vdirsyncer sync cal_google
vdirsyncer sync contacts_google

# Discover new calendars/address books
vdirsyncer discover

# Sync metadata (calendar colors, names)
vdirsyncer metasync

# Debug mode
vdirsyncer -v DEBUG sync
```

## Systemd Services

axios-dav creates user-level systemd services for automatic sync:

```bash
# Check sync timer status
systemctl --user status vdirsyncer-sync.timer

# List all vdirsyncer timers
systemctl --user list-timers | grep vdirsyncer

# Manually trigger sync
systemctl --user start vdirsyncer-sync.service

# View sync logs
journalctl --user -u vdirsyncer-sync.service -f
```

Services created:
- `vdirsyncer-sync.service` / `.timer` - Main sync (every 5 minutes by default)
- `vdirsyncer-metasync.service` / `.timer` - Metadata sync (daily)
- `vdirsyncer-discover.service` - Initial collection discovery

## Migration from Manual Config

If you're migrating from a manually configured vdirsyncer setup:

### 1. Backup existing config

```bash
cp ~/.config/vdirsyncer/config ~/.config/vdirsyncer/config.bak
cp -r ~/.calendars ~/.calendars.bak
cp -r ~/.contacts ~/.contacts.bak
```

### 2. Note your existing paths

Check your current config for:
- Token file locations
- Local calendar/contacts paths
- Calendar names

### 3. Configure axios-dav with matching paths

Use `localPath` option to match your existing paths:

```nix
services.pim.calendar.accounts.google = {
  type = "google";
  tokenFile = "/home/user/.vdirsyncer/google_token.json";  # Existing token
  localPath = "~/.calendars/";  # Match existing path
  # ...
};
```

### 4. Rebuild and verify

```bash
# Rebuild system
sudo nixos-rebuild switch

# The new config will use your existing token and data
khal list
khard list
```

## Troubleshooting

### "403 Forbidden" during vdirsyncer discover

**Cause**: Wrong API enabled or wrong Google Cloud project

**Fix**:
1. Verify you enabled **CalDAV API** and/or **CardDAV API** (not Calendar API or People API)
2. Verify your Client ID is from the same project where APIs are enabled
3. Delete token file and re-authorize:
   ```bash
   rm ~/.vdirsyncer/google_token.json
   vdirsyncer discover
   ```

### khal shows "Found no calendars"

**Cause**: vdirsyncer hasn't discovered collections yet

**Fix**:
```bash
vdirsyncer discover
vdirsyncer sync
```

### khard shows "Found no contacts"

**Cause**: Google Contacts creates a "default" subdirectory that older configs might not expect

**Fix**: Ensure you're using the latest axios-dav which handles this automatically

### Sync timer not running

**Cause**: Home-manager services need to be enabled

**Fix**:
```bash
systemctl --user daemon-reload
systemctl --user enable --now vdirsyncer-sync.timer
```

### Token refresh errors

**Cause**: Token file not writable or corrupted

**Fix**:
```bash
# Remove old token
rm ~/.vdirsyncer/google_token.json

# Re-authorize
vdirsyncer discover
```

## MCP Server

The mcp-dav MCP server provides AI agents with direct access to your synced calendar and contacts data. When `services.pim.mcp.enable = true` (default), the `mcp-dav` binary is installed.

### Available Tools

#### Calendar Tools

| Tool | Description |
|------|-------------|
| `list_events` | List events in date range (default: today to +30 days) |
| `search_events` | Search events by text in summary/description/location |
| `create_event` | Create new calendar event (run `vdirsyncer sync` after to push to remote) |
| `get_free_busy` | Get busy time slots for scheduling |

#### Contacts Tools

| Tool | Description |
|------|-------------|
| `list_contacts` | List all contacts from address book |
| `search_contacts` | Search contacts by name, email, phone, or organization |
| `get_contact` | Get detailed contact info by UID or name |

### Registering with Claude Code

Add mcp-dav to your Claude Code MCP configuration (`~/.mcp.json` or `~/.claude.json`):

```json
{
  "mcpServers": {
    "mcp-dav": {
      "command": "mcp-dav",
      "env": {
        "MCP_DAV_CALENDARS": "~/.calendars",
        "MCP_DAV_CONTACTS": "~/.contacts"
      }
    }
  }
}
```

Or use the full path from Nix store:
```bash
# Find the path
which mcp-dav
# Output: /nix/store/...-mcp-dav-0.1.0/bin/mcp-dav
```

### Testing with mcp-cli

```bash
# List available tools
mcp-cli mcp-dav -d

# List events for next week
mcp-cli call mcp-dav list_events '{"start_date": "2025-01-24", "end_date": "2025-01-31"}'

# Search contacts
mcp-cli call mcp-dav search_contacts '{"query": "John"}'

# Create an event
mcp-cli call mcp-dav create_event '{
  "summary": "Team Meeting",
  "start": "2025-01-25T10:00:00",
  "end": "2025-01-25T11:00:00",
  "calendar": "Family",
  "location": "Conference Room"
}'
# Then sync: vdirsyncer sync

# Check availability
mcp-cli call mcp-dav get_free_busy '{"start_date": "2025-01-24", "end_date": "2025-01-26"}'
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_DAV_CALENDARS` | `~/.calendars` | Path to vdirsyncer calendar storage |
| `MCP_DAV_CONTACTS` | `~/.contacts` | Path to vdirsyncer contacts storage |

### Tool Schemas

<details>
<summary>list_events</summary>

```json
{
  "start_date": "2025-01-24",  // Optional, defaults to today
  "end_date": "2025-01-31",    // Optional, defaults to +30 days
  "calendar": "Family"          // Optional, filter by calendar name
}
```
</details>

<details>
<summary>search_events</summary>

```json
{
  "query": "meeting",      // Required, case-insensitive search
  "calendar": "Work",      // Optional, filter by calendar
  "limit": 50              // Optional, max results (default: 50)
}
```
</details>

<details>
<summary>create_event</summary>

```json
{
  "summary": "Event Title",           // Required
  "start": "2025-01-25T10:00:00",    // Required, ISO8601
  "end": "2025-01-25T11:00:00",      // Required, ISO8601
  "calendar": "Family",              // Required, calendar name
  "location": "123 Main St",         // Optional
  "description": "Event details",    // Optional
  "all_day": false                   // Optional, default false
}
```
</details>

<details>
<summary>get_free_busy</summary>

```json
{
  "start_date": "2025-01-24",       // Required
  "end_date": "2025-01-26",         // Required
  "calendars": ["Work", "Family"]   // Optional, filter calendars
}
```
</details>

<details>
<summary>list_contacts</summary>

```json
{
  "addressbook": "google",  // Optional, filter by addressbook
  "limit": 100              // Optional, max results (default: 100)
}
```
</details>

<details>
<summary>search_contacts</summary>

```json
{
  "query": "john",           // Required, searches name/email/phone/org
  "addressbook": "google",   // Optional
  "limit": 50                // Optional, default: 50
}
```
</details>

<details>
<summary>get_contact</summary>

```json
{
  "uid": "abc123",    // Optional, exact UID match
  "name": "John"      // Optional, partial name match
}
```
</details>

## Options Reference

### services.pim.calendar

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable` | bool | false | Enable calendar sync |
| `defaultCalendar` | string | null | Default calendar for new events |
| `accounts.<name>.type` | enum | - | "google", "caldav", or "http" |
| `accounts.<name>.tokenFile` | string | null | OAuth token file path (google) |
| `accounts.<name>.clientId` | string | null | OAuth client ID (google) |
| `accounts.<name>.clientSecretFile` | path | null | OAuth client secret file (google) |
| `accounts.<name>.url` | string | null | CalDAV server URL |
| `accounts.<name>.username` | string | null | CalDAV username |
| `accounts.<name>.passwordFile` | path | null | CalDAV password file |
| `accounts.<name>.icsUrl` | string | null | HTTP ICS URL (read-only) |
| `accounts.<name>.localPath` | string | null | Custom local storage path |
| `accounts.<name>.readOnly` | bool | false | Disable local→remote sync |
| `sync.frequency` | string | "5m" | Sync interval |
| `sync.conflictResolution` | enum | "remote" | "remote" or "local" wins |

### services.pim.contacts

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable` | bool | false | Enable contacts sync |
| `accounts.<name>.type` | enum | - | "google" or "carddav" |
| `accounts.<name>.tokenFile` | string | null | OAuth token file path |
| `accounts.<name>.clientId` | string | null | OAuth client ID |
| `accounts.<name>.clientSecretFile` | path | null | OAuth client secret file |
| `accounts.<name>.url` | string | null | CardDAV server URL |
| `accounts.<name>.username` | string | null | CardDAV username |
| `accounts.<name>.passwordFile` | path | null | CardDAV password file |
| `accounts.<name>.localPath` | string | null | Custom local storage path |

### services.pim.mcp

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable` | bool | true | Enable MCP server for AI access |

## Related Projects

- [axios](https://github.com/kcalvelli/axios) - Modular NixOS distribution
- [axios-ai-mail](https://github.com/kcalvelli/axios-ai-mail) - AI-powered email for NixOS
- [vdirsyncer](https://vdirsyncer.pimutils.org/) - Underlying sync engine
- [khal](https://khal.readthedocs.io/) - CLI calendar application
- [khard](https://khard.readthedocs.io/) - CLI contacts application

## License

MIT
