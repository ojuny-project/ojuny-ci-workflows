# Coverage matrix

Date: 2026-11-07

Status: implemented, partial or pending.

| Surface | Fast | Nix | Heavy |
| --- | --- | --- | --- |
| Plan 01 outputs | implemented | implemented | pending |
| Template | implemented | pending | pending |
| Installer | implemented | implemented | pending |
| CLI | implemented | implemented | pending |
| Desktop and GUIs | implemented | partial | pending |
| Patches | implemented | partial | pending |
| Cache discovery | implemented | implemented | pending |
| CI server | implemented | implemented | pending |
| Test flakes | implemented | implemented | pending |
| Docs and site | implemented | partial | pending |
| Release boundary | partial | pending | pending |

Pending means the check is defined in the plan or manifest but needs KVM,
ISO artifacts, the CI server, physical hardware or a heavy build.

## Implemented checks

- `ojuny-ci-workflows`: `checks.runner`, `checks.schemas`, `checks.default`.
- `ojuny-template`: `hardware-profile`, `bind-args`, `module-tree-current`.
- `ojuny-installer`: `format`, `extensions`, `module`, `unattended`,
  `offline-install-closure`, `install-report`.
- `ojuny-cli`: `lint`, `binary-programs`, `cli-reference-current`, `tests`,
  `ojuny-cli`, `ojuny-patches-cli`.
- `ojuny-desktop`: `menu-extra-entries`, `wallpaper-set`.
- `ojuny-manual`: `manual-summary`, `default`.
- `ojuny-patches`: `annotations`, `catalogue`, `default`.
- `ojuny-test-flakes`: `examples`, `default`.
- `ojuny-site`: `apps.ci` runs the site check, docs links, metrics and build.
- `nix-cache-discovery`: `package`, `vm`.
- `ojuny-ci-server`: `settings-eval`, `jobsets-schema`, `storage-assertions`,
  `options-coverage`, `default`.
- `nix-cleaner`, `nix-settings-gui`, `nix-regedit`, `nix-shell-gui`,
  `simple-nix-update-gui`: package and default checks.
- `nix-settings-gui` also builds `checks.minimal`, the build without the
  ojuny-specific widgets.
- `ojuny-welcome`: package and default checks.

## Pending checks

- `install-report-schema` example validation is implemented in the runner schema
  test.
- `acceptance-inventory` and `ocr-selftest` are scaffolded with draft flows.
- `options-reference-current` needs a non-mutating wrapper.
- The build matrix and aarch64 checks.
- The template fixture system build.
- The VM baseline.
- The acceptance install, session, rollback and chained jobs.
- The OCR stability job.
- The heavy ISO, reproducibility and release-boundary checks.
- The aggregate Hydra contract.
- The `ojuny-ci-server` runtime: Hydra admin login, jobset upsert, cache
  discovery, network mounts, remote builders, Proxmox image and aarch64 build.
  The server list is in `~/repos/ojuny-ci-server/docs/heavy-testing.md`.
