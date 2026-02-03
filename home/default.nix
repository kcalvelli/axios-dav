# axios-dav home-manager module
# Generates vdirsyncer, khal, and khard configurations
# Reads from services.pim.calendar and services.pim.contacts
{
  config,
  lib,
  pkgs,
  osConfig ? { },
  inputs ? { },
  ...
}:
let
  # Get config from NixOS module or standalone home-manager config
  pimCfg = osConfig.services.pim or config.services.pim or { };
  calCfg = pimCfg.calendar or { };
  contactsCfg = pimCfg.contacts or { };
  mcpCfg = pimCfg.mcp or { };

  calendarEnabled = calCfg.enable or false;
  contactsEnabled = contactsCfg.enable or false;
  mcpEnabled = (mcpCfg.enable or true) && (calendarEnabled || contactsEnabled);
  enabled = calendarEnabled || contactsEnabled;

  # mcp-dav package - try overlay first, then inputs
  mcp-dav =
    pkgs.mcp-dav or (
      if inputs ? axios-dav then
        inputs.axios-dav.packages.${pkgs.stdenv.hostPlatform.system}.mcp-dav
      else if inputs ? self then
        inputs.self.packages.${pkgs.stdenv.hostPlatform.system}.mcp-dav
      else
        throw "mcp-dav package not found. Add axios-dav overlay or ensure inputs.axios-dav is available."
    );

  # Calendar accounts (from NixOS module)
  calendarAccounts = calCfg.accounts or { };
  contactsAccounts = contactsCfg.accounts or { };

  # Sync settings
  syncCfg = calCfg.sync or { };
  syncFrequency = syncCfg.frequency or "5m";
  conflictResolution = syncCfg.conflictResolution or "remote";

  # Convert frequency like "5m" to OnCalendar format
  frequencyToOnCalendar =
    freq:
    let
      # Parse "5m" -> 5 minutes, "1h" -> hourly, etc.
      value = lib.strings.toInt (builtins.head (builtins.match "([0-9]+).*" freq));
      unit = builtins.head (builtins.match "[0-9]+([a-z]+)" freq);
    in
    if unit == "m" then
      "*:0/${toString value}"
    else if unit == "h" then
      "*:00"
    else
      "*:0/5"; # default to 5 min

  # Conflict resolution mapping
  conflictString = if conflictResolution == "remote" then "b wins" else "a wins";

  # Base paths
  calendarsPath = "~/.calendars";
  contactsPath = "~/.contacts";
  statusPath = "~/.local/share/vdirsyncer/status/";

  # Generate vdirsyncer config for a single calendar account
  generateCalendarStorage =
    name: account:
    let
      # Use custom localPath if specified, otherwise default to ~/.calendars/<name>/
      localPath =
        if account.localPath or null != null then account.localPath else "${calendarsPath}/${name}/";
      collections = if account.readOnly or false then ''["from b"]'' else ''["from a", "from b"]'';
    in
    ''
      [pair cal_${name}]
      a = "cal_${name}_local"
      b = "cal_${name}_remote"
      collections = ${collections}
      conflict_resolution = "${conflictString}"
      metadata = ["color", "displayname"]

      [storage cal_${name}_local]
      type = "filesystem"
      path = "${localPath}"
      fileext = ".ics"

      ${generateRemoteCalendarStorage name account}
    '';

  # Generate remote storage config based on account type
  generateRemoteCalendarStorage =
    name: account:
    if account.type == "google" then
      ''
        [storage cal_${name}_remote]
        type = "google_calendar"
        token_file = "${account.tokenFile}"
        client_id = "${account.clientId}"
        client_secret.fetch = ["command", "cat", "${toString account.clientSecretFile}"]
      ''
    else if account.type == "caldav" then
      ''
        [storage cal_${name}_remote]
        type = "caldav"
        url = "${account.url}"
        username = "${account.username}"
        password.fetch = ["command", "cat", "${toString account.passwordFile}"]
      ''
    else if account.type == "http" then
      ''
        [storage cal_${name}_remote]
        type = "http"
        url = "${account.icsUrl}"
      ''
    else
      throw "Unknown calendar type: ${account.type}";

  # Generate vdirsyncer config for a single contacts account
  generateContactsStorage =
    name: account:
    let
      localPath =
        if account.localPath or null != null then account.localPath else "${contactsPath}/${name}/";
    in
    ''
      [pair contacts_${name}]
      a = "contacts_${name}_local"
      b = "contacts_${name}_remote"
      collections = ["from a", "from b"]
      conflict_resolution = "${conflictString}"

      [storage contacts_${name}_local]
      type = "filesystem"
      path = "${localPath}"
      fileext = ".vcf"

      ${generateRemoteContactsStorage name account}
    '';

  # Generate remote contacts storage config
  generateRemoteContactsStorage =
    name: account:
    if account.type == "google" then
      ''
        [storage contacts_${name}_remote]
        type = "google_contacts"
        token_file = "${account.tokenFile}"
        client_id = "${account.clientId}"
        client_secret.fetch = ["command", "cat", "${toString account.clientSecretFile}"]
      ''
    else if account.type == "carddav" then
      ''
        [storage contacts_${name}_remote]
        type = "carddav"
        url = "${account.url}"
        username = "${account.username}"
        password.fetch = ["command", "cat", "${toString account.passwordFile}"]
      ''
    else
      throw "Unknown contacts type: ${account.type}";

  # Complete vdirsyncer config
  vdirsyncerConfig = ''
    # Auto-generated by axios-dav - do not edit manually
    # Source: services.pim.calendar and services.pim.contacts

    [general]
    status_path = "${statusPath}"

    ${lib.concatStringsSep "\n" (lib.mapAttrsToList generateCalendarStorage calendarAccounts)}
    ${lib.optionalString contactsEnabled (
      lib.concatStringsSep "\n" (lib.mapAttrsToList generateContactsStorage contactsAccounts)
    )}
  '';

  # Generate khal config
  # HTTP/ICS subscriptions store files directly in directory (no subdirs)
  # Google/CalDAV create subdirectories per calendar, requiring type=discover
  generateKhalCalendarEntry =
    name: account:
    let
      isHttpSubscription = account.type == "http";
      khalPath =
        if account.localPath or null != null then
          (if isHttpSubscription then account.localPath else "${account.localPath}*")
        else
          (if isHttpSubscription then "${calendarsPath}/${name}/" else "${calendarsPath}/${name}/*");
    in
    ''
      [[cal_${name}]]
      path = ${khalPath}
      ${lib.optionalString (!isHttpSubscription) "type = discover"}
      ${lib.optionalString (account.readOnly or false) "readonly = True"}
    '';

  khalConfig = ''
    # Auto-generated by axios-dav - do not edit manually

    [calendars]
    ${lib.concatStringsSep "\n" (lib.mapAttrsToList generateKhalCalendarEntry calendarAccounts)}

    [default]
    ${lib.optionalString (calCfg.defaultCalendar or null != null) ''
      default_calendar = ${calCfg.defaultCalendar}
    ''}
    highlight_event_days = True

    [locale]
    timeformat = %H:%M
    dateformat = %Y-%m-%d
    longdateformat = "%A, %B %d, %Y"
    datetimeformat = %Y-%m-%d %H:%M
    longdatetimeformat = "%A, %B %d, %Y %H:%M"

    [view]
    agenda_event_format = {calendar-color}{cancelled}{start-end-time-style} {title}{repeat-symbol}{reset}
  '';

  # Generate khard config
  # Google/CardDAV create subdirectories per collection (e.g., "default/")
  # khard needs path to the actual vcf files directory
  generateKhardAddressbookEntry =
    name: account:
    let
      # Google Contacts uses "default" as collection name
      # CardDAV may have multiple collections - use wildcard
      basePath =
        if account.localPath or null != null then account.localPath else "${contactsPath}/${name}/";
      # For Google, point to default/ subdirectory; for CardDAV, use glob
      khardPath = if account.type == "google" then "${basePath}default/" else "${basePath}";
    in
    ''
      [[contacts_${name}]]
      path = ${khardPath}
    '';

  khardConfig = ''
    # Auto-generated by axios-dav - do not edit manually

    [general]
    default_action = list
    editor = $EDITOR
    merge_editor = vimdiff

    [addressbooks]
    ${lib.concatStringsSep "\n" (lib.mapAttrsToList generateKhardAddressbookEntry contactsAccounts)}

    [contact table]
    display = formatted_name
    group_by_addressbook = yes
    reverse = no
    show_nicknames = no
    show_uids = no
    sort = last_name
    localize_dates = yes
  '';

