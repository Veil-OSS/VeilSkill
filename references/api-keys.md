# Integration API keys

Sources: [API-key guide](https://veil.rip/docs/api-keys), [quota contract](https://veil.rip/docs/rate-limit) and the per-endpoint JSON entries. Public reads and verification remain available without a key.

## Obtain and store a key

Open [API keys](https://veil.rip/developers), available from the active profile menu. A person manages their own card, and an organisation requires an accepted owner. An active device signs management requests.

Choose a label of 1 to 60 characters, `read` and/or `verify` scope, and expiry from 1 to 365 days (default 90). Each owner can have 20 unexpired, unrevoked keys, including suspended keys. Creation returns HTTP 201 with `key` metadata and `secret`. The secret appears once, and the server stores only its SHA-256 hash.

Keep the bearer secret in server configuration. Never put it in a URL, repository, frontend bundle or shared output. A device's private signing key stays on that device. To use the bundled client, supply only the environment variable's name:

```bash
python scripts/veil.py --api-key-env VEIL_API_KEY platforms
python scripts/veil.py --api-key-env VEIL_API_KEY --include-headers quota
```

The client does not create keys or execute signed management calls. `--dry-run` redacts bearer credentials. A key must be sent to the configured API origin over HTTPS. Loopback HTTP is available for local development. Authenticated redirects to another origin are refused.

## Shared limits

| Allowance | Default | Behaviour |
|---|---|---|
| Owner requests | 600 per minute | One bucket shared by every key of a permanent card |
| Owner verification | 120 per minute | Additional bucket. Verification spends both |
| Per-key cap | Unset | Additional constraint that never adds to the owner total |
| Owner UTC-day cap | Unset | Additional constraint resetting at midnight UTC |
| Outer API-key guard | 3000 per minute per IP | Still applies with owner quotas. Authentication concurrency is bounded |

Minute buckets refill continuously and can admit a burst up to the available balance. Counters survive restarts. Creating or rotating keys never resets the owner's allowance. Staff can set custom owner limits and additional key/daily caps according to role. API keys do not raise signed-write, card-creation, pairing or account-linking limits.

Admitted requests count even when an endpoint later returns an error. Quota rejections are counted separately.

## Read current usage

`GET /v1/rate-limit` requires an active bearer key and does not spend its primary allowance. The outer IP guard still applies. Its response has:

| Field | Meaning |
|---|---|
| `owner` | Permanent owner card number |
| `key` | Key metadata without secret or hash |
| `quota.requests` | Shared request bucket |
| `quota.verification` | Shared verification bucket |
| `quota.daily` | UTC-day cap, or null |
| `quota.key` | Additional key cap, or null |
| `rate`, `resource` | Bucket described by the response headers |
| `retryAfter` | Seconds until admission is possible. It can be positive with HTTP 200 on this status call |

Each bucket has `limit`, `remaining` and `resetAt`. The reset time is Unix seconds when the bucket would be full without more requests, or the next UTC midnight for a daily cap. It is not a fixed minute boundary.

Authenticated public requests also return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` and `X-RateLimit-Resource`. The resource is `requests`, `verification`, `key` or `daily`. A quota 429 includes `Retry-After` for the next admissible request. Responses carrying API-key data use `Cache-Control: no-store`.

Public browser CORS exposes `Date`, `ETag` and `Retry-After`. It does not open bearer credentials or these additional quota headers to frontend code.

## Owner management contracts

All of these require a device signature, not the bearer secret. Read their live contract before preparing a request.

| ID | Method and path | Response |
|---|---|---|
| `developer-account` | `GET /v1/developer/accounts/{n}` | Limits, quota, current usage, latest 31 days, key page, private receipts and permissions |
| `developer-keys` | `GET /v1/developer/accounts/{n}/keys` | `owner`, `keys`, `next` |
| `create-api-key` | `POST /v1/developer/accounts/{n}/keys` | 201 with `key` and one-time `secret` |
| `revoke-api-key` | `DELETE /v1/developer/accounts/{n}/keys/{id}` | Revoked key metadata |
| `api-key-audit` | `GET /v1/developer/accounts/{n}/audit` | `owner`, `events`, `next` |

Key and audit pages take `before` and `limit` (1 to 100, default 50). Continue with returned `next` as `before` until null. The overview initially has at most 50 keys and 20 audit events. Management writes accept at most 8 KiB and reject unknown fields. `nonce` and `timestamp` remain common signing fields.

Receipts contain actor, action, reason, details and the exact signed method/path/body/public key/algorithm/signature. They do not contain the bearer secret and are not published in the identity log. Usage is aggregate, without message text, lookup queries or IP addresses.

## Rotation and restrictions

Create a replacement, update the integration and revoke the old key. Revocation is permanent. Revoking a device does not revoke the API keys it issued. Inspect receipts and revoke affected integrations after a device compromise.

| HTTP | Code | Action |
|---|---|---|
| 401 | `invalid_api_key` | Replace a malformed, unknown, expired or revoked credential |
| 403 | `api_key_scope` | Use the required scope or the endpoint's device-signing flow |
| 403 | `api_key_suspended` | Ask authorised staff to restore the key |
| 403 | `developer_suspended` | Resolve the owner-account restriction. Another key cannot bypass it |
| 409 | `api_key_limit` | Revoke an unused key before creating another |
| 429 | `rate_limited` | Respect `Retry-After` and coordinate workers sharing the allowance |

Invalid credentials never fall back automatically to anonymous access. Remove `Authorization` explicitly when anonymous access is intended. Staff may inspect integrations, suspend or restore keys, revoke them and set custom limits according to role. Private staff administration routes are outside the public integration catalogue.
