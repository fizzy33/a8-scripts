{
  description = "a8-scripts - Accur8 build and deployment scripts";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    let
      # Define supported systems
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      # Create outputs for each system
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;

      # Package builder function
      mkPackage = system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          a8-scripts-drv = pkgs.callPackage ./default.nix {
            inherit system;
            src = self;
          };
        in
          a8-scripts-drv.a8-scripts;
    in
    {
      # Packages output
      packages = forAllSystems (system: {
        default = mkPackage system;
        a8-scripts = mkPackage system;
      });

      # Overlay output
      overlays.default = final: prev: {
        a8-scripts = mkPackage prev.system;
      };

      # Dev shell for development
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = pkgs.mkShell {
            buildInputs = [ self.packages.${system}.default ];
          };
        });

      # Legacy support - expose the function for backward compatibility
      lib.mkA8Scripts = { system, nixpkgs }:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
          pkgs.callPackage ./default.nix {
            inherit system;
            src = self;
          };
    };
}