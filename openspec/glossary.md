# cairn-dav Glossary

## Core Concepts

### CalDAV
Calendar Distributed Authoring and Versioning. A protocol for accessing calendar data on a remote server. Google Calendar exposes a CalDAV endpoint.

### CardDAV
Contact Distributed Authoring and Versioning. A protocol for accessing contact/address book data on a remote server. Google Contacts exposes a CardDAV endpoint.

### vdirsyncer
A command-line tool to synchronize calendars and contacts between servers and local storage. Supports CalDAV, CardDAV, Google Calendar, Google Contacts, and HTTP ICS feeds.

### khal
A CLI calendar application that reads from local `.ics` files (typically synced by vdirsyncer). Provides both command-line and TUI interfaces.

### khard
A CLI contacts/address book application that reads from local `.vcf` files (typically synced by vdirsyncer).

### MCP (Model Context Protocol)
A protocol for AI assistants to access external tools and data sources. cairn-dav provides an MCP server for calendar and contacts access.

## Configuration Terms

### Storage (vdirsyncer)
A vdirsyncer storage is a source or destination for calendar/contact data. Can be local filesystem, CalDAV server, Google Calendar, etc.

### Pair (vdirsyncer)
A vdirsyncer pair defines a synchronization relationship between two storages (typically remote ↔ local).

### Collection
A single calendar or address book. One Google account may have multiple calendars (collections).

### OAuth Token
An authentication token obtained via OAuth2 flow. Required for Google Calendar/Contacts access. Stored in a file and refreshed automatically.

## NixOS/Nix Terms

### Flake
A Nix feature for hermetic, reproducible package definitions with locked dependencies.

### NixOS Module
A Nix file that defines configuration options and their implementation. Modules compose to build a complete system.

### home-manager
A Nix tool for managing user-level configuration (dotfiles, user services) declaratively.

### agenix
A Nix-native secrets management tool using age encryption. Secrets are encrypted in the repo and decrypted at activation time.

### mkEnableOption
A Nix function that creates a boolean enable option with standard description.

### mkOption
A Nix function that creates a typed configuration option.

### mkIf
A Nix function that conditionally includes configuration based on a boolean.

## File Formats

### ICS (iCalendar)
Standard file format for calendar events. Extension: `.ics`

### vCard (VCF)
Standard file format for contact information. Extension: `.vcf`

## Google-Specific Terms

### Google Calendar API
Google's REST API for calendar access. NOT what vdirsyncer uses (it uses CalDAV).

### Google People API
Google's REST API for contacts access. More reliable than CardDAV but requires different implementation.

### Google CalDAV Endpoint
Google's CalDAV-compatible interface. Used by vdirsyncer's `google_calendar` storage type.

### Google CardDAV Endpoint
Google's CardDAV-compatible interface. Used by vdirsyncer's `google_contacts` storage type. Reportedly less reliable than People API.

## Project Terms

### cairn-dav
This project. Declarative NixOS module for CalDAV/CardDAV sync with MCP integration.

### cairn
The parent project. A modular NixOS distribution that can import cairn-dav as a flake input.

### cairn-mail
Sibling project. AI-powered email management for NixOS. cairn-dav follows similar patterns.

### mcp-dav
The MCP server component of cairn-dav. Provides AI access to calendar and contacts.
