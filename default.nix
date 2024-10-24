{ system ? builtins.currentSystem
, sources ? import ./nix/sources.nix
, nixpkgs ? import sources.nixpkgs { inherit system; }
, lib ? nixpkgs.lib
, src ? lib.cleanSource ./.
}:
{

  a8-scripts = nixpkgs.stdenv.mkDerivation {
    name = "a8-scripts";

    inherit src;

    buildInputs = [ nixpkgs.python3 nixpkgs.openjdk11_headless nixpkgs.makeWrapper ];

    buildPhase = ''
      mkdir -p $out/bin
      for script in $src/bin/*; do
        cp --no-dereference $script $out/bin/$(basename $script)
      done

      function fixExec() {
        local script=$1
        local scriptFile=$out/bin/$script
        local launcher=$out/bin/a8-launcher.py
        rm $scriptFile 
        #echo creating launcher $scriptFile -- $out  
        echo '#!/bin/sh' > $scriptFile
        echo $launcher --l-launcherJson $scriptFile.json >> $scriptFile
        chmod +x $scriptFile
      }

      fixExec a8-versions
      fixExec a8-codegen
      fixExec a8-zero
      fixExec a8-zoo
      fixExec honeybadger

      patchShebangs $out/bin;
      '';

    installPhase = "echo hello > /dev/null";

    postFixup = ''

      wrapProgram $out/bin/a8-launcher.py \
          --set PATH ${lib.makeBinPath [
            nixpkgs.openjdk11_headless
          ]}

      wrapProgram $out/bin/coursier \
          --set PATH ${lib.makeBinPath [
            nixpkgs.openjdk11_headless
          ]}

    '';
  };

}
