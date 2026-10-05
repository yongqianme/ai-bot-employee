# Memory and State Policy

- **Working context:** prospect input and generated draft for the current process only.
- **Task state:** stored in the generated JSON ledger entry under `demo/output/`.
- **Operational memory:** none is required for the offline demo.
- **Policy/configuration:** `employee-contract.yaml`, `authority-matrix.yaml`, and `tool-map.yaml` are controlled configuration.
- **Secrets:** never stored in the ledger, YAML files, prompt text, or model memory.

A production deployment may add a durable database, queue, or runtime-native state store, but should preserve these separations.
