# Optional approved self-hosted runner

Managed CI defaults to disposable hosted Linux. Select this optional dedicated runner only with INJI_USE_SELF_HOSTED_RUNNER=true. It requires a Linux Docker engine. The verified deployment used Ubuntu on WSL, Java 21, Maven 3.8.7 and an official ephemeral GitHub runner. That runner unregistered after its job. No always-on service is assumed or installed. Native Linux Docker networking and a completely uncached deployment remain separate validation targets.

## Preflight and one approved job

Use an extracted official GitHub runner in the Linux filesystem, installed using the repository's Settings > Actions > Runners > New self-hosted runner > Linux instructions. Verify the download against the official release checksum. Run from the harness root in the configured Python environment:

Set INJI_GITHUB_REPOSITORY to your actual HTTPS repository URL before using the tool. An explicit --repository takes precedence. The tool rejects missing configuration, credentials in URLs, and unexpected hosts; registration remains bound to that repository.

```bash
export INJI_GITHUB_REPOSITORY=https://github.com/your-owner/your-repository
python runner/local_runner.py status --runner-dir /absolute/linux/runner
python runner/local_runner.py preflight --runner-dir /absolute/linux/runner
```

Preflight checks Java 21, javac, Maven 3.8.7, Git, OpenSSL, Docker Compose and Linux Docker connectivity; Linux memory and disk; managed service ports; TLS connectivity to dependency endpoints; the actual runner Node24 connection using `--no-network-family-autoselection --dns-result-order=ipv4first`; and repository-bound ephemeral registration. Exit 2 means not ready, including an unregistered runner. Repository access is finally proven by a successful authenticated runner connection/job, not by local registration metadata. TLS verification remains enabled. The resource floor is a preflight threshold, not proof of peak build capacity; 8 GiB or more is recommended.

For an approved run, obtain a short-lived registration token from that same repository's GitHub settings. Put it in an owner-only regular file on the Linux filesystem, outside this repository (`chmod 600`). Never paste it in chat, commit it, or put it in shell history. Then:

```bash
python runner/local_runner.py start --owner-approved \
  --runner-dir /absolute/linux/runner \
  --registration-token-file /absolute/private/registration-token
```

The tool deletes the token file after successful registration, serializes registration/start with a filesystem lock, refuses another repository or persistent registration, detects a running listener, and starts one foreground job. If the runner is already validly registered, omit the token-file argument. Failed registration retains the private file for recovery; remove it securely after diagnosis. Console output excludes registration output and credentials. No permanent GitHub credential is introduced. Runner auto-update is retained. Only `inji-conformance` trusted jobs should be dispatched while it is online.

Confirm `Listening for Jobs` and repository runner visibility before approving/publishing a release. Ctrl+C or SIGTERM stops the owned listener process group. The tool never deletes Docker resources. A successfully completed ephemeral job unregisters automatically. Check status and GitHub settings afterward; an interrupted listener may retain registration and needs explicit recovery.

## Supervision and recovery

For one approved unattended job, an operator may supervise the same foreground command with a transient user systemd unit on WSL with systemd enabled:

```bash
systemd-run --user --unit=inji-approved-job --collect \
  /absolute/venv/bin/python /absolute/harness/runner/local_runner.py start \
  --owner-approved --runner-dir /absolute/linux/runner \
  --registration-token-file /absolute/private/registration-token
journalctl --user -u inji-approved-job -f
systemctl --user stop inji-approved-job
```

This is a documented option, not an installed service. It requires the selected Linux host and Docker engine to remain running. It deliberately does not auto-register again or silently turn one approval into indefinite access. Provision and approve each subsequent runner job. A reusable service or automatic token provisioning is a separate infrastructure decision. An owner approval flag is an operator attestation; it is not GitHub-enforced reviewer protection.

If interrupted before completion, inspect GitHub runner settings and the local status. Remove a stale runner through GitHub's supported removal procedure, using its fresh removal token locally, before clearing local registration. Do not delete `.runner`/`.credentials` merely to bypass a conflicting registration. If managed services survive cancellation, locate that job's `INJI_CLEAN_ROOT` and ownership state, and run its `runner/isolated_stack.py down --project <exact-owned-project>`. Never prune the shared Docker daemon or historical volumes. The workflow's existing trap and always-run cleanup handle normal success and failure.

## Approval boundary

The private repository's current plan does not expose environment required-reviewer enforcement. Existing `main` and `v*` environment restrictions, event/SHA/ancestry checks and read-only workflow permissions remain in place. Explicit owner approval is required for privileged live execution, each merge, and release publication. Restrict repository write access and do not put PR jobs on this runner. A label or environment alone does not isolate a self-hosted machine from all writable repository workflows. Do not claim that an operator procedure supplies GitHub-enforced reviewer protection.

References: [GitHub runner services](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/configure-the-application), [ephemeral runners](https://docs.github.com/en/actions/reference/runners/self-hosted-runners), [environment limitations](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).