in
{
  # Allow this module to work standalone (without NixOS module)
  options.services.pim = lib.mkOption {
    type = lib.types.attrs;
    default = { };
    description = "PIM configuration (calendar/contacts) - usually set via NixOS module";
  };

  config = lib.mkIf enabled {
    # Install user packages
    home.packages =
      with pkgs;
      lib.optionals calendarEnabled [
        vdirsyncer
        khal
      ]
      ++ lib.optionals contactsEnabled [ khard ]
      ++ lib.optionals mcpEnabled [ mcp-dav ];

    # vdirsyncer configuration
    xdg.configFile."vdirsyncer/config" = lib.mkIf calendarEnabled { text = vdirsyncerConfig; };

    # khal configuration
    xdg.configFile."khal/config" = lib.mkIf calendarEnabled { text = khalConfig; };

    # khard configuration (if contacts enabled)
    xdg.configFile."khard/khard.conf" = lib.mkIf contactsEnabled { text = khardConfig; };

    # Create calendar directories (only for accounts without custom localPath)
    home.file = lib.mkMerge [
      # Calendar directories
      (lib.mkIf calendarEnabled (
        lib.mapAttrs' (
          name: account:
          lib.nameValuePair ".calendars/${name}/.keep" {
            text = "";
            # Only create if no custom localPath is specified
            enable = (account.localPath or null) == null;
          }
        ) calendarAccounts
      ))
      # Contacts directories
      (lib.mkIf contactsEnabled (
        lib.mapAttrs' (
          name: account:
          lib.nameValuePair ".contacts/${name}/.keep" {
            text = "";
            enable = (account.localPath or null) == null;
          }
        ) contactsAccounts
      ))
    ];

    # Systemd user service for vdirsyncer sync (mkForce to override axios's home/calendar module)
    systemd.user.services.vdirsyncer-sync = lib.mkIf calendarEnabled (
      lib.mkForce {
        Unit = {
          Description = "vdirsyncer: sync calendars and contacts";
          After = [ "network-online.target" ];
          Wants = [ "network-online.target" ];
        };
        Service = {
          Type = "oneshot";
          ExecStart = "${pkgs.vdirsyncer}/bin/vdirsyncer sync";
          StandardOutput = "journal";
          StandardError = "journal";
        };
      }
    );

    # Timer for periodic sync (mkForce to override axios's home/calendar module)
    systemd.user.timers.vdirsyncer-sync = lib.mkIf calendarEnabled (
      lib.mkForce {
        Unit.Description = "Run vdirsyncer sync periodically";
        Timer = {
          OnCalendar = frequencyToOnCalendar syncFrequency;
          Persistent = true;
          RandomizedDelaySec = "30s";
        };
        Install.WantedBy = [ "timers.target" ];
      }
    );

    # Systemd service for metasync (metadata like colors, names)
    systemd.user.services.vdirsyncer-metasync = lib.mkIf calendarEnabled (
      lib.mkForce {
        Unit = {
          Description = "vdirsyncer: metasync (names/colors)";
          After = [ "network-online.target" ];
        };
        Service = {
          Type = "oneshot";
          ExecStart = "${pkgs.vdirsyncer}/bin/vdirsyncer metasync";
          StandardOutput = "journal";
          StandardError = "journal";
        };
      }
    );

    # Timer for daily metasync
    systemd.user.timers.vdirsyncer-metasync = lib.mkIf calendarEnabled (
      lib.mkForce {
        Unit.Description = "Run vdirsyncer metasync daily";
        Timer = {
          OnCalendar = "daily";
          Persistent = true;
          RandomizedDelaySec = "5m";
        };
        Install.WantedBy = [ "timers.target" ];
      }
    );

    # Initial discovery service (runs once after first sync)
    systemd.user.services.vdirsyncer-discover = lib.mkIf calendarEnabled {
      Unit = {
        Description = "vdirsyncer: discover collections";
        After = [ "network-online.target" ];
      };
      Service = {
        Type = "oneshot";
        ExecStart = "${pkgs.bash}/bin/bash -c '${pkgs.vdirsyncer}/bin/vdirsyncer discover --yes || true'";
        StandardOutput = "journal";
        StandardError = "journal";
      };
    };

    # MCP server configuration
    # When enabled, install mcp-dav and make its command path available
    # The actual MCP registration happens in the consuming config (e.g., axios)
    # by reading this module's output and adding to their MCP server list
    #
    # Example MCP server registration (in axios home/ai/mcp.nix):
    #   mcp-dav = {
    #     command = "${pkgs.mcp-dav}/bin/mcp-dav";
    #     env = {
    #       MCP_DAV_CALENDARS = "~/.calendars";
    #       MCP_DAV_CONTACTS = "~/.contacts";
    #     };
    #   };
  };
}
