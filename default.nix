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
      nixpkgs.makeWrapper
    ];

    buildInputs = [
      nixpkgs.python3
    ];

    installPhase = ''
      mkdir -p $out/bin

      # Copy all the source into $out/bin
      cp -r ./* $out/bin/

      # Remove unneeded Nix code
      rm $out/bin/*.{nix,lock}

      # Add runtime dependency.
      #
      # Currently breaks the launcher internal logic
      wrapProgram $out/bin/a8-launcher.py \
        --argv0 '$0' \
        --prefix PATH : ${lib.makeBinPath [ nixpkgs.openjdk11_headless ]}
    '';
  };
}
