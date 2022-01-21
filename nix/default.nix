{ system ? builtins.currentSystem }:
rec {
  sources = import ./sources.nix;

  nixpkgs = import sources.nixpkgs { inherit system; };
}
