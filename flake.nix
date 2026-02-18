{
  description = "Office Hours Intake Bot development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs { inherit system; };
    in {
      devShell = pkgs.mkShell {
        buildInputs = with pkgs; [
          python311
          uv
          ruff
          cloudflared
          direnv
        ];

        shellHook = ''
          echo "Office Hours Intake Bot environment loaded"
          echo "Python: $(python3 --version)"
          echo "uv: $(uv --version)"
          echo "Use 'uv sync' to install project dependencies"
        '';
      };
    });
}
