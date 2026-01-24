# axios-dav NixOS module
# Provides declarative CalDAV/CardDAV synchronization
{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.services.axios-dav;
in
{
  options.services.axios-dav = {
    enable = lib.mkEnableOption "axios-dav calendar and contacts sync";

    calendar = {
      enable = lib.mkEnableOption "Calendar sync via CalDAV";

      accounts = lib.mkOption {
        type = lib.types.attrsOf (
          lib.types.submodule {
            options = {
              type = lib.mkOption {
                type = lib.types.enum [
                  "google"
                  "caldav"
                  "http"
                ];
                description = "Calendar provider type";
              };

              # Google OAuth
              tokenFile = lib.mkOption {
                type = lib.types.nullOr lib.types.path;
                default = null;
                description = "Path to OAuth token file (agenix secret)";
              };

              clientId = lib.mkOption {
                type = lib.types.nullOr lib.types.str;
                default = null;
                description = "Google OAuth client ID";
              };

              clientSecretFile = lib.mkOption {
                type = lib.types.nullOr lib.types.path;
                default = null;
                description = "Path to Google OAuth client secret file";
              };

              # CalDAV
              url = lib.mkOption {
                type = lib.types.nullOr lib.types.str;
                default = null;
                description = "CalDAV server URL";
              };

              username = lib.mkOption {
                type = lib.types.nullOr lib.types.str;
                default = null;
                description = "CalDAV username";
              };

              passwordFile = lib.mkOption {
                type = lib.types.nullOr lib.types.path;
                default = null;
                description = "Path to CalDAV password file";
              };

              # HTTP ICS (read-only)
              icsUrl = lib.mkOption {
                type = lib.types.nullOr lib.types.str;
                default = null;
                description = "URL to ICS file for read-only subscription";
              };

              # Sync behavior
              readOnly = lib.mkOption {
                type = lib.types.bool;
                default = false;
                description = "If true, local changes are not synced back";
              };
            };
          }
        );
        default = { };
        description = "Calendar accounts to sync";
      };

      defaultCalendar = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Default calendar for new events (khal)";
      };
    };

    contacts = {
      enable = lib.mkEnableOption "Contacts sync via CardDAV";

      accounts = lib.mkOption {
        type = lib.types.attrsOf (
          lib.types.submodule {
            options = {
              type = lib.mkOption {
                type = lib.types.enum [
                  "google"
                  "carddav"
                ];
                description = "Contacts provider type";
              };

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
            };
          }
        );
        default = { };
        description = "Contacts accounts to sync";
      };
    };

    sync = {
      frequency = lib.mkOption {
        type = lib.types.str;
        default = "5m";
        description = "Sync frequency (systemd timer format)";
      };

      conflictResolution = lib.mkOption {
        type = lib.types.enum [
          "remote"
          "local"
        ];
        default = "remote";
        description = "Which side wins on sync conflict";
      };
    };

    mcp = {
      enable =
        lib.mkEnableOption "MCP server for AI calendar/contacts access"
        // {
          default = true;
        };
    };
  };

  config = lib.mkIf cfg.enable {
    # System-level configuration
    # Most config is in home-manager module

    # Ensure required packages are available
    environment.systemPackages = with pkgs; [
      vdirsyncer
      khal
    ] ++ lib.optionals cfg.contacts.enable [ khard ];
  };
}
