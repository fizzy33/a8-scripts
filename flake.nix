{
  description = "a8-scripts flake";

  # Define the inputs of the flake (e.g., nixpkgs)
  inputs = {
    # Reference the Nixpkgs version to use for building
    nixpkgs.url = "nixpkgs/nixpkgs-unstable";
  };

  # Define the outputs, including packages, apps, etc.
  outputs = { self, nixpkgs }: {

    # Packages can be built with `nix build .#myPackage`
    packages = (nixpkgs.lib.genAttrs [ "x86_64-linux" "aarch64-darwin" "x86_64-darwin" ] (system: 
      {
        a8-scripts = (nixpkgs.legacyPackages.${system}.callPackage ./default.nix {
          inherit system;
          src = ./.; # Use the current directory as the source (Git repo root)
        }).a8-scripts;
      }
    ));

    # You can also define apps to run with `nix run .#myApp`
    # apps = {
    #   myApp = {
    #     # Wrap the package into an app
    #     # This assumes that `default.nix` defines a package with a "bin"
    #     # or a shell script that should be run.
    #     pkg = self.packages.myPackage;
    #   };
    # };

    # Example: devShell that can be entered with `nix develop`
    # devShell = mkShell {
    #   buildInputs = [ self.packages.a8-scripts ];
    # };
  };
}