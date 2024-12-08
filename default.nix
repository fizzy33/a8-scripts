{
  system,
  python3,
  openjdk11_headless,
  makeWrapper,
  lib,
  src,
  stdenv,
}:
{

  a8-scripts = stdenv.mkDerivation {
    name = "a8-scripts";

    inherit src;

    buildInputs = [ python3 openjdk11_headless makeWrapper ];

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
        echo $launcher --l-launcherJson $scriptFile.json '$@' >> $scriptFile
        chmod +x $scriptFile
      }

      fixExec a8-versions
      fixExec a8-codegen
      fixExec a8-zero
      fixExec a8-zoo
      fixExec honeybadger
      # fixExec run-pgbackrest

      patchShebangs $out/bin;

      cp -r $src/pydevops $out/pydevops

      '';

    installPhase = "echo hello > /dev/null";

    postFixup = ''

      wrapProgram $out/bin/run-pgbackrest \
          --set PATH ${lib.makeBinPath [
            python3
          ]}

      wrapProgram $out/bin/a8-launcher.py \
          --set PATH ${lib.makeBinPath [
            openjdk11_headless
          ]}

      wrapProgram $out/bin/coursier \
          --set PATH ${lib.makeBinPath [
            openjdk11_headless
          ]}

    '';
  };

}
