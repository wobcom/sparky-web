{
  description = "SPARKY-Web";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }: flake-utils.lib.eachDefaultSystem (system: let
    pkgs = nixpkgs.legacyPackages.${system};
    python-env = (pkgs.python311.withPackages (ps: with ps; [
      django
      django-bootstrap5
      fontawesomefree
      macaddress
      psycopg2
      requests
      pytz
      gitpython
      # some tools pycharm wants
      setuptools
    ]));
  in {
    packages = {
      python-env = python-env;
    };
    devShells.default = pkgs.mkShell {
      buildInputs = [
        python-env
      ];
    };
  });
}
