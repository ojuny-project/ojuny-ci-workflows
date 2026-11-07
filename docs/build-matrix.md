# Build matrix

Date: 2026-11-07

x86_64-linux is the primary release platform. The one ARM target for plan 01 is
generic `aarch64-linux`. Specialized targets such as T2, Apple Silicon,
Snapdragon, Raspberry Pi and NVIDIA stay in plan 05.

| Surface | x86_64-linux | aarch64-linux | Tier |
| --- | --- | --- | --- |
| Fast checks | all repositories | evaluation only | Fast |
| Package builds | all repositories | supported packages | Nix |
| System builds | fixture host | fixture host when supported | Heavy |
| ISO builds | all variants | generic ISO when supported | Heavy |
| VM tests | yes | when a runner is available | Heavy |
| Acceptance | yes | no | Heavy |
| Install report | yes | no | Nix |
| Install time | yes | no | Manual |

## Status

- The manifest records `x86_64-linux` for every repository and both systems for
  `ojuny-ci-workflows`.
- The generic aarch64 evaluation is not enabled yet. It needs a runner and a
  measured list of supported attributes.
- The specialized targets are out of scope for plan 01.
- The matrix is applied to the coverage table in
  `docs/coverage-matrix.md`.
