---
name: veil
description: Integrate Veil (veil.pub) into an app, bot or service. Use for Veil card and linked-account lookups by ID or by name, signed-message and signed-file checks, public keys from elsewhere (SSH, OpenPGP, minisign), account alerts and signed statements, Sign in with Veil (OpenID Connect), transparency proofs and log format 2 verification, badges and widgets, API keys and quotas, or interpreting Veil endpoint responses and errors.
---

# Veil integration

Veil is the public directory of cryptographic identities. It resolves accounts people know (Discord, GitHub, email, domain and Fediverse) to a permanent card and its signing keys, so you can find someone's key from an account you already know. A stolen account cannot produce the owner's signature. Every card change enters a public, witnessed transparency log.

Use `https://veil.pub` for the directory, `https://log.veil.pub` for the log and [the documentation](https://veil.pub/docs) for contracts. Public reads and verification work anonymously. Optional API keys give server and local clients a shared owner allowance.

The directory moved from `veil.rip` on 6 November 2026. The old host redirects its pages and its API still answers in place, so earlier integrations keep working. New code uses `veil.pub`.

## Start with the current contract

The [live catalogue](https://veil.pub/v1/integrations) contains 129 endpoints and 18 guides (revision `eeb4170b004a4565`). `GET /v1/integrations/{id}` returns a localised entry and the catalogue revision. Its ID is also the documentation slug. Read the entry before implementing a call, and follow its access mode, parameters, response types and verification requirements. The same reference is an OpenAPI 3.1 document at `GET /openapi.json`.

- `responses` gives HTTP status, content type, field names, types, descriptions and selected examples.
- `responseObjects` describes nested types, and `responseHeaders` describes headers.
- `errorDetails` gives HTTP status, stable code, explanation, recovery action and scope. `response` and `errors` remain available for existing consumers.
- Read [references/responses-and-errors.md](references/responses-and-errors.md) when interpreting fields, handling errors, caching responses or choosing retries.

Paths under `/v1`, documented fields and error codes stay. New fields and codes can appear, so ignore what you do not know and branch on `error.code`. A removal is announced on the [changelog](https://veil.pub/docs/changelog) at least 90 days ahead, with `Deprecation` and `Sunset` headers on the affected call.

The directory writes to the log `log.veil.rip/staging-1` in **format 2**, and `GET /v1/log` answers `"format": 2` with `staffOrg`, the token of the Veil organisation. The origin keeps that name for good, because every checkpoint signs it. Cards in format 2 carry signed labels, a verifiable index and signed staff statements. Read [references/format-2.md](references/format-2.md) before you parse `current`, `authority`, `state` or `index`, or verify a card in your own code. The examples use card 1 (a person, alias `gab`) and card 2 (the Veil organisation, alias `veil`).

## Bundled client

`scripts/veil.py` uses Python's standard library. Put client options before the command.

```bash
python scripts/veil.py lookup --account github:Gabriele73
python scripts/veil.py lookup --key 73ad6159583a43f8ad230a215b758db680efcd3ce32ab8e83c622eeca883e68a
python scripts/veil.py card 1
python scripts/veil.py org veil
python scripts/veil.py authority 1
python scripts/veil.py members 2
python scripts/veil.py verify --block-file signed.txt
python scripts/veil.py verify --signature-file SHA256SUMS.veil --file veil-0.1.4-darwin-arm64.zip
python scripts/veil.py keys-file gab --format allowed_signers
python scripts/veil.py alerts 1
python scripts/veil.py card-statements o veil
python scripts/veil.py canary
python scripts/veil.py doc verify-file
python scripts/veil.py doc errors --lang it
python scripts/veil.py --include-headers card 1
python scripts/veil.py --api-key-env VEIL_API_KEY quota
python scripts/veil.py --output badge.svg get /o/2/badge.svg
python scripts/veil.py --dry-run summary 1
```

The named environment variable supplies an optional bearer secret, and request previews redact it. Keep keys in server secret configuration. The client never signs management requests or handles device private keys. `verify --file` hashes the file on this machine and sends the hash and the name. Read-only transient failures get at most one retry. If the required wait exceeds 30 seconds, the client returns the response without retrying early. `--if-none-match` sends a card's `ETag` back, and a `304` leaves any `--output` file untouched.

## Choose a call

| Job | Call |
|---|---|
| Find a card from whatever a person typed (a username, a login, an address, a profile URL, a key) | `GET /v1/lookup?account=<value>` |
| Find a card by one exact account ID, key or fingerprint | `GET /v1/lookup` with exactly one lookup parameter |
| Link to an account's card | `https://veil.pub/github/<login>`, `/discord/<ID>`, `/email/<address>`, `/domain/<name>`, `/fediverse/<@user@server>` |
| Resolve an alias | `GET /v1/aliases/{kind}/{alias}`, or the card at `/u/{alias}.json` and `/o/{alias}.json` |
| Read a full card and its proof | `GET /u/{card}.json` or `/o/{card}.json`, revalidated with `If-None-Match` |
| Display current name, image or badges | `GET /v1/identities/{n}/summary` |
| Verify a signed message | `POST /v1/verify` with a block or raw signature fields |
| Verify a signed file or release | `POST /v1/verify` with `signature`, the file's hash and its `name` |
| Read a key's owner or validity | `GET /v1/keys/{key}` or `/active-at?t=<Unix seconds>` |
| Fetch a person's SSH, OpenPGP or minisign keys | `GET /u/{card}/keys.txt?format=...` or `/u/{card}.keys` |
| See whether an account was declared stolen or moved | `alert` in the lookup answer, or `GET /v1/identities/{n}/alerts` |
| Read a card's signed statements | `GET /{kind}/{card}/statements.json`, `GET /v1/statements/{id}` or the Atom feed |
| Learn the log, its format and the Veil organisation | `GET /v1/log` (`format`, `staffOrg`) |
| Verify a card in your own code | The card JSON, then [references/format-2.md](references/format-2.md) |
| Page authority versions or staff statements (format 2) | `GET /v1/identities/{n}/authority`, or follow `index.statementsNext` |
| Poll for changes | `GET /v1/identities/{n}/versions?latest=true&limit=1`, `/events?after=<id>`, or the card's `ETag` |
| Embed a card | `/{kind}/{n}/badge.svg`, `/{kind}/{n}/embed` or `/embed.js`, with the card number |
| Let people sign in to your site with their card | OpenID Connect at `https://veil.pub`, see [references/sign-in.md](references/sign-in.md) |
| Give Discord roles to members with a card | Linked Roles, `GET /v1/discord/linked-roles` and the [`discord-app`](https://veil.pub/docs/discord-app) guide |
| Read the warrant canary | `GET /v1/canary` |
| Generate a client or validate responses | `GET /openapi.json` |
| Inspect an integration's allowance | `GET /v1/rate-limit` with its bearer key |
| Create or manage integration keys | Device-signed `/v1/developer/accounts/{n}` routes, see the [API-key reference](references/api-keys.md) |

[references/endpoints.md](references/endpoints.md) maps all 129 endpoint IDs to paths and access requirements. Read its relevant group for calls outside this table.

## Resolve and verify

Supply exactly one lookup parameter. The ID parameters take stable platform IDs: `discord` a 17 to 20 digit user ID, `github` a numeric account ID. `account` takes anything typed, a Discord username or a GitHub login included, and the answer says what it was read as in `match.by` and `understood`.

A name is weaker than an ID, because it can pass to someone else.

- Store `match.subject` (the stable ID) and the card number `n`. Treat the name as a dated label.
- When `match.stale` is true, the platform last confirmed the name more than 2 days ago. Show the ID and the date `recorded`, and do not open the card unasked.
- `409 ambiguous` lists `candidates`. Show them all and never pick the first.
- An `alert` in the answer means the owner declared that account stolen, abandoned or moved. Show it before anything else.
- A card's alias can equal someone else's login. When `match.by` is `alias`, the word is an address the card chose.

Display names are not unique and are never searched. Aliases can change or be reassigned, so `/u/gab` and `/o/veil` are for people, and stored references use `/u/1` and `/o/2`.

For a message, use the overall `valid` verdict. HTTP 200 with `valid: false` is a completed negative check. `signatureOk` can be true after a key was revoked. Read `reason`, `keyState` and any requested account ownership result. When checking a bot's sender, supply raw `key`, `message`, `signature`, `platform` and `subject` so ownership is checked too. For `at`, use a publication time in Unix seconds that you trust independently. A timestamp written by the signer proves nothing.

For a file, hash it yourself and send the hash, the file's name and the signature. Veil never receives the file. The verdict adds `covers` (`file` or `list`) and `match`, and a wrong file answers `valid: false` with `reason: "hash_mismatch"`. The signature can come from a Veil key or from an SSH, OpenPGP or minisign key that the card holds with a proof of possession.

`POST /v1/verify` sends the message to Veil. [Browser verification](https://veil.pub/verify) keeps data after `#` in the browser and hashes files there. Ask for a network verification only within the user's intended sharing of that message.

A summary carries no proof. A full card can return 200 with `proof: null`, and in format 2 also with `index: null` or `index.statements: null`. Leave such a card unverified and retry later. `/v1/log`, `/v1/verify`, a lookup answer, a keys file and every image report the server's checks. Independent verification starts from a log key and witness policy you pinned yourself and checks the signed labels, the index proof, the authority versions, the state roots and the chain of staff statements. Only accepted organisation memberships count as authority. A `304` on the card means its bytes did not change, but freshness still has to be checked again.

## Access and limits

Anonymous browser requests use public CORS and omit credentials. CORS opens public reads and `POST /v1/verify`. It does not allow `Authorization` or device-signing headers. Keep bearer keys in server or local clients.

Without a key, an IP gets 300 public reads a minute, and verification counts as a read. An API owner normally shares 600 requests per minute across all keys. Verification also uses a shared 120-per-minute bucket. Both refill continuously. Optional key caps and UTC-day caps can further constrain access. Rotation does not reset the owner's allowance. Signed writes keep their own limits. Read [references/api-keys.md](references/api-keys.md) for scopes, expiry, custom limits, status headers and private receipts.

Errors use a stable `error.code` and a mutable English `error.message`. Use the endpoint's `errorDetails` and [the error guide](https://veil.pub/docs/errors) for the next action. Respect `Retry-After`, and check the current state before repeating a signed operation. A service failure is never a successful verification. The endpoints under `/oidc/` follow OAuth instead and answer `{"error", "error_description"}`.

## Signed operations

Creating or changing a card, publishing an alert or a statement, connecting Linked Roles and managing API keys or sign-in apps require an authorised device signature. A bearer key grants public reads and verification only. Read [references/signed-requests.md](references/signed-requests.md) when the user requests a signed operation.

On a format 2 log a card version is `{label, body, signature, pictureData?}`: the label carries the operations that change who can sign, and the body carries the rest. A format 1 `record` gets `400 wrong_format`. Pictures are named by hash (`{type, sha256, size}`, PNG, GIF or SVG, up to 2 MiB) and their bytes travel beside the version.

Prepare the unsigned request and signing bytes, then let the owner sign on their own device. Never ask them to paste, transmit or store a device private key in the integration. A key-management action records a private receipt, and publishing an identity version requires witnessed inclusion in the public log. With `Prefer: respond-async` the server answers `202` as soon as the log holds the entry, and the change counts only once `witnessed` is true. After a timeout, check the relevant state before signing another request.
