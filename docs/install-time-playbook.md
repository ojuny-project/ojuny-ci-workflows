# Install time playbook

Date: 2026-11-07

This playbook defines how an install report becomes a result. The benchmark is
manual by nature, but the report and the result generation are automatic.

## Input files

The installer writes three files on the installed system:

- `ojuny-install.log`: timestamped phases.
- `install-report.json`: ISO, template and environment identity.
- `first-boot.log`: kernel start, display manager, session ready and login
  ready.

## Result generation

Run the report app on the directory:

```console
$ nix run .#install-report -- /path/to/report --output-dir /path/to/result
```

It writes:

- `result.json`
- `result.md`
- `result.html` with inline SVG phase bars

The result is private by default. Publish by pull request or issue attachment
only if desired.

## Identity

The result identity is:

- ISO system closure hash
- template source and revision
- installer and ISO variant
- environment fingerprint
- VM spec identifier for VM runs

A commit is recorded when available, but it is not the primary key.

## VM track

- Use the published VM spec with pinned CPU model, vCPU count, RAM, disk, cache
  mode, network backend, firmware and QEMU version.
- The unattended ISO run is automatic in the heavy tier.
- A normal install in the same VM spec is a valid manual run.
- The baseline result is published for the spec.

## Physical track

- Use the same device, USB drive, enclosure, cable, port and network for every
  run.
- Three runs per selected ISO.
- Report the median and the spread.
- A different device, enclosure or network is a labelled configuration.
- Do not merge different configurations.

## Run set

- attended online
- attended discovery
- attended offline
- unattended offline

The persistent image is out of scope.

## Current status

The report app and the schemas are implemented and unit-tested with synthetic
fixtures. The installer collection code, the VM baseline and the physical runs
remain in `docs/heavy-testing.md`.
