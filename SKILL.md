---
name: veil
description: Integrate Veil (veil.rip) into an app, bot or service. Use for Veil card and linked-account lookups, signed-message checks, transparency proofs and log format 2 verification, badges and widgets, API keys and quotas, or interpreting Veil endpoint responses and errors.
---

# Veil integration

Veil is the public directory of cryptographic identities. It resolves accounts people know (Discord, GitHub, email, domain and Fediverse) to a permanent card and its signing keys, so you can find someone's key from an account you already know. A stolen account cannot produce the owner's signature. Every card change enters a public, witnessed transparency log.

Use `https://veil.rip` for the directory, `https://log.veil.rip` for the log and [the documentation](https://veil.rip/docs) for contracts. Public reads and message verification work anonymously. Optional API keys give server and local clients a shared owner allowance.

## Start with the current contract

The [live catalogue](https://veil.rip/v1/integrations) contains 71 endpoints and 10 guides (revision `97321eb55810004b`). `GET /v1/integrations/{id}` returns a localised entry and the catalogue revision. Its ID is also the documentation slug. Read the entry before implementing a call, and follow its access mode, parameters, response types and verification requirements.

- `responses` gives HTTP status, content type, field names, types, descriptions and selected examples.
- `responseObjects` describes nested types, and `responseHeaders` describes headers.
- `errorDetails` gives HTTP status, stable code, explanation, recovery action and scope. `response` and `errors` remain available for existing consumers.
- Read [references/responses-and-errors.md](references/responses-and-errors.md) when interpreting fields, handling errors, caching responses or choosing retries.

Since 28 October 2026 the directory writes to the log `log.veil.rip/staging-1` in **format 2**, and `GET /v1/log` answers `"format": 2` with `staffOrg`, the token of the Veil organisation. Cards in format 2 carry signed labels, a verifiable index and signed staff statements. Read [references/format-2.md](references/format-2.md) before you parse `current`, `authority`, `state` or `index`, or verify a card in your own code. The cards were recreated on this log: today they are card 1 (a person) and card 2 (the Veil organisation), with new IDs and fingerprints.

## Bundled client

`scripts/veil.py` uses Python's standard library. Put client options before the command.

```bash
python scripts/veil.py lookup --key 73ad6159583a43f8ad230a215b758db680efcd3ce32ab8e83c622eeca883e68a
python scripts/veil.py card 1
python scripts/veil.py org 2
python scripts/veil.py authority 1
python scripts/veil.py members 2
python scripts/veil.py verify --block-file signed.txt
python scripts/veil.py doc verify-message
python scripts/veil.py doc errors --lang it
python scripts/veil.py --include-headers card 1
python scripts/veil.py --api-key-env VEIL_API_KEY quota
python scripts/veil.py --output badge.svg get /o/2/badge.svg
python scripts/veil.py --dry-run summary 1
```

The named environment variable supplies an optional bearer secret, and request previews redact it. Keep keys in server secret configuration. The client never signs management requests or handles device private keys. Read-only transient failures get at most one retry. If the required wait exceeds 30 seconds, the client returns the response without retrying early. `--if-none-match` sends a card's `ETag` back, and a `304` leaves any `--output` file untouched.

## Choose a call

| Job | Call |
|---|---|
| Find a card by one exact account, key or fingerprint | `GET /v1/lookup` with exactly one lookup parameter |
| Resolve an alias | `GET /v1/aliases/{kind}/{alias}`, or the card at `/u/{alias}.json` and `/o/{alias}.json` |
| Read a full card and its proof | `GET /u/{card}.json` or `/o/{card}.json`, revalidated with `If-None-Match` |
| Display current name, image or badges | `GET /v1/identities/{n}/summary` |
| Verify a signed message | `POST /v1/verify` with a block or raw signature fields |
| Read a key's owner or validity | `GET /v1/keys/{key}` or `/active-at?t=<Unix seconds>` |
| Learn the log, its format and the Veil organisation | `GET /v1/log` (`format`, `staffOrg`) |
| Verify a card in your own code | The card JSON, then [references/format-2.md](references/format-2.md) |
| Page authority versions or staff statements (format 2) | `GET /v1/identities/{n}/authority`, or follow `index.statementsNext` |
| Poll for changes | `GET /v1/identities/{n}/versions?latest=true&limit=1`, `/events?after=<id>`, or the card's `ETag` |
| Embed a card | `/{kind}/{n}/badge.svg`, `/{kind}/{n}/embed` or `/embed.js`, with the card number |
| Inspect an integration's allowance | `GET /v1/rate-limit` with its bearer key |
| Create or manage integration keys | Device-signed `/v1/developer/accounts/{n}` routes, see the [API-key reference](references/api-keys.md) |

[references/endpoints.md](references/endpoints.md) maps all 71 endpoint IDs to paths and access requirements. Read its relevant group for calls outside this table.

## Resolve and verify

Use stable platform IDs. Discord takes a 17 to 20 digit user ID, and GitHub takes a numeric account ID, never a login. Supply exactly one lookup parameter. Display names are not unique. Store the permanent card number `n`, because aliases can change or be reassigned. `/v1/lookup` has no alias parameter: the `@alias` form belongs to the search box on Veil's pages, and the API resolves aliases through `/v1/aliases/{kind}/{alias}`. The Veil organisation's alias `veil` is reserved for card 2 but not set today, so use `/o/2`.

For a message, use the overall `valid` verdict. HTTP 200 with `valid: false` is a completed negative check. `signatureOk` can be true after a key was revoked. Read `reason`, `keyState` and any requested account ownership result. When checking a bot's sender, supply raw `key`, `message`, `signature`, `platform` and `subject` so ownership is checked too. For `at`, use a publication time in Unix seconds that you trust independently. A timestamp written by the signer proves nothing.

`POST /v1/verify` sends the message to Veil. [Browser verification](https://veil.rip/verify) keeps data after `#` in the browser. Ask for a network verification only within the user's intended sharing of that message.

A summary carries no proof. A full card can return 200 with `proof: null`, and in format 2 also with `index: null` or `index.statements: null`. Leave such a card unverified and retry later. `/v1/log` and `/v1/verify` report the server's checks. Independent verification starts from a log key and witness policy you pinned yourself and checks the signed labels, the index proof, the authority versions, the state roots and the chain of staff statements. Only accepted organisation memberships count as authority. A `304` on the card means its bytes did not change, but freshness still has to be checked again.

## Access and limits

Anonymous browser requests use public CORS and omit credentials. CORS opens public reads and `POST /v1/verify`. It does not allow `Authorization` or device-signing headers, and it leaves out `GET /v1/identities/{n}/statements`. Keep bearer keys in server or local clients.

An API owner normally shares 600 requests per minute across all keys. Verification also uses a shared 120-per-minute bucket. Both refill continuously. Optional key caps and UTC-day caps can further constrain access. Rotation does not reset the owner's allowance. Anonymous traffic keeps its existing IP limits, and signed writes keep their own limits. Read [references/api-keys.md](references/api-keys.md) for scopes, expiry, custom limits, status headers and private receipts.

Errors use a stable `error.code` and a mutable English `error.message`. Use the endpoint's `errorDetails` and [the error guide](https://veil.rip/docs/errors) for the next action. Respect `Retry-After`, and check the current state before repeating a signed operation. A service failure is never a successful verification.

## Signed operations

Creating or changing a card and managing API keys require an authorised device signature. A bearer key grants public reads and verification only. Read [references/signed-requests.md](references/signed-requests.md) when the user requests a signed operation.

On a format 2 log a card version is `{label, body, signature, pictureData?}`: the label carries the operations that change who can sign, and the body carries the rest. A format 1 `record` gets `400 wrong_format`. Pictures are named by hash (`{type, sha256, size}`, PNG, GIF or SVG, up to 2 MiB) and their bytes travel beside the version.

Prepare the unsigned request and signing bytes, then let the owner sign on their own device. Never ask them to paste, transmit or store a device private key in the integration. A key-management action records a private receipt, and publishing an identity version requires witnessed inclusion in the public log. After a timeout, check the relevant state before signing another request.
