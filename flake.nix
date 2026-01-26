{
  description = "Declarative CalDAV/CardDAV sync for NixOS with MCP integration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      home-manager,
      flake-utils,
    }:
    let
      # Systems to support
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      # Helper to generate per-system outputs
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    in
    {
      # NixOS module
      nixosModules = {
        default = self.nixosModules.axios-dav;
        axios-dav = ./modules;
      };

      # home-manager module
      homeModules = {
        default = self.homeModules.axios-dav;
        axios-dav = ./home;
      };

      # Overlay for custom packages
      overlays.default = final: prev: {
        mcp-dav =
          self.packages.${prev.system}.mcp-dav or (throw "mcp-dav not available for ${prev.system}");
      };

      # Per-system outputs (packages, devShells)
      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          # MCP server for calendar and contacts access
          mcp-dav = pkgs.python3Packages.buildPythonApplication {
            pname = "mcp-dav";
            version = "0.1.0";
            format = "pyproject";

            src = ./pkgs/mcp-dav;

            build-system = with pkgs.python3Packages; [
              setuptools
            ];

            dependencies = with pkgs.python3Packages; [
              icalendar # For parsing .ics calendar files
              vobject # For parsing .vcf contact files
              fastmcp # MCP server framework
            ];

            # No tests yet
            doCheck = false;

            meta = {
              description = "MCP server for calendar and contacts access";
              homepage = "https://github.com/kcalvelli/axios-dav";
              license = pkgs.lib.licenses.mit;
              mainProgram = "mcp-dav";
            };
          };

          default = self.packages.${system}.mcp-dav;
        }
      );

      # Development shell
      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.mkShell {
            buildInputs = with pkgs; [
              # Nix tools
              nil # Nix LSP
              nixfmt-rfc-style

              # Python for MCP server development
              python3
              python3Packages.pip

              # Testing tools
              vdirsyncer
              khal
              khard
            ];

            shellHook = ''
              echo "axios-dav development shell"
              echo "Tools available: nil, nixfmt, python3, vdirsyncer, khal, khard"
            '';
          };
        }
      );

      # Formatter
      formatter = forAllSystems (system: nixpkgs.legacyPackages.${system}.nixfmt-rfc-style);
    };
}
