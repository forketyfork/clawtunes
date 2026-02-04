{
  description = "Clawtunes - CLI app to control Apple Music";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        pythonEnv = pkgs.python312.withPackages (ps: with ps; [
          # Core dependencies
          click

          # Development dependencies
          pytest
          pytest-cov
          black
          ruff
          mypy
          build

          # Additional useful tools
          ipython
          pip
        ]);

      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python environment
            pythonEnv

            # System dependencies
            git

            # Optional: Useful utilities
            fd
            ripgrep
            tree
          ];

          shellHook = ''
            echo "🎵 Clawtunes development environment loaded!"
            echo ""
            echo "Python: $(python --version)"
            echo "Available commands:"
            echo "  clawtunes      - Run clawtunes CLI (uses local source)"
            echo "  pytest         - Run tests"
            echo ""

            # Add src directory to PYTHONPATH for development
            export PYTHONPATH="$PWD/src:$PYTHONPATH"

            # Create clawtunes wrapper script in a temporary bin directory
            mkdir -p .nix-bin
            cat > .nix-bin/clawtunes <<'EOF'
#!/usr/bin/env bash
exec python -m clawtunes.cli "$@"
EOF
            chmod +x .nix-bin/clawtunes
            export PATH="$PWD/.nix-bin:$PATH"
          '';

          # Environment variables
          PYTHONPATH = "${pythonEnv}/${pythonEnv.sitePackages}";
        };

        # Package definition for clawtunes
        packages.default = pkgs.python312Packages.buildPythonApplication {
          pname = "clawtunes";
          version = "0.1.0";

          src = ./.;

          format = "pyproject";

          nativeBuildInputs = with pkgs.python312Packages; [
            hatchling
          ];

          propagatedBuildInputs = with pkgs.python312Packages; [
            click
          ];

          checkInputs = with pkgs.python312Packages; [
            pytest
            pytest-cov
          ];

          meta = with pkgs.lib; {
            description = "CLI app to control Apple Music";
            homepage = "https://github.com/forketyfork/clawtunes";
            license = licenses.mit;
            maintainers = [ ];
          };
        };

        # Make the app directly runnable
        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/clawtunes";
        };
      }
    );
}
