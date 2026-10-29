# Veil endpoint reference

Snapshot of [the live catalogue](https://veil.rip/v1/integrations), revision `97321eb55810004b`, reviewed 29 October 2026. It contains **71 endpoints and 10 guides**. Each endpoint ID is its docs slug and the key for `GET /v1/integrations/{id}`.

The detail JSON contains response status, content type, fields, nested objects, headers, selected examples and error recovery guidance. Read [responses and errors](responses-and-errors.md) before relying on an HTTP status or parsing a body. Fetch a current detail with `python scripts/veil.py doc <id>`.

`directory` uses `https://veil.rip`. `log` uses `https://log.veil.rip`. Access modes are `public` (anonymous, with optional bearer access only on eligible directory calls), `api-key` (bearer required), `signed` (device signature), `private-code` (secret URL token), `public-write` (temporary unauthenticated operation) and `provider-callback` (OAuth return page). Browser modes distinguish anonymous `fetch`, `frame`, `navigation` and `local-or-server`.

The directory runs log format 2 since 28 October 2026. Six reads exist only on a format 2 log and are marked **format 2** below. On a format 1 log they answer `400 wrong_format`. [Log format 2](format-2.md) explains the shapes they return and how to verify them.

## Guides

- [`start`](https://veil.rip/docs) Integrate Veil
- [`browser-apps`](https://veil.rip/docs/browser-apps) Call Veil from a website
- [`message-verification`](https://veil.rip/docs/message-verification) Verify a signed message
- [`sharing`](https://veil.rip/docs/sharing) Show a card on your site
- [`proofs`](https://veil.rip/docs/proofs) Verify a card independently
- [`signed-requests`](https://veil.rip/docs/signed-requests) Make a signed request
- [`limits`](https://veil.rip/docs/limits) Limits and errors
- [`api-reference`](https://veil.rip/docs/api-reference) API reference
- [`api-keys`](https://veil.rip/docs/api-keys) Use a developer API key
- [`errors`](https://veil.rip/docs/errors) Responses and errors

The `proofs` and `signed-requests` guides still describe the format 1 record. For format 2 use [format-2.md](format-2.md) and [signed-requests.md](signed-requests.md).

## Find people and cards

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`lookup`](https://veil.rip/docs/lookup) | `GET /v1/lookup` | directory | `public` / `fetch` | Find the card that holds one exact account, key or fingerprint. |
| [`person-card`](https://veil.rip/docs/person-card) | `GET /u/{card}.json` | directory | `public` / `fetch` | Read the full public card, signed record, proof and recent history. |
| [`organisation-card`](https://veil.rip/docs/organisation-card) | `GET /o/{card}.json` | directory | `public` / `fetch` | Read an organisation, its signed membership record, public links and proof. |
| [`summary`](https://veil.rip/docs/summary) | `GET /v1/identities/{n}/summary` | directory | `public` / `fetch` | Get current metadata without downloading signed records, proofs or history. |
| [`aliases`](https://veil.rip/docs/aliases) | `GET /v1/aliases/{kind}/{alias}` | directory | `public` / `fetch` | Check availability and find the permanent card behind a claimed alias. |
| [`platforms`](https://veil.rip/docs/platforms) | `GET /v1/platforms` | directory | `public` / `fetch` | Find the supported platforms, proof methods and their current availability. |

## Keys and signatures

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`key-info`](https://veil.rip/docs/key-info) | `GET /v1/keys/{key}` | directory | `public` / `fetch` | Look up a public key, the card holding it and its validity period. |
| [`key-at-time`](https://veil.rip/docs/key-at-time) | `GET /v1/keys/{key}/active-at` | directory | `public` / `fetch` | Ask whether a key was active at a particular time. |
| [`verify-message`](https://veil.rip/docs/verify-message) | `POST /v1/verify` | directory | `public` / `fetch` | Check a signature block or an explicit key, message and signature. This POST only reads. |
| [`grant-key`](https://veil.rip/docs/grant-key) | `GET /v1/grant-key` | directory | `public` / `fetch` | Read the public key used to sign account-linking grants. |

## Versions and changes

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`versions`](https://veil.rip/docs/versions) | `GET /v1/identities/{n}/versions` | directory | `public` / `fetch` | Page through the signed versions. Format 2 items carry label, body, signature and entry. |
| [`history`](https://veil.rip/docs/history) | `GET /v1/identities/{n}/history` | directory | `public` / `fetch` | Read older version events and the account transfers around them. |
| [`version-proof`](https://veil.rip/docs/version-proof) | `GET /v1/identities/{n}/versions/{k}/proof` | directory | `public` / `fetch` | Get the inclusion proof for a particular version under the current checkpoint. |
| [`events`](https://veil.rip/docs/events) | `GET /v1/identities/{n}/events` | directory | `public` / `fetch` | Read takeover and publication-reconciliation events for a card. |
| [`takeovers`](https://veil.rip/docs/takeovers) | `GET /v1/takeovers` | directory | `public` / `fetch` | Read account transfer requests involving a card on either side. |
| [`authority`](https://veil.rip/docs/authority) | `GET /v1/identities/{n}/authority` | directory | `public` / `fetch` | **Format 2.** Page through the versions that changed who can sign the card. |
| [`statements`](https://veil.rip/docs/statements) | `GET /v1/identities/{n}/statements` | directory | `public` / `local-or-server` | **Format 2.** Page through a card's counted staff statements after the first page in `index.statements`. |
| [`labels`](https://veil.rip/docs/labels) | `GET /v1/identities/{n}/labels` | directory | `public` / `fetch` | **Format 2.** Read the chain of labels alone, up to 1000 a page. |
| [`version-v2`](https://veil.rip/docs/version-v2) | `GET /v1/identities/{n}/versions/{v}` | directory | `public` / `fetch` | **Format 2.** Read one version whole: label, body, signature and log position. |
| [`set-path`](https://veil.rip/docs/set-path) | `GET /v1/identities/{n}/sets/{set}/path` | directory | `public` / `fetch` | **Format 2.** Get the sparse Merkle path of one item, or of its empty place, to update a set root. |

## Organisations and public status

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`memberships`](https://veil.rip/docs/memberships) | `GET /v1/identities/{n}/orgs` | directory | `public` / `fetch` | Read a person’s organisation memberships or an organisation’s members. |
| [`staff-roles`](https://veil.rip/docs/staff-roles) | `GET /v1/staff` | directory | `public` / `fetch` | Identify Veil’s official organisation and the powers of each staff role. |
| [`moderation`](https://veil.rip/docs/moderation) | `GET /v1/identities/{n}/moderation` | directory | `public` / `fetch` | Read the public status and moderation actions affecting a card. |
| [`moderation-entries`](https://veil.rip/docs/moderation-entries) | `GET /v1/moderation/entries` | directory | `public` / `fetch` | Page through public moderation, badge and badge-removal log entries. |
| [`badge-catalogue`](https://veil.rip/docs/badge-catalogue) | `GET /v1/badges/catalogue` | directory | `public` / `fetch` | Read badge IDs, labels and assignment rules. |
| [`card-badges`](https://veil.rip/docs/card-badges) | `GET /v1/identities/{n}/badges` | directory | `public` / `fetch` | Read a card’s badges and removed badge history. |
| [`members`](https://veil.rip/docs/members) | `GET /v1/organizations/{n}/members` | directory | `public` / `fetch` | **Format 2.** Read the members whose position starts with a prefix, with the proof to the members root. |

## Share and embed

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`oembed`](https://veil.rip/docs/oembed) | `GET /oembed` | directory | `public` / `fetch` | Get an embeddable card or link preview for a supported Veil URL. |
| [`badge-image`](https://veil.rip/docs/badge-image) | `GET /{kind}/{card}/badge.svg` | directory | `public` / `fetch` | Show a linked status badge in a README, profile or forum signature. |
| [`card-image`](https://veil.rip/docs/card-image) | `GET /{kind}/{card}/card.png` | directory | `public` / `fetch` | Read a 1200 by 630 PNG for a card’s social preview. |
| [`logo`](https://veil.rip/docs/logo) | `GET /{kind}/{n}/logo.{format}` | directory | `public` / `fetch` | Read the image currently published on a person’s or organisation’s card. |
| [`widget`](https://veil.rip/docs/widget) | `GET /{kind}/{card}/embed` | directory | `public` / `frame` | Show a read-only card that verifies itself in the visitor’s browser. |
| [`embed-loader`](https://veil.rip/docs/embed-loader) | `GET /embed.js` | directory | `public` / `fetch` | Turn data-veil-card and data-veil-org elements into card frames. |
| [`preview-image`](https://veil.rip/docs/preview-image) | `GET /preview.png` | directory | `public` / `fetch` | Read the general directory preview image. |
| [`verify-page`](https://veil.rip/docs/verify-page) | `GET /verify` | directory | `public` / `navigation` | Open a message check that runs in the reader’s browser. |
| [`verify-link`](https://veil.rip/docs/verify-link) | `GET /v/{n}/{signature}` | directory | `public` / `navigation` | Share a signed message with a server-generated social preview. |
| [`snippet-builder`](https://veil.rip/docs/snippet-builder) | `GET /embed` | directory | `public` / `frame` | Copy a card link, badge or widget with a live preview. |

## Transparency log

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`log-state`](https://veil.rip/docs/log-state) | `GET /v1/log` | directory | `public` / `fetch` | Identify the active log, its format and the checkpoint and witness state seen by the server. |
| [`log-about`](https://veil.rip/docs/log-about) | `GET /{log}/` | log | `public` / `navigation` | Read the log origin, verification key, daily request allowance and contact. |
| [`log-checkpoint`](https://veil.rip/docs/log-checkpoint) | `GET /{log}/checkpoint` | log | `public` / `fetch` | Read the log’s signed size and Merkle root. |
| [`log-policy`](https://veil.rip/docs/log-policy) | `GET /{log}/policy` | log | `public` / `fetch` | Read the log key, witness keys and quorum rule. |
| [`log-witnesses`](https://veil.rip/docs/log-witnesses) | `GET /{log}/witnesses` | log | `public` / `fetch` | Read each configured witness’s latest stored cosignature. |
| [`log-hash-tiles`](https://veil.rip/docs/log-hash-tiles) | `GET /{log}/tile/{level}/{index}` | log | `public` / `fetch` | Read C2SP hash tiles for inclusion and consistency proofs. |
| [`log-entry-tiles`](https://veil.rip/docs/log-entry-tiles) | `GET /{log}/tile/entries/{index}` | log | `public` / `fetch` | Read C2SP bundles of public log entries. |

The current log is `staging-1`. Its host also serves `GET /{log}/index` and `GET /{log}/index/{token}` for format 2 index bundles, which the catalogue does not list. See [format-2.md](format-2.md#on-the-log-host).

## Developer API keys

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`developer-account`](https://veil.rip/docs/developer-account) | `GET /v1/developer/accounts/{n}` | directory | `signed` / `local-or-server` | Read shared limits, quota balances, usage, keys and private activity. |
| [`developer-keys`](https://veil.rip/docs/developer-keys) | `GET /v1/developer/accounts/{n}/keys` | directory | `signed` / `local-or-server` | List key metadata without revealing secrets. |
| [`create-api-key`](https://veil.rip/docs/create-api-key) | `POST /v1/developer/accounts/{n}/keys` | directory | `signed` / `local-or-server` | A person or organisation owner signs the request to issue a secret bearer key. |
| [`revoke-api-key`](https://veil.rip/docs/revoke-api-key) | `DELETE /v1/developer/accounts/{n}/keys/{id}` | directory | `signed` / `local-or-server` | Permanently stop a key owned by this card. |
| [`api-key-audit`](https://veil.rip/docs/api-key-audit) | `GET /v1/developer/accounts/{n}/audit` | directory | `signed` / `local-or-server` | Inspect management receipts and the original device signatures. |
| [`rate-limit`](https://veil.rip/docs/rate-limit) | `GET /v1/rate-limit` | directory | `api-key` / `local-or-server` | Read your current owner and key quotas without spending the primary allowance. |

## Manage a card

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`create-person`](https://veil.rip/docs/create-person) | `POST /v1/identities` | directory | `signed` / `local-or-server` | Publish the first version, signed by the key that version adds. |
| [`publish-person`](https://veil.rip/docs/publish-person) | `POST /v1/identities/{n}/versions` | directory | `signed` / `local-or-server` | Change keys, linked accounts, alias or other signed card fields. |
| [`create-organisation`](https://veil.rip/docs/create-organisation) | `POST /v1/organizations` | directory | `signed` / `local-or-server` | Publish an organisation’s first version, signed by its founder’s active person key. |
| [`publish-organisation`](https://veil.rip/docs/publish-organisation) | `POST /v1/organizations/{n}/versions` | directory | `signed` / `local-or-server` | Publish a change authorised by an accepted owner or administrator. Role rules still apply. |
| [`salt-ticket`](https://veil.rip/docs/salt-ticket) | `POST /v1/salt-tickets` | directory | `public-write` / `local-or-server` | Commit the server’s half of the first-version salt before the device chooses its half. |
| [`start-link`](https://veil.rip/docs/start-link) | `POST /v1/links/start` | directory | `signed` / `local-or-server` | Begin OAuth, email, domain or Fediverse proof for a card you can manage. |
| [`complete-link`](https://veil.rip/docs/complete-link) | `POST /v1/links/{state}/complete` | directory | `signed` / `local-or-server` | Complete a proof using the same key that started it. |
| [`link-state`](https://veil.rip/docs/link-state) | `GET /v1/links/{state}` | directory | `private-code` / `local-or-server` | Resume a proof with its secret state token. |
| [`oauth-callback`](https://veil.rip/docs/oauth-callback) | `GET /v1/links/callback/{platform}` | directory | `provider-callback` / `local-or-server` | Receive the redirect from Veil’s configured Discord or GitHub application. |
| [`request-device`](https://veil.rip/docs/request-device) | `POST /v1/device-requests` | directory | `public-write` / `local-or-server` | Create a temporary pairing code for a new device’s public key. |
| [`read-device-request`](https://veil.rip/docs/read-device-request) | `GET /v1/device-requests/{code}` | directory | `signed` / `local-or-server` | Read a pairing request with an active person key before adding the new device. |
| [`invite-accept`](https://veil.rip/docs/invite-accept) | `POST /v1/orgs/{n}/invites/{id}/accept` | directory | `signed` / `local-or-server` | The invited person signs with an active key. The JSON body contains nonce and timestamp. |
| [`invite-decline`](https://veil.rip/docs/invite-decline) | `POST /v1/orgs/{n}/invites/{id}/decline` | directory | `signed` / `local-or-server` | The invited person signs with an active key. The JSON body contains nonce and timestamp. |
| [`cancel-takeover`](https://veil.rip/docs/cancel-takeover) | `POST /v1/takeovers/{id}/cancel` | directory | `signed` / `local-or-server` | The current account holder signs to cancel an open transfer. |
| [`logo-preview-create`](https://veil.rip/docs/logo-preview-create) | `POST /v1/logo-previews` | directory | `signed` / `local-or-server` | Validate a profile image or organisation logo before including it in a signed version. |
| [`logo-preview-read`](https://veil.rip/docs/logo-preview-read) | `GET /v1/logo-previews/{hash}.{format}` | directory | `private-code` / `local-or-server` | Read a temporary image using the preview URL returned to its creator. |
| [`request-erasure`](https://veil.rip/docs/request-erasure) | `POST /v1/identities/{n}/erase` | directory | `signed` / `local-or-server` | An active person key or an organisation owner signs the erasure request. There is a 24-hour cancellation window. |
| [`cancel-erasure`](https://veil.rip/docs/cancel-erasure) | `POST /v1/identities/{n}/erase/cancel` | directory | `signed` / `local-or-server` | An active authorised key cancels erasure during its cancellation window. |
| [`submit-report`](https://veil.rip/docs/submit-report) | `POST /v1/identities/{n}/reports` | directory | `signed` / `local-or-server` | An active person key submits a moderation report about a card. |

## Service reference

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`catalogue`](https://veil.rip/docs/catalogue) | `GET /v1/integrations` | directory | `public` / `fetch` | Read the guides and endpoint index as JSON. |
| [`catalogue-entry`](https://veil.rip/docs/catalogue-entry) | `GET /v1/integrations/{id}` | directory | `public` / `fetch` | Read one guide or endpoint contract, including examples. |

Public CORS does not allow bearer or device-signing credentials. It opens the public reads and `POST /v1/verify`, but not `GET /v1/identities/{n}/statements`, which a script on another origin cannot read. [API keys](api-keys.md) describes the six developer endpoints and their access requirements. Private staff routes are outside this catalogue.

## Detailed contracts

Captured from the docs pages and checked against the live service on 29 October 2026. For the full field tables, nested types and errors, use `python scripts/veil.py doc <id>`. The examples use the two cards that exist today: card 1, the person Gabriele Todaro, and card 2, the Veil organisation.

### GET /v1/lookup

Exactly one query parameter. Errors: `400 invalid_parameter`, `404 not_found`.

- `discord`: stable numeric user ID, 17 to 20 digits
- `github`: numeric account ID, not the login
- `email`: the complete address
- `domain`: the exact domain, no trailing dot, IDNs as their ASCII A-label
- `fediverse`: the complete `@user@server`
- `key`: an Ed25519 public key in hex, or the full composite key in base64 (URL-encode it). A revoked key still finds its card.
- `fingerprint`: the 12 words (English or Italian) or the 60 digits

Response: `identity` (the short card, including `alias` and `aliasUrl`), `match.by` and `match.value` (the normalised query), and a nullable `takeover` with `toIdentity`, `openedAt` and `resolvesAt`. Fetch the full card for its proof.

`GET /v1/lookup?key=73ad6159583a43f8ad230a215b758db680efcd3ce32ab8e83c622eeca883e68a` returns card 1. Card 1 has no linked accounts yet, so account lookups such as `?github=109546049` answer `404 not_found` today.

There is no alias parameter. The search box on Veil's pages accepts `@alias`, `u/alias` and `o/alias`, and the API equivalent is `GET /v1/aliases/{kind}/{alias}` or the card at `/u/{alias}.json` and `/o/{alias}.json`.

### GET /u/{card}.json and /o/{card}.json

`card` is the permanent number or the current alias. Without `.json`, send `Accept: application/json`. `/v1/identities/{n}` and `/v1/organizations/{n}` need the permanent number. A person card has `n, id, url, type, keys, links, orgs, events, fingerprint, proof, historyBefore` and the other presentation fields. An organisation's JSON `type` is `organization` and it adds `members`. Errors include `404 not_found`, `410 erased` (with a public receipt) and `422 not_an_organization` on `/o/` for a person. A successful response can have `proof: null` when the server cannot verify the log at that moment. Keep such a card unverified.

On a format 2 log the card adds `format`, `current`, `authority`, `authorityNext`, `state`, `index` and `standing`, and `proof` carries the format 2 entry instead of the record. [format-2.md](format-2.md) lists every field.

Card JSON responses carry a weak `ETag` (a SHA-256 of the JSON bytes), `Cache-Control: private, no-cache, must-revalidate` and `Vary: Accept`. Send the tag back in `If-None-Match` and the server answers `304` with no body when the rebuilt card, with its current visibility, moderation and proof, has identical bytes. A changed record, checkpoint or moderation state changes the tag. Errors keep their own status. A 304 only saves the download. Re-check freshness, and keep a stored verdict only for the exact bytes you verified.

### GET /v1/identities/{n}/summary

Fields: `n, url, name, initials, type, version, keys, orgs, badges, nameHidden, logo, alias, aliasUrl`. `nameHidden` is a boolean here and `logo` can be null. Errors `404`, `410`. It carries no proof and is the same in both formats.

### GET /v1/aliases/{kind}/{alias}

`kind` is `u` or `o`. `alias` is 3 to 32 ASCII letters, digits, hyphens or underscores, starting with a letter and ending with a letter or digit. Response: `kind`, `alias`, `available`, `status` (`available`, `claimed`, `publishing`, `quarantined` or `reserved_name`), `url`, `identity` (`n` and permanent `url` when claimed), `reusableAt`, `quarantineDays` (30), `previousIdentity` and `reservedFor`. Availability does not reserve a name. Errors include `400 invalid_parameter` and `400 invalid_alias`.

The alias `veil` under `/o/` is reserved for the Veil organisation. Today it is not set, so `/o/veil` answers `404 not_found` and the alias check says:

```json
{"kind": "o", "alias": "veil", "available": false, "status": "reserved_name", "url": "https://veil.rip/o/veil",
 "identity": null, "reusableAt": null, "quarantineDays": 30, "previousIdentity": null,
 "reservedFor": {"n": 2, "url": "https://veil.rip/o/2"}}
```

An alias is an address chosen by the card. A change or release stops the old address at once and starts 30 days of quarantine, during which only the previous holder can take it back. Store `n`.

### GET /v1/platforms

Returns `platforms` with IDs, translated labels, `method`, `methods`, `enabled`, `reason` and `organizations` (whether an organisation can link it). Use it to build account-linking choices.

### GET /v1/keys/{key}

`key` is 64 hex characters of an Ed25519 key, or the Ed25519 half of a composite key. Response: `key, alg, ed25519, identity, device, role, state, addedIn, revokedIn, validFrom, validUntil`. Composite keys return the full key in `key`. Errors `400`, `404`.

### GET /v1/keys/{key}/active-at

Query `t` is Unix seconds (default now, range 0 to 253402300799). Response: `at, active, reason, validFrom, validUntil`. `reason` is `active`, `not_yet_valid` or `revoked`.

### POST /v1/verify

No device-signing headers. An optional bearer key needs `verify` scope. The JSON body takes one of two forms.

- Block mode: `block` (the full pasted signature block, at most 32768 characters) and an optional `at` (Unix seconds, default now). It cannot be combined with `key`, `message`, `signature`, `platform` or `subject`.
- Raw mode: `key`, `message` (the exact UTF-8 text) and `signature`. Ed25519 keys and signatures are hex. Composite keys and signatures are base64. The optional pair `platform` and `subject` checks account ownership at `at`.

Response: `valid` (the overall verdict), `signatureOk`, `identity`, `device`, `role`, `keyState`, `account` and `reason`. Block mode also returns `block`, the parsed block, and `key`, the matching key when one is found. HTTP 200 can carry `valid: false`, so read the fields to decide. Errors: `400 invalid_block`, `400 invalid_parameter`. From browsers use `fetch(..., {credentials: "omit"})`. This call is the same in both log formats.

Share links, from the guide, with `message` and `signatureBytes` from the signer and `cardNumber`:

```js
const b64u = b => btoa(String.fromCharCode(...b)).replaceAll("+","-").replaceAll("/","_").replace(/=+$/,"");
const m = b64u(new TextEncoder().encode(message)), s = b64u(signatureBytes);
const browserLink = `https://veil.rip/verify#u=${cardNumber}&m=${m}&s=${s}`;      // stays in browser, both algorithms
const previewLink = `https://veil.rip/v/${cardNumber}/${s}?m=${m}`;               // Ed25519 only, message <= 1500 UTF-8 bytes
```

### GET /v1/grant-key

Returns `alg, key, format, signingPrefix` for account-linking grants. A grant is the directory's statement about an account proof: check its signature, scope and expiry. A grant alone does not publish a card version.

### GET /v1/identities/{n}/versions

Query: `after` (the version to continue after, default 0), `limit` (1 to 200, default 50), `latest=true` (only the latest version, cannot be combined with a nonzero `after`). `versions` is oldest first. Follow `next` as `after` until it is null. A 2 MiB byte budget can return fewer rows than `limit`. Errors `400`, `404`, `410`.

On a format 2 log each item is `{label, body, signature, signedBy, logIndex, publishedAt, entry}`, with `label` and `body` as canonical texts. Check that the body hashes to `label.body`, that each label's `prev` is the hash of the label before, and each signature against the authority before it. On a format 1 log each item has `record`, `salt` and `commitment` in place of `label` and `body`.

### GET /v1/identities/{n}/versions/{v} (format 2)

One version whole, in the shape of an item of `versions`. `404` when the version does not exist.

### GET /v1/identities/{n}/authority (format 2)

Query: `after` (default 0) and `limit` (1 to 200, default 50). Response: `{"authority": [...], "next": k | null}`, the versions whose `label.auth` is not empty, oldest first, in the shape of `versions`. Pass `next` as `after`. The card's own `authority` field already holds the first 50, each with its log position `i` and `inclusion`.

### GET /v1/identities/{n}/statements (format 2)

The pages after `index.statements` of the card. Query: `from` (a log position, the `prev` of the last statement on the page before) and `size` (the checkpoint size of the card's index bundle). Both are required. Follow the card's `index.statementsNext` instead of building the query yourself. Response: `{"n", "size", "statements": [{"i", "entry", "inclusion", "by"}], "statementsNext": "<path>" | null}`, up to 200 statements newest first, with inclusion proofs in the tree of `size` entries. It also answers for a closed card. `400 invalid_parameter` for a `from` beyond `size`, `503 log_unavailable` when the log cannot be verified or an entry cannot be proven. This endpoint is not open to CORS.

### GET /v1/identities/{n}/labels (format 2)

Query: `after` (default 0) and `limit` (1 to 1000, default 1000). Response: `{"labels": ["<canonical label>", ...], "next": k | null}`, oldest first, with `null` for an erased version. A full page never changes and is served with `Cache-Control: public, max-age=31536000, immutable`. The last, shorter page is `no-cache`. Labels alone are enough to follow the `prev` chain. Bodies and signatures come from `versions`.

### GET /v1/identities/{n}/sets/{set}/path (format 2)

`set` is `keys`, `links`, `orgs` or `members`. Query `key` is the item key: a public key, the platform and subject separated by a newline (`%0A`), or a card token. Response: `n, version, set, key, position, item, proof, root`. `item` is `null` for a key that is not in the set, and the proof then starts from the empty leaf. A signer uses the path to compute the new set root after changing one item.

### GET /v1/organizations/{n}/members (format 2)

Query: `prefix` (standard base64 of the prefix bytes, empty for the first page) and `bits` (0 to 24, default the server's page depth). Response: `n, version, root, prefix, bits, items, proof, pages`, where each item is `{member, role, since}`. Compute the page's subtree root from `items`, fold `proof` up to `root`, and compare it with `state.roots.members` of the card. A page over 4096 members or a prefix of the wrong length is `400 invalid_parameter`. A person answers `422 not_an_organization`.

```json
{"n": 2, "version": 1, "root": "+PLnoN4SNNIkKS68NqKSNzj27wRJ6vtaGyROFwsHN4E=", "prefix": "", "bits": 0,
 "items": [{"member": "uD5J2crwuJtpSSPgObKrUQ", "role": "owner", "since": 1}],
 "proof": {"bitmap": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", "siblings": []}, "pages": 1}
```

### GET /v1/identities/{n}/history

Query: `before` (an exclusive version cursor, omit it for the newest page) and `limit` (1 to 200, default 50). Response `events`. Pass the returned `before` for the next older page. `null` marks the first version. In format 2 the event kinds come from the operations: `created` or `founded`, `added`, `recovery`, `revoked`, `device` (a renamed key), `link`, `unlinked`, `invited`, `member_removed`, `role`, `joined`, `left`, `renamed`, `alias`, `alias_released`, `logo` and `logo_removed`.

### GET /v1/identities/{n}/versions/{k}/proof

The proof object of a full card, for version `k`. In format 2 it is `{version, labelHash, entry, logIndex, leafHash, checkpoint, inclusion, witnesses}`. Verify the entry, the leaf hash, the inclusion and the signed checkpoint. Errors `404`, `503 log_unavailable`.

### GET /v1/identities/{n}/events

Query `after` (a nonnegative event ID, default 0). Response `n, events, next`. Keep `next` and pass it as `after` on the next poll. These events are separate from the signed version history.

### GET /v1/takeovers

Query `identity` (required, a permanent card number). Response `identity` and `takeovers`, newest first, each with `from, to, status, openedAt, resolvesAt`. An open transfer has not changed the owner yet.

### GET /v1/identities/{n}/orgs

Response `n, type, memberships` with role, acceptance and removal state. An invitation is not an accepted membership.

### GET /v1/staff

Response `org` (the Veil organisation: `n`, `url`, `name`, `token`, `nameHidden`, `logo`) and `roles`, the actions each staff role may take. Today `org.n` is 2 and `org.token` equals `staffOrg` of `GET /v1/log`.

### GET /v1/moderation/entries

Query `after` (an exclusive log index, default -1) and `limit` (1 to 500, default 200). Response `org, entries, next`. Follow `next` until null.

### GET /oembed

Query `url` (required: a Veil person, organisation or `/v/` URL), `format=json` (XML gives `501 format_not_implemented`), `maxwidth` (below 280 gives a link response) and `maxheight` (below 200 gives a link response). Cards return type `rich` with the widget HTML and a thumbnail. Verification links and small limits return type `link`. Errors `400`, `404`, `501`.

### Card images

`GET /{kind}/{n}/logo.{svg|png|gif}` serves the exact published picture at the `logo.url` of the card. Pictures are PNG (APNG included, as `image/png`), GIF (animated or not) or a restricted SVG, at most 2 MiB (2,097,152 bytes). PNG and GIF are at most 512 by 512 pixels. A matching `v` query allows one day of public caching. `size=64` or `size=128` on a PNG asks for a smaller display thumbnail. Read [responses-and-errors.md](responses-and-errors.md) for thumbnails. `404 not_found` for a missing or hidden picture, `410 erased`, and `422 not_a_person` or `422 not_an_organization` for the wrong `kind`.

### GET /v1/log

Response includes `origin, size, root, checkpoint, witnesses, quorum, signed, of, quorumMet`, freshness (`newestCosignatureAt`, `fresh`, `freshSeconds`) and consistency (`consistency`, `accepted`). These are the server's own checks. On a format 2 log it adds `"format": 2` and `"staffOrg"`, the token of the Veil organisation. A missing `format` means format 1. Today:

```json
{"origin": "log.veil.rip/staging-1", "quorum": 2, "of": 5, "format": 2, "staffOrg": "d8aKGsTCN1U_lB3NznVocg", "...": "..."}
```

Pin the expected log and witness policy for independent verification. `503 log_unavailable`.

### POST /v1/identities (create-person)

Needs the `X-Public-Key` and `X-Signature` headers. On a format 2 log the JSON body is `label`, `body`, `signature`, the optional `pictureData`, `clientSalt` and `saltTicket` (both required for version 1), `nonce` (16 to 128 characters: letters, digits, `_`, `-`) and `timestamp` (Unix ms within 2 minutes of the server). A format 1 `record` answers `400 wrong_format`. Response `201` with `n, id, url, token, version, commitment, logIndex, publishedAt, checkpoint` after witnessed publication. In format 2 `commitment` is the label hash in hex. Errors include `422 invalid_op`, `422 label_mismatch`, `422 invalid_record`, `401 missing_signature`, `409 version_conflict`, `409 salt_ticket_invalid`, `409 key_already_used` and `503 log_unavailable`. [signed-requests.md](signed-requests.md) has the label, body and operations.

### POST /v1/links/start

Signed. Body: `identity` (the permanent number), `platform` (an ID from `/v1/platforms`), `subject` (required for email, domain and Fediverse, OAuth takes it from the platform) and an optional `method` (domains support `dns_txt` and `well_known`). Response `201` with `state, method, expiresAt, challenge`. Keep `state` private. Starting or completing a proof does not add the account to the card. A published version does.

### Share and embed snippets

```markdown
[![Veil card](https://veil.rip/o/2/badge.svg)](https://veil.rip/o/2)
```

```html
<iframe src="https://veil.rip/o/2/embed" title="Veil organisation card"
  width="560" height="200" loading="lazy" referrerpolicy="no-referrer"></iframe>
<div data-veil-org="2"></div>   <!-- people: data-veil-card="N" -->
<script src="https://veil.rip/embed.js" async></script>
```

Use the number, which never changes. A snippet with an alias stops working when the alias changes or, as with `veil` today, is not set. CSP: allow `frame-src https://veil.rip`, and `script-src https://veil.rip` if you use `embed.js`. Options: `data-theme`, `data-lang`. The SVG badge reports the server's status when it was generated and may be cached. The widget verifies the card in each visitor's browser, in format 2 as in format 1.

### Developer API responses

Read [API keys and shared quotas](api-keys.md) for management access, pagination and the quota response. An owner overview includes `owner`, `suspended`, `limits`, `quota`, `usage`, `history`, `keys`, `next`, `audit` and `permissions`. Overview and list calls never return secret material. Only creation returns a one-time `secret` with the key metadata.

The quota endpoint returns HTTP 200 with `owner`, `key`, `quota`, `rate`, `resource` and `retryAfter`. Reading it does not spend the primary allowance. Minute buckets refill continuously and daily caps reset at midnight UTC.

### GET /v1/integrations and /{id}

Optional `lang=en|it`. The index has `revision`, `language`, `baseUrl`, `documentationUrl`, `groups` and `entries`. Each endpoint summary has `supportsBrowserFetch` and `browserMode`. A detail has `revision`, `language` and `entry`. Endpoint entries expose `responses`, `responseObjects`, `responseHeaders` and `errorDetails`, plus request parameters and the earlier summaries. A matching `If-None-Match` returns 304 with no body. Cache by revision, entry and language. The public reference can be cached for five minutes.
