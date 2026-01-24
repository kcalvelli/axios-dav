# axios-dav home-manager module
# Generates vdirsyncer, khal, and khard configurations
{
  config,
  lib,
  pkgs,
  osConfig ? { },
  ...
}:
let
  cfg = osConfig.services.axios-dav or config.services.axios-dav or { };
  calendarEnabled = cfg.calendar.enable or false;
  contactsEnabled = cfg.contacts.enable or false;
  enabled = cfg.enable or false;

  # TODO: Implement config generation functions
  # generateVdirsyncerConfig = ...
  # generateKhalConfig = ...
  # generateKhardConfig = ...
in
{
  # Allow this module to work standalone (without NixOS module)
  options.services.axios-dav = lib.mkOption {
    type = lib.types.attrs;
    default = { };
    description = "axios-dav configuration (usually set via NixOS module)";
  };

  config = lib.mkIf enabled {
    # Install user packages
    home.packages =
      with pkgs;
      [
        vdirsyncer
        khal
      ]
      ++ lib.optionals contactsEnabled [ khard ];

    # vdirsyncer configuration
    # TODO: Generate from cfg.calendar.accounts and cfg.contacts.accounts
    # home.file.".config/vdirsyncer/config".text = generateVdirsyncerConfig cfg;

    # khal configuration
    # TODO: Generate from cfg.calendar options
    # home.file.".config/khal/config".text = generateKhalConfig cfg;

    # khard configuration (if contacts enabled)
    # TODO: Generate from cfg.contacts options
    # home.file.".config/khard/config".text = lib.mkIf contactsEnabled (generateKhardConfig cfg);

    # Systemd user service for vdirsyncer sync
    systemd.user.services.vdirsyncer-sync = {
      Unit = {
        Description = "vdirsyncer: sync calendars and contacts";
        After = [ "network.target" ];
      };
      Service = {
        Type = "oneshot";
        ExecStart = "${pkgs.vdirsyncer}/bin/vdirsyncer sync";
        StandardOutput = "journal";
        StandardError = "journal";
      };
    };

    # Timer for periodic sync
    systemd.user.timers.vdirsyncer-sync = {
      Unit.Description = "Run vdirsyncer sync periodically";
      Timer = {
        OnCalendar = "*:0/5"; # TODO: Use cfg.sync.frequency
        Persistent = true;
        RandomizedDelaySec = "30s";
      };
      Install.WantedBy = [ "timers.target" ];
    };

    # Systemd service for metasync (metadata like colors, names)
    systemd.user.services.vdirsyncer-metasync = {
      Unit.Description = "vdirsyncer: metasync (names/colors)";
      Service = {
        Type = "oneshot";
        ExecStart = "${pkgs.vdirsyncer}/bin/vdirsyncer metasync";
      };
    };

    # Timer for daily metasync
    systemd.user.timers.vdirsyncer-metasync = {
      Unit.Description = "Run vdirsyncer metasync daily";
      Timer = {
        OnCalendar = "daily";
        Persistent = true;
        RandomizedDelaySec = "5m";
      };
      Install.WantedBy = [ "timers.target" ];
    };

    # MCP server configuration
    # TODO: Add mcp-dav to MCP config when mcp.enable = true
  };
}
