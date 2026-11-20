# Deploying Kavach (District D8)

The core (detection, decision, audit, console) is **stdlib-only** — no external
network calls at build or run time — so it deploys the same way from SaaS to a
fully air-gapped bank. The optional MuRIL NER is the only component that needs
network (once, to fetch model weights) or a pre-seeded model cache.

## Topologies

| Mode | How | For |
|---|---|---|
| **SaaS / dev** | `python -m kavach.console.server` | quick trials, non-regulated |
| **Container / VPC** | `docker build . && docker run -p 8765:8765 kavach` | runs inside the customer's cloud |
| **On-prem / air-gap** | same image, no egress; config + audit on a mounted volume | banks, health — RBI localisation |

## Run

```bash
# local
python -m kavach.console.server            # http://localhost:8765

# docker
docker build -t kavach:latest .
docker run --rm -p 8765:8765 kavach:latest

# docker compose (mounts config + persists audit)
docker compose up --build
```

## Configuration (no code changes)

Point `KAVACH_CONFIG` at a JSON file to set the trust registry, policy and the
audit log path. See `deploy/kavach.config.json`:

```json
{
  "trust": { "crm_external_api": "untrusted", "core_banking": "trusted" },
  "policy": { "version": "onprem-v1", "escalate_below": 0.6 },
  "audit_path": "/data/audit.jsonl"
}
```

Env vars: `KAVACH_HOST` (default 127.0.0.1; set 0.0.0.0 in containers),
`KAVACH_PORT` (8765), `KAVACH_CONFIG` (path above).

Endpoints: `GET /health`, `GET /api/meta`, `POST /api/scan`, `GET /api/audit`,
`POST /api/trust`.

## Air-gap notes

- The core needs **no network**. Do not install the `[ner]` extra, or pre-seed
  the model cache (`HF_HOME`) into the image so no runtime download happens.
- The audit log is append-only and hash-chained; mount it on durable storage.

## Production hardening (not yet done — honest status)

The bundled server is the stdlib `ThreadingHTTPServer` — fine for dev/demo and
VPC-internal use. For production, front it with a real ASGI server + reverse
proxy (mTLS, authn/z on the admin console), move the token vault to KMS/HSM
(District D4), and run multiple stateless replicas behind a load balancer.
