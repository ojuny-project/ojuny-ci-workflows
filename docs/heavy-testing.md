# Heavy testing backlog

Date: 2026-11-07

This file records what is implemented but cannot be verified without KVM, ISO
artifacts, physical hardware, the plan 02 CI server or GitHub repository
administration.

## Required environment

- Nix with flakes and a working binary cache.
- KVM access for graphical and non-graphical VM tests.
- ISO artifacts from plan 03.
- The plan 02 CI server for the aggregate `hydraJobs` and advisory status.
- Physical hardware for the physical install-time track and vendor reports.
- GitHub repository administration for branch protection.

## Backlog

1. Template fixture system build.
   Run: `nix build .#checks.x86_64-linux.fixture-system-build`.
   Record: toplevel store path and failed units.
   Pass: the fixture host evaluates and builds for x86_64-linux.

2. VM install baseline.
   Run: `nix run .#vm-install-baseline` with the unattended offline ISO and the
   published VM spec.
   Record: `result.json`, `result.md`, `result.html` and the VM spec identifier.
   Pass: the install finishes, the report is generated and the baseline is
   stored.

3. Acceptance install.
   Run: `acceptance.install`.
   Record: serial log, disk image, exit code.
   Pass: the unattended offline ISO installs and powers off.

4. Acceptance session.
   Run: `acceptance.session`.
   Record: screenshots, OCR text and journal.
   Pass: login, bar, launcher, Ojuny menu, settings page, notification and clean
   shutdown.

5. Acceptance rollback.
   Run: `acceptance.rollback`.
   Record: generation list, screenshots and journal.
   Pass: the previous generation boots and the session starts.

6. OCR stability.
   Run: `ocr-stability` five times.
   Record: failure count and the 1/5, 3/5 and 5/5 classification.
   Pass: zero failures promotes the assertions to required. One in five stays
   advisory. Three in five is an inconsistent issue. Five in five is a
   deterministic problem.

7. Real install report.
   Run: `apps.install-report <directory>` on a real install.
   Record: `result.json`, `result.md` and `result.html`.
   Pass: the timings and phases match the install log and the first-boot log.

8. Physical install-time track.
   Run: three runs per selected ISO on the documented device.
   Record: the configuration fingerprint, median and spread.
   Pass: a published result, private or by pull request.

9. Heavy ISO checks.
   Run: `iso-build`, `iso-size`, `iso-boot-smoke`, `offline-install-vm`.
   Record: ISO hashes, sizes and boot logs.
   Pass: every variant builds, is under 8,000,000,000 bytes and boots.

10. Reproducibility audit.
    Run: two builds on separate stores or machines.
    Record: `nix hash path`, file SHA-256 and the rebuild command.
    Pass: the hashes match, or the mismatch is attributed to the Ojuny layer.

11. aarch64 checks.
    Run: the generic `aarch64-linux` evaluation and build matrix.
    Record: failing attributes and the reason.
    Pass: the supported attributes build or are explicitly out of scope.

12. Hydra aggregate.
    Run: the plan 02 jobset generator against the per-repository `hydraJobs`.
    Record: evaluated jobs, build results and the advisory status.
    Pass: the aggregate evaluates and one heavy job runs.

13. Branch protection.
    Run: enable required `fast` and `nix` checks in every repository.
    Record: the required-check list.
    Pass: a failing fast check blocks a test pull request, and Hydra stays
    advisory.

## Current status

- Items 1 to 13 are implemented as code, manifests or playbooks where possible.
- No item has been executed.
- The install-report app and the collector script are unit-tested with synthetic
  fixtures.
- The installer call to the collector and the first-boot log are implemented but
  untested.
- The template fixture host and `checks.fixture-system-build` are implemented
  but untested.
- `ojuny-installer/tests/acceptance.nix` and `tests/install-vm.nix` are
  parseable skeletons. They are not wired into `checks` or `hydraJobs`.
- The runner and schema checks are unit-tested.
- No `nix build`, `nix flake check` or `/nix` access has been run in this
  environment.
