{ system ? builtins.currentSystem
, sources ? import ./nix/sources.nix
, nixpkgs ? import sources.nixpkgs { inherit system; }
, lib ? nixpkgs.lib
, src ? lib.cleanSource ./.
}:
{ }
