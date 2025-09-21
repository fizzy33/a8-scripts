{
  description = "a8-scripts - Accur8 build and deployment scripts";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        a8-scripts-drv = pkgs.callPackage ./default.nix {
          inherit system;
          src = self;
        };
        a8-scripts-pkg = a8-scripts-drv.a8-scripts;
      in
      {
        # Packages output - properly exposed when used as flake input
        packages = {
          default = a8-scripts-pkg;
          a8-scripts = a8-scripts-pkg;
        };

        # Dev shell for development
        devShells.default = pkgs.mkShell {
          buildInputs = [ a8-scripts-pkg ];
        };

        # Apps if needed
        apps.default = flake-utils.lib.mkApp {
          drv = a8-scripts-pkg;
        };
      }
    ) // {
      # System-independent outputs
      # Overlay for those who prefer overlay approach
      overlays.default = final: prev:
        let
          a8-scripts-drv = final.callPackage ./default.nix {
            system = prev.system;
            src = self;
          };
        in {
          a8-scripts = a8-scripts-drv.a8-scripts;
        };

      # Keep backward compatibility lib function if needed
      lib.mkA8Scripts = { pkgs, system ? pkgs.system }:
        let
          a8-scripts-drv = pkgs.callPackage ./default.nix {
            inherit system;
            src = self;
          };
        in
          a8-scripts-drv.a8-scripts;
    };
}