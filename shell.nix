{ system ? builtins.currentSystem
, sources ? import ./nix/sources.nix
, nixpkgs ? import sources.nixpkgs { inherit system; }
}:
nixpkgs.mkShell {
  buildInputs = [
    nixpkgs.openjdk11_headless
    nixpkgs.python3
  ];
}
