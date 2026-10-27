---
name: veil
description: Integrate Veil (veil.rip) into an app, bot or service. Use for Veil card and linked-account lookups, signed-message checks, transparency proofs, badges and widgets, API keys and quotas, or interpreting Veil endpoint responses and errors.
---

# Veil integration

Veil resolves accounts people know (Discord, GitHub, email, domain and Fediverse) to a permanent card and its signing keys. A stolen account cannot produce the owner's signature. Every card change enters a public, witnessed transparency log.

Use `https://veil.rip` for the directory, `https://log.veil.rip` for the log and [the documentation](https://veil.rip/docs) for contracts. Public reads and message verification work anonymously. Optional API keys give server and local clients a shared owner allowance.

## Start with the current contract

The [live catalogue](https://veil.rip/v1/integrations) currently contains 65 endpoints and 10 guides. `GET /v1/integrations/{id}` returns a localised entry and catalogue revision. Its ID is also the documentation slug. Read the entry before implementing a call; follow its access mode, parameters, response types and verification requirements.

- `responses` gives HTTP status, content type, field names, types, descriptions and selected examples.
- `responseObjects` describes nested types; `responseHeaders` describes headers.
- `errorDetails` gives HTTP status, stable code, explanation, recovery action and scope. `response` and `errors` remain available for existing consumers.
- Read [references/responses-and-errors.md](references/responses-and-errors.md) when interpreting fields, handling errors, caching responses or choosing retries.

## Bundled client

`scripts/veil.py` uses Python's standard library. Put client options before the command.

```bash
python scripts/veil.py lookup --github 109546049
python scripts/veil.py card 1
python scripts/veil.py verify --block-file signed.txt
python scripts/veil.py doc verify-message
python scripts/veil.py doc errors --lang it
python scripts/veil.py --include-headers platforms
python scripts/veil.py --api-key-env VEIL_API_KEY quota
python scripts/veil.py --output badge.svg get /o/veil/badge.svg
python scripts/veil.py --dry-run lookup --github 109546049
```

The named environment variable supplies an optional bearer secret; request previews redact it. Keep keys in server secret configuration. The client never signs management requests or handles device private keys. Read-only transient failures get at most one retry. If the required wait exceeds 30 seconds, the client returns the response without retrying early.

## Choose a call

| Job | Call |
|---|---|
| Find a card by one exact account, key or fingerprint | `GET /v1/lookup` with exactly one lookup parameter |
| Read a full card and its proof | `GET /u/{card}.json` or `/o/{card}.json` |
| Display current name, image or badges | `GET /v1/identities/{n}/summary` |
| Verify a signed message | `POST /v1/verify` with a block or raw signature fields |
| Read a key's owner or validity | `GET /v1/keys/{key}` or `/active-at?t=<Unix seconds>` |
| Poll for changes | `GET /v1/identities/{n}/versions?latest=true&limit=1` or `/events?after=<id>` |
| Embed a card | `/{kind}/{card}/badge.svg`, `/{kind}/{card}/embed` or `/embed.js` |
| Inspect an integration's allowance | `GET /v1/rate-limit` with its bearer key |
| Create or manage integration keys | Device-signed `/v1/developer/accounts/{n}` routes; [API-key reference](references/api-keys.md) |

[references/endpoints.md](references/endpoints.md) maps all 65 endpoint IDs to paths and access requirements. Read its relevant group for calls outside this table.

## Resolve and verify

Use stable platform IDs. Discord takes a 17 to 20-digit user ID; GitHub takes a numeric account ID, not a login. Supply exactly one lookup parameter. Display names are not unique. Store permanent card number `n`; aliases can change or be reassigned.

For a message, use the overall `valid` verdict. HTTP 200 with `valid: false` is a completed negative check. `signatureOk` can be true after a key was revoked. Read `reason`, `keyState` and any requested account ownership result. When checking a bot's sender, supply raw `key`, `message`, `signature`, `platform` and `subject` so ownership is checked too. Use a publication time you independently trust for `at`, in Unix seconds; a timestamp written by the signer proves nothing.

`POST /v1/verify` sends the message to Veil. [Browser verification](https://veil.rip/verify) keeps data after `#` in the browser. Ask for a network verification only within the user's intended sharing of that message.

A summary carries no proof. A full card can return 200 with `proof: null`; leave it unverified and retry later. Independent verification requires the exact signed records, commitments, version chain, inclusion proof, expected log key and witness policy. `/v1/log` and `/v1/verify` report the server's checks. Only accepted organisation memberships count as authority.

## Access and limits

Anonymous browser requests use public CORS and omit credentials. CORS opens public reads and `POST /v1/verify`; it does not allow `Authorization` or device-signing headers. Keep bearer keys in server or local clients.

An API owner normally shares 600 requests per minute across all keys. Verification also uses a shared 120-per-minute bucket. Both refill continuously. Optional key caps and UTC-day caps can further constrain access. Rotation does not reset the owner's allowance. Anonymous traffic retains its existing IP limits, and signed writes retain their own limits. Read [references/api-keys.md](references/api-keys.md) for scopes, expiry, custom limits, status headers and private receipts.

Errors use a stable `error.code` and a mutable English `error.message`. Use the endpoint's `errorDetails` and [the error guide](https://veil.rip/docs/errors) for the next action. Respect `Retry-After`; check the current state before repeating a signed operation. A service failure is never a successful verification.

## Signed operations

Creating or changing a card and managing API keys require an authorised device signature. A bearer key grants public reads and/or verification only. Read [references/signed-requests.md](references/signed-requests.md) when the user requests a signed operation.

Prepare the unsigned request and signing bytes, then let the owner sign on their own device. Never ask them to paste, transmit or store a device private key in the integration. A key-management action records a private receipt; publishing an identity version requires witnessed inclusion in the public log. Check the relevant state after a timeout before signing another request.
