{ system ? builtins.currentSystem
, sources ? import ./nix/sources.nix
, nixpkgs ? import sources.nixpkgs { inherit system; }
, lib ? nixpkgs.lib
, src ? lib.cleanSource ./.
}:
{
  # Encode a common pattern for those Haxe scripts.
  a8-scripts = nixpkgs.stdenv.mkDerivation {
    name = "a8-scripts";

    inherit src;

    nativeBuildInputs = [
#      nixpkgs.makeWrapper
    ];

    buildInputs = [
      nixpkgs.python3
    ];

    installPhase = ''
      mkdir -p $out/bin

      echo boom

      # Copy all the source into $out/bin
      cp -r bin/* $out/bin

      # Add runtime dependency.
      #
      # Currently breaks the launcher internal logic
      #wrapProgram $out/bin/a8-launcher.py \
      #  --argv0 '$0' \
      #  --prefix PATH : ${lib.makeBinPath [ nixpkgs.openjdk11_headless ]}
    '';
  };
}
