{
  description = "Ojuny CI runner and shared workflows";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          python = pkgs.python3;
        in
        {
          ojuny-ci = python.pkgs.buildPythonApplication {
            pname = "ojuny-ci";
            version = "0.1.0";
            pyproject = true;
            src = ./.;
            build-system = [ python.pkgs.setuptools ];
            preCheck = ''
              export PYTHONPATH="$PWD/src"
            '';
            checkPhase = ''
              python -m unittest discover -s tests -v
            '';
            postInstall = ''
              mkdir -p $out/share/ojuny-ci/schemas
              install -Dm644 repos.json $out/share/ojuny-ci/repos.json
              install -Dm644 schemas/*.json $out/share/ojuny-ci/schemas/
            '';
          };

          default = self.packages.${system}.ojuny-ci;
        }
      );

      apps = forAllSystems (system: {
        ci = {
          type = "app";
          program = "${self.packages.${system}.ojuny-ci}/bin/ojuny-ci";
        };
        default = self.apps.${system}.ci;
      });

      checks = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          runner = self.packages.${system}.ojuny-ci;

          schemas = pkgs.runCommand "check-schemas" {
            nativeBuildInputs = [ pkgs.python3 ];
          } ''
            cd ${./.}
            python3 -m unittest tests.test_schemas -v
            touch $out
          '';

          default = pkgs.runCommand "check-ojuny-ci" { } ''
            echo ${self.checks.${system}.runner} >/dev/null
            echo ${self.checks.${system}.schemas} >/dev/null
            touch $out
          '';
        }
      );

      devShells = forAllSystems (system: {
        default = nixpkgs.legacyPackages.${system}.mkShell {
          packages = [
            nixpkgs.legacyPackages.${system}.python3
            nixpkgs.legacyPackages.${system}.python3Packages.pytest
          ];
        };
      });
    };
}
