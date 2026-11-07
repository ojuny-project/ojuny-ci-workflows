# Acceptance playbook

Date: 2026-11-07

This playbook defines the acceptance flows, the VM requirements and the
artifacts. The flows are implemented as heavy-tier jobs and run when KVM and ISO
artifacts are available.

## Flows

| Flow | Job | Install path | Manual |
| --- | --- | --- | --- |
| Unattended install | `acceptance.install` | Offline unattended ISO | no |
| Template setup install | `acceptance.setup` | Template setup on a minimal NixOS VM | no |
| Session | `acceptance.session` | Installed target | no |
| Rollback | `acceptance.rollback` | Installed target with two generations | no |
| Chained install to session | `acceptance.chained` | Installed target | no |
| Attended Calamares | manual | ISO | yes |

## VM requirements

- KVM is required. Without it the job is skipped with exit code 4.
- The session uses a graphical VM with `virtualisation.graphics = true`.
- The Wayland session uses `virtio-vga-gl`.
- Resolution and font size are pinned for OCR.
- The install job may run headless.

## Session assertions

- The display manager appears.
- The fixture user logs in.
- The bar appears.
- The launcher opens and finds a known application.
- The Ojuny menu opens.
- The settings GUI opens and shows a known page.
- One notification appears.
- No failed systemd units above the agreed threshold.
- The session shuts down cleanly.

## OCR

- The inventory lives in `acceptance-inventory.json`.
- Draft flows have no strings yet. Active flows must have at least one string.
- Each assertion is repeated five times across separate session runs.
- 1/5 failure is a flake.
- 2/5 is a borderline flake.
- 3/5 is an inconsistent issue.
- 4/5 is a borderline inconsistent issue.
- 5/5 is a deterministic problem.
- Promotion to required needs zero failures, or an agreed lower rate after
  review.

## Artifacts

- serial log
- screenshots
- OCR text
- journal and failed unit list
- generation list
- install report and first-boot log

## Manual boundary

Attended Calamares, real hardware sessions, vendor hardware reports, the
physical install-time track and the unreleased-marker review stay manual.
