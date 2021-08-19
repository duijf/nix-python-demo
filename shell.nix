let
  pkgs = import ./nix/nixpkgs.nix {};
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
pkgs.mkShell {
  name = "nix-python-example";
  buildInputs = [
    pythonEnv
    pkgs.overmind
    pkgs.postgresql_13
    pkgs.watchexec
  ];
}
