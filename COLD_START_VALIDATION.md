# Isolated deployment validation

Stage 22 verified fresh tracked-source extraction, newly generated development certificates/keys, twelve real services, five fresh volumes, official plan execution, TestNG/Extent, 115 MinIO read-backs, GitHub artifact upload and owned cleanup. It reused Docker images/dependency caches. Do not describe that run as an empty-cache deployment.

An empty-cache full deployment must use a separate disposable Docker Desktop machine/VM with WSL integration, or a separately provisioned compatible Docker daemon. The current managed manifests rely on Docker Desktop's `host.docker.internal` topology. A new checkout on the existing daemon is insufficient to prove empty image caches, and deleting this development machine's images/volumes would destroy retained state. Native Linux hosted networking has not been validated for these manifests.

On that isolated machine, record OS/engine/resources, ensure the Docker image list is initially empty, clone the approved immutable source revision, create a new virtual environment, use new Maven and pip caches, and execute:

```bash
git clone https://github.com/SantoshReddy0603/mosip-inji-conformance.git harness
cd harness
git checkout --detach <approved-commit-sha>
python3 -m venv /absolute/new/venv
source /absolute/new/venv/bin/activate
python -m pip install --no-cache-dir -r runner/requirements-ci.txt
python runner/setup.py
export MAVEN_OPTS="-Dmaven.repo.local=/absolute/new/maven-cache"
python runner/build_native_certify.py --positive-serial
docker compose --env-file docker/.env -f docker/docker-compose.yml build conformance-server
docker compose --env-file docker/.env -f docker/storage.compose.yml build minio
python -m pytest tests -q --junitxml=/absolute/evidence/harness.xml
bash run-clean-conformance.sh --combined --parallel 2 --reports-dir /absolute/private/reports
```

The isolated-stack launcher retrieves the remaining service images. Record the actual command exit: the conformance command is expected to return 1 if the six official REVIEWs persist. Verify component gates, native/combined XML and HTML, official exports, MinIO read-back hashes and cleanup ownership. Export only restricted CI evidence with `runner/ci_artifacts.py`; retain raw credentials, exports and screenshots privately. Run `runner/verify_storage.py` against the actual deployment environment before storage teardown if doing an additional independent read-back. Archive logs and provenance before disposing of the isolated environment.

No fresh-machine PASS is implied by these commands. The Stage 23 validation report records which portions were actually executed and any remaining environment limitation. No existing Docker image cache or historical volume may be pruned to simulate this test.
