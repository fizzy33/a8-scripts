# a8-scripts

Accur8 build and deployment scripts collection.

## Installation

### Using Nix Flakes (Recommended)

This repository is packaged as a Nix flake, making it easy to use as an input in other flake-based projects.

#### As a flake input

Add to your `flake.nix`:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    a8-scripts.url = "github:fizzy33/a8-scripts";
  };

  outputs = { self, nixpkgs, a8-scripts, ... }: {
    # Use in your packages
    packages.x86_64-linux.myPackage = pkgs.mkDerivation {
      buildInputs = [
        a8-scripts.packages.x86_64-linux.default
        # or
        a8-scripts.packages.x86_64-linux.a8-scripts
      ];
      # ...
    };
  };
}
```

#### Using the overlay

The flake provides an overlay that adds `a8-scripts` to nixpkgs:

```nix
{
  outputs = { self, nixpkgs, a8-scripts, ... }: {
    nixosConfigurations.mySystem = nixpkgs.lib.nixosSystem {
      modules = [
        {
          nixpkgs.overlays = [ a8-scripts.overlays.default ];
          # Now you can use pkgs.a8-scripts anywhere
          environment.systemPackages = [ pkgs.a8-scripts ];
        }
      ];
    };
  };
}
```

#### Building directly

```bash
# Build the package
nix build github:fizzy33/a8-scripts

# Run in a shell
nix shell github:fizzy33/a8-scripts

# Enter development shell
nix develop github:fizzy33/a8-scripts
```

### Legacy Usage (without flakes)

For systems not using flakes, you can still import the package using the traditional Nix approach:

```nix
let
  a8-scripts-src = builtins.fetchGit {
    url = "https://github.com/fizzy33/a8-scripts.git";
    ref = "master";
  };

  a8-scripts = (import "${a8-scripts-src}/default.nix" {
    inherit (pkgs) system python3 openjdk11_headless makeWrapper lib stdenv;
    src = a8-scripts-src;
  }).a8-scripts;
in
  # Use a8-scripts in your derivation
  pkgs.mkDerivation {
    buildInputs = [ a8-scripts ];
    # ...
  }
```

## Available Commands

After installation, the following commands will be available:

- `a8-versions` - Version management tool
- `a8-codegen` - Code generation utilities
- `a8-zero` - Zero deployment tool
- `a8-zoo` - Zoo management utilities
- `honeybadger` - Honeybadger integration
- `coursier` - Coursier dependency management
- `a8-launcher.py` - Python launcher script

## Development

To work on a8-scripts locally:

```bash
# Clone the repository
git clone https://github.com/fizzy33/a8-scripts.git
cd a8-scripts

# Enter development shell
nix develop

# Build the package
nix build

# Test the build
./result/bin/a8-versions --help
```

## Flake Outputs

The flake provides the following outputs:

- `packages.${system}.default` - The main a8-scripts package
- `packages.${system}.a8-scripts` - Same as default, explicit name
- `overlays.default` - Overlay that adds a8-scripts to nixpkgs
- `devShells.${system}.default` - Development shell with a8-scripts

## Requirements

- Nix 2.4+ with flakes enabled (for flake usage)
- Nix (any version for legacy usage)

## License

See LICENSE file for details.