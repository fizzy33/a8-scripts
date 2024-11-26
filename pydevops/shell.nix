{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "python-dev-env";

  buildInputs = with pkgs; [
    python3           # Base Python interpreter
    python3Packages.mypy  # Type checker for Python
    python3Packages.ipython # Interactive Python shell
    # python3Packages.virtualenv # For setting up a virtual environment
  ];

  shellHook = ''
    echo "Environment loaded with Python, mypy, and IPython."

  '';
}