let
  # Import Nixpkgs so we get the package set and the "standard library".
  # See the file `nix/nixpkgs.nix` for details and background.
  pkgs = import ./nix/nixpkgs.nix {};

  # Define a Python environment. The exact versions aren't specified here, but
  # they *are* pinned. Nixpkgs provides a snapshot of the ecosystem. You can
  # override package versions to specific ones if you'd like though.
  pythonEnv = pkgs.python38.withPackages (ps: [
    ps.asyncpg
    ps.black
    ps.cryptography
    ps.fastapi
    ps.flake8
    ps.funcy
    ps.hypothesis
    ps.isort
    ps.jinja2
    ps.mypy
    ps.pylint
    ps.pytest
    ps.typer
    ps.uvicorn
  ]);
in
  # Create a development environment with our Python packages and a few system
  # tools. Use Postgres 13 as our database. (This also makes the right version of
  # `libpq` available.)
  pkgs.mkShell {
    name = "nix-python-example";
    buildInputs = [
      pythonEnv           # Python environment.
      pkgs.overmind       # To manage our processes in the dev setup.
      pkgs.postgresql_13  # Database.
    ];
  }
