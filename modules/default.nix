# cairn-dav NixOS module
# Provides declarative CalDAV/CardDAV synchronization under services.pim
{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.services.pim;
  calCfg = cfg.calendar or { };
  contactsCfg = cfg.contacts or { };
in
{
  options.services.pim = {
    # Calendar options
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
                type = lib.types.nullOr lib.types.str;
                default = null;
                description = "Path to OAuth token file (must be writable for token refresh)";
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

              # Custom paths (for backward compatibility with existing setups)
              localPath = lib.mkOption {
                type = lib.types.nullOr lib.types.str;
                default = null;
                description = "Custom local storage path. Defaults to ~/.calendars/<account-name>/";
                example = "~/.calendars/";
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
    };

    # Contacts options
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
                type = lib.types.nullOr lib.types.str;
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

              localPath = lib.mkOption {
                type = lib.types.nullOr lib.types.str;
                default = null;
                description = "Custom local storage path. Defaults to ~/.contacts/<account-name>/";
              };
            };
          }
        );
        default = { };
        description = "Contacts accounts to sync";
      };
    };

    # MCP server option
    mcp = {
      enable = lib.mkEnableOption "MCP server for AI calendar/contacts access" // {
        default = true;
      };
    };
  };

  config = lib.mkIf (calCfg.enable or false || contactsCfg.enable or false) {
    # System-level configuration
    # Most config is in home-manager module

    # Ensure required packages are available
    environment.systemPackages =
      with pkgs;
      lib.optionals (calCfg.enable or false) [
        vdirsyncer
        khal
      ]
      ++ lib.optionals (contactsCfg.enable or false) [ khard ];
  };
}
