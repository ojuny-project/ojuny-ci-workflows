# ojuny-ci-workflows

Runner and shared workflows for Ojuny CI.

## Tiers

- **Fast**: formatting, pure evaluation, static checks and generated-file
  drift. Runs on every pull request and push.
- **Nix**: package builds and unit tests. Runs on pull requests and push for
  the touched repositories.
- **Heavy**: system builds, VM tests, ISO builds and reproducibility. Runs on
  Hydra, nightly and on tags. Advisory, not a required status.

## Manifest

`repos.json` lists every repository, its kind, its systems and its checks per
tier. `schemas/repos.schema.json` describes the shape.

A check is a flake attribute, a `script:` command or a `meta:` check.
Examples:

- `checks.x86_64-linux.hardware-profile`
- `hydraJobs`
- `meta:check-inventory`
- `script:npm run check`

## Usage

```console
$ nix run .#ci -- list
$ nix run .#ci -- run --tier fast --repo ojuny-template
$ nix run .#ci -- run --tier nix --changed
$ nix run .#ci -- run --tier all --json-file result.json --junit junit.xml
```

Exit codes:

- `0` all selected checks passed
- `1` at least one check failed
- `2` usage or manifest error
- `3` missing dependency
- `4` every selected check was skipped

## `apps.ci`

Every repository exposes `apps.ci` and runs its own fast and Nix checks. The
aggregate runner uses the same flake attributes.

## Local scripts

The scripts directly under `~/repos` are early-development fixtures. Proper CI
replaces them. They are not migrated or wrapped.

## Workflows

- `.github/workflows/reusable-ci.yml` is the reusable caller.
- `.github/workflows/ci.yml` runs the runner on this repository.

## Branch protection

Require the `fast` and `nix` jobs from `.github/workflows/ojuny-ci.yml` in every
product repository. Hydra stays advisory. Fork pull requests use a read-only
token, no secrets and no self-hosted runners.
