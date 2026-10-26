# Signed requests (writes)

Source: https://veil.rip/docs/signed-requests plus the per-endpoint pages. Read this only when the user wants to change a card. Reads and `POST /v1/verify` never need it.

## Ground rules

- A write is signed by an **active authorised device key** that belongs to the card owner. Never ask the user to paste a private key, never generate or store one on their behalf, and never send one to Veil. Prepare the unsigned record and request bytes, explain what must be signed, and let the owner sign on their own device.
- Signed writes are for local or server clients. CORS does not open them to other websites, so do not build them into browser pages.
- A publication is ready only after its commitment appears in a witnessed checkpoint. If a request times out, read the card's current versions before resending.

## Request signature

Headers: `X-Public-Key`, `X-Signature`. Ed25519 keys and signatures are hex. Composite keys and signatures are base64 and add `X-Signature-Alg: mldsa65-ed25519`.

Signed bytes for a POST (the exact UTF-8 JSON body that is sent):

```
veil-rubrica:request:v1
POST /v1/identities/1/versions
<exact UTF-8 JSON body>
```

For a signed GET, send `X-Nonce` and `X-Timestamp` and sign the exact path with its query:

```
veil-rubrica:request:v1
GET /v1/device-requests/PAIRING_CODE
<nonce>
<Unix milliseconds>
```

The JSON body of a POST carries `nonce` (fresh, single use, 16-128 chars of letters, digits, `_`, `-`) and `timestamp` (Unix **milliseconds**, within 2 minutes of the server clock). The request signature covers method, exact path and exact body, so sign the bytes you actually send.

Limits: 10 signed writes per minute per key, 30 writes per minute per IP, separate budgets for account-linking steps.

## Record (the thing the card is made of)

The record has its **own** signature, separate from the request signature, over the identity-version prefix plus canonical JSON.

- `v`: 1. `identity`: base64url of a fresh 16-byte token for version 1, unchanged afterwards. `n`: starts at 1, +1 each version. `prev`: null for version 1, else the previous commitment (standard base64).
- `name`: display name. `time`: Unix **seconds**, within 5 minutes of the server clock. `type`: `person` or `organization` (omitted means person). `alias`: optional, lowercase, check `GET /v1/aliases/{kind}/{alias}`.
- `keys`: full key history. Each item: `key, alg, device, role, since, revoked`. `role` is `device` or `recovery`. `since`/`revoked` are version numbers; `revoked` is null while active.
- `links`: full account history. Each item: `platform, subject, display, since, removed` and its `grant` when added. Removed entries stay in later records. Get the grant from the linking APIs before publishing.
- People may carry `orgs` (accepted memberships); organisations carry `members` with roles. Keep history and acceptance grants. An invitation alone is not membership.
- `logo` (optional): `type` (`image/svg+xml`, `image/png`, `image/gif`) and `data` (padded standard base64, max 2 MiB decoded). Validate first with `POST /v1/logo-previews`.

Canonical JSON: object keys sorted by UTF-16 code units, array order preserved, no whitespace outside strings, only safe-range integers, UTF-8 strings, booleans, null. Do not normalise or trim signed text. The outer request body need not be canonical.

## Typical flows

**New card:** `POST /v1/salt-tickets` (public-write) -> device draws its salt half -> build version-1 record -> owner signs record and request -> `POST /v1/identities` with `record, signature, nonce, timestamp, clientSalt, saltTicket`. Success is `201` with `n, id, url, token, version, commitment, logIndex, publishedAt, checkpoint`.

**Link an account:** `POST /v1/links/start` `{identity, platform, subject?, method?}` -> `201 {state, method, expiresAt, challenge}` (keep `state` private; OAuth platforms redirect through `GET /v1/links/callback/{platform}`) -> `POST /v1/links/{state}/complete` with the same key -> take the returned grant -> publish the next version via `POST /v1/identities/{n}/versions`. Starting or completing a proof does not itself add the account.

**Organisation changes:** `POST /v1/organizations` and `/v1/organizations/{n}/versions`; role rules apply, only accepted owners/admins authorise changes. Invitees answer with `POST /v1/orgs/{n}/invites/{id}/accept|decline`.

**Pair a new device:** new device `POST /v1/device-requests` -> existing device reads `GET /v1/device-requests/{code}` (signed GET) -> publishes a version adding the key.

**Erasure:** `POST /v1/identities/{n}/erase` (24-hour cancellation window), `POST /v1/identities/{n}/erase/cancel`.

## Write errors

`422 invalid_record`, `401 missing_signature`, `403 signer_not_authorised`, `409 version_conflict` (re-read versions, rebuild, retry), `503 log_unavailable`. For other statuses see the table in SKILL.md.

For exact per-endpoint bodies run `python scripts/veil.py doc <id>` (for example `publish-person`, `complete-link`).
