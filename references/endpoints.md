# Veil endpoint reference

Snapshot of [the live catalogue](https://veil.rip/v1/integrations), revision `6e91849bbb93df7c`, reviewed 27 October 2026. It contains **65 endpoints and 10 guides**. Each endpoint ID is its docs slug and the key for `GET /v1/integrations/{id}`.

The detail JSON contains response status, content type, fields, nested objects, headers, selected examples and error recovery guidance. Read [responses and errors](responses-and-errors.md) before relying on an HTTP status or parsing a body. Fetch a current detail with `python scripts/veil.py doc <id>`.

`directory` uses `https://veil.rip`; `log` uses `https://log.veil.rip`. Access modes are `public` (anonymous, with optional bearer access only on eligible directory calls), `api-key` (bearer required), `signed` (device signature), `private-code` (secret URL token), `public-write` (temporary unauthenticated operation) and `provider-callback` (OAuth return page). Browser modes distinguish anonymous `fetch`, `frame`, `navigation` and `local-or-server`.

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
| [`versions`](https://veil.rip/docs/versions) | `GET /v1/identities/{n}/versions` | directory | `public` / `fetch` | Page through canonical records, signatures and openings. |
| [`history`](https://veil.rip/docs/history) | `GET /v1/identities/{n}/history` | directory | `public` / `fetch` | Read older version events and the account transfers around them. |
| [`version-proof`](https://veil.rip/docs/version-proof) | `GET /v1/identities/{n}/versions/{k}/proof` | directory | `public` / `fetch` | Get the inclusion proof for a particular version under the current checkpoint. |
| [`events`](https://veil.rip/docs/events) | `GET /v1/identities/{n}/events` | directory | `public` / `fetch` | Read takeover and publication-reconciliation events for a card. |
| [`takeovers`](https://veil.rip/docs/takeovers) | `GET /v1/takeovers` | directory | `public` / `fetch` | Read account transfer requests involving a card on either side. |

## Organisations and public status

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`memberships`](https://veil.rip/docs/memberships) | `GET /v1/identities/{n}/orgs` | directory | `public` / `fetch` | Read a person’s organisation memberships or an organisation’s members. |
| [`staff-roles`](https://veil.rip/docs/staff-roles) | `GET /v1/staff` | directory | `public` / `fetch` | Identify Veil’s official organisation and the powers of each staff role. |
| [`moderation`](https://veil.rip/docs/moderation) | `GET /v1/identities/{n}/moderation` | directory | `public` / `fetch` | Read the public status and moderation actions affecting a card. |
| [`moderation-entries`](https://veil.rip/docs/moderation-entries) | `GET /v1/moderation/entries` | directory | `public` / `fetch` | Page through public moderation, badge and badge-removal log entries. |
| [`badge-catalogue`](https://veil.rip/docs/badge-catalogue) | `GET /v1/badges/catalogue` | directory | `public` / `fetch` | Read badge IDs, labels and assignment rules. |
| [`card-badges`](https://veil.rip/docs/card-badges) | `GET /v1/identities/{n}/badges` | directory | `public` / `fetch` | Read a card’s badges and removed badge history. |

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
| [`log-state`](https://veil.rip/docs/log-state) | `GET /v1/log` | directory | `public` / `fetch` | Identify the active log and read the checkpoint and witness state seen by the server. |
| [`log-about`](https://veil.rip/docs/log-about) | `GET /{log}/` | log | `public` / `navigation` | Read the log origin, verification key, daily request allowance and contact. |
| [`log-checkpoint`](https://veil.rip/docs/log-checkpoint) | `GET /{log}/checkpoint` | log | `public` / `fetch` | Read the log’s signed size and Merkle root. |
| [`log-policy`](https://veil.rip/docs/log-policy) | `GET /{log}/policy` | log | `public` / `fetch` | Read the log key, witness keys and quorum rule. |
| [`log-witnesses`](https://veil.rip/docs/log-witnesses) | `GET /{log}/witnesses` | log | `public` / `fetch` | Read each configured witness’s latest stored cosignature. |
| [`log-hash-tiles`](https://veil.rip/docs/log-hash-tiles) | `GET /{log}/tile/{level}/{index}` | log | `public` / `fetch` | Read C2SP hash tiles for inclusion and consistency proofs. |
| [`log-entry-tiles`](https://veil.rip/docs/log-entry-tiles) | `GET /{log}/tile/entries/{index}` | log | `public` / `fetch` | Read C2SP bundles of public log entries. |

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
| [`create-person`](https://veil.rip/docs/create-person) | `POST /v1/identities` | directory | `signed` / `local-or-server` | Publish the first record, signed by the key named in that record. |
| [`publish-person`](https://veil.rip/docs/publish-person) | `POST /v1/identities/{n}/versions` | directory | `signed` / `local-or-server` | Change keys, linked accounts, alias or other signed card fields. |
| [`create-organisation`](https://veil.rip/docs/create-organisation) | `POST /v1/organizations` | directory | `signed` / `local-or-server` | Publish an organisation’s first record, signed by its founder’s active person key. |
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
| [`logo-preview-create`](https://veil.rip/docs/logo-preview-create) | `POST /v1/logo-previews` | directory | `signed` / `local-or-server` | Validate a profile image or organisation logo before including it in a signed record. |
| [`logo-preview-read`](https://veil.rip/docs/logo-preview-read) | `GET /v1/logo-previews/{hash}.{format}` | directory | `private-code` / `local-or-server` | Read a temporary image using the preview URL returned to its creator. |
| [`request-erasure`](https://veil.rip/docs/request-erasure) | `POST /v1/identities/{n}/erase` | directory | `signed` / `local-or-server` | An active person key or an organisation owner signs the erasure request. There is a 24-hour cancellation window. |
| [`cancel-erasure`](https://veil.rip/docs/cancel-erasure) | `POST /v1/identities/{n}/erase/cancel` | directory | `signed` / `local-or-server` | An active authorised key cancels erasure during its cancellation window. |
| [`submit-report`](https://veil.rip/docs/submit-report) | `POST /v1/identities/{n}/reports` | directory | `signed` / `local-or-server` | An active person key submits a moderation report about a card. |

## Service reference

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`catalogue`](https://veil.rip/docs/catalogue) | `GET /v1/integrations` | directory | `public` / `fetch` | Read the guides and endpoint index as JSON. |
| [`catalogue-entry`](https://veil.rip/docs/catalogue-entry) | `GET /v1/integrations/{id}` | directory | `public` / `fetch` | Read one guide or endpoint contract, including examples. |

Public CORS does not allow bearer or device-signing credentials. [API keys](api-keys.md) describes the six developer endpoints and their access requirements. Private staff routes are outside this catalogue.

## Detailed contracts

Captured from the docs pages. For the full field tables, nested types and errors, use `python scripts/veil.py doc <id>`.

### GET /v1/lookup
Exactly one query param. Errors: `400 invalid_parameter`, `404 not_found`.
- `discord` stable numeric user ID, 17-20 digits
- `github` numeric account ID (not login)
- `email` complete address
- `domain` exact domain, no trailing dot; IDNs as ASCII A-label
- `fediverse` complete `@user@server`
- `key` Ed25519 public key in hex, or full composite key in base64 (URL-encode)
- `fingerprint` 12 words (English or Italian) or 60 digits

Response: `identity` (short card), `match.by` and `match.value` (normalised query), and nullable `takeover` with `toIdentity`, `openedAt` and `resolvesAt`. Then fetch the full card for its proof.

### GET /u/{card}.json and /o/{card}.json
`card` = permanent number or current alias. Without `.json`, send `Accept: application/json`. `/v1/identities/{n}` and `/v1/organizations/{n}` require the permanent number. Person card has `n, id, url, type, keys, links, proof, historyBefore`. Organisation JSON `type` is `organization`; includes members, logo, signed record, proof. Errors include `404 not_found` and `410 erased` (public receipt). A successful response can have `proof: null` when current log verification is unavailable; keep it unverified.

### GET /v1/identities/{n}/summary
Fields include `n, url, name, initials, type, version, keys, orgs, badges, nameHidden, logo, alias, aliasUrl`. `nameHidden` is a boolean and `logo` can be null. Errors `404`, `410`.

### GET /v1/aliases/{kind}/{alias}
`kind` is `u` or `o`. `alias`: 3-32 ASCII letters/digits/hyphen/underscore, starts with a letter, ends with letter or digit. Response: `available`, `status`, `identity` when claimed, `quarantineDays`, `reusableAt`, `reservedFor`. Availability does not reserve a name. Errors include `400 invalid_parameter` and `400 invalid_alias`.

### GET /v1/platforms
Returns `platforms` with IDs, translated labels, methods, availability, organisation support. Use it to build account-linking choices.

### GET /v1/keys/{key}
`key` = 64 hex chars of an Ed25519 key (including the Ed25519 half of a composite key). Response: `identity, device, role, state, addedIn, revokedIn, validFrom, validUntil`; composite keys also give the full key. Errors `400`, `404`.

### GET /v1/keys/{key}/active-at
Query `t` = Unix seconds (default now; range 0..253402300799). Response: `at, active, reason, validFrom, validUntil`; reason is `active`, `not_yet_valid` or `revoked`.

### POST /v1/verify
No device-signing headers. An optional bearer key needs `verify` scope. JSON body, either:
- block mode: `block` (full pasted signature block, max 32768 chars), optional `at` (Unix seconds, default now). Cannot be combined with `key/message/signature/platform/subject`.
- raw mode: `key`, `message` (exact UTF-8 text), `signature` (Ed25519 hex; composite keys and signatures base64), optional pair `platform` + `subject` to check account ownership at `at`.

Response: `valid` (overall), `signatureOk`, `identity`, `device`, `keyState`, `account`, `reason`; block mode also returns the parsed block and a matching key when one is found. HTTP 200 includes `valid: false`; use the fields to decide whether verification succeeded. Errors: `400 invalid_block`, `400 invalid_parameter`. Use `fetch(..., {credentials: "omit"})` from browsers.

Share links (from the guide): with `message` and `signatureBytes` from the signer and `cardNumber`:
```js
const b64u = b => btoa(String.fromCharCode(...b)).replaceAll("+","-").replaceAll("/","_").replace(/=+$/,"");
const m = b64u(new TextEncoder().encode(message)), s = b64u(signatureBytes);
const browserLink = `https://veil.rip/verify#u=${cardNumber}&m=${m}&s=${s}`;      // stays in browser; both algorithms
const previewLink = `https://veil.rip/v/${cardNumber}/${s}?m=${m}`;               // Ed25519 only, message <= 1500 UTF-8 bytes
```

### GET /v1/grant-key
Returns `alg, key, format, signingPrefix` for account-linking grants. A grant is the directory's assertion about an account proof: check signature, scope and expiry. A grant alone does not publish a card version.

### GET /v1/identities/{n}/versions
Query: `after` (version to continue after, default 0), `limit` (1-200, default 50), `latest=true` (only latest; cannot combine with nonzero `after`). `versions` oldest first; follow `next` as `after` until null. Byte budget may return fewer rows. Errors `400`, `404`, `410`. Verify by recomputing commitments, checking signatures and following `prev`.

### GET /v1/identities/{n}/history
Query: `before` (exclusive version cursor; omit for newest page), `limit` (1-200, default 50). Response `events`; pass returned `before` for the next older page, null marks first version.

### GET /v1/identities/{n}/versions/{k}/proof
Same proof object supplied with a full card, for version `k`. Verify the opening, leaf hash, inclusion and signed checkpoint. Errors `404`, `503 log_unavailable`.

### GET /v1/identities/{n}/events
Query `after` (nonnegative event ID, default 0). Response `n, events, next`; keep `next` and pass as `after` on the next poll. Separate from signed version history.

### GET /v1/takeovers
Query `identity` (required, permanent card number). Response `identity` and `takeovers` newest first, each with `from, to, status, openedAt, resolvesAt`. An open transfer has not changed the owner yet.

### GET /v1/identities/{n}/orgs
Response `n, type, memberships` with role, acceptance and removal state. An invitation is not an accepted membership.

### GET /v1/moderation/entries
Query `after` (exclusive log index, default -1), `limit` (1-500, default 200). Response `org, entries, next`; follow `next` until null.

### GET /oembed
Query `url` (required: Veil person, organisation or `/v/` URL), `format=json` (XML gives `501 format_not_implemented`), `maxwidth` (<280 gives a link response), `maxheight` (<200 gives a link response). Cards return type `rich` with widget HTML and thumbnail; verification links and small limits return type `link`. Errors `400`, `404`, `501`.

### GET /v1/log
Response includes `origin, size, root, checkpoint, witnesses, quorum, quorumMet`, freshness and consistency info (the server's own checks). Pin the expected log and witness policy for independent verification. `503 log_unavailable`.

### POST /v1/identities (create-person)
Needs `X-Public-Key` and `X-Signature` headers. JSON body: `record` (complete canonical record), `signature` (record signature), `nonce` (16-128 chars: letters, digits, `_`, `-`), `timestamp` (Unix ms within 2 minutes of server), optional `clientSalt` + `saltTicket` (get the ticket from `POST /v1/salt-tickets` before drawing the client salt). Response `201` with `n, id, url, token, version, commitment, logIndex, publishedAt, checkpoint` after witnessed publication. Errors: `422 invalid_record`, `401 missing_signature`, `409 version_conflict`, `403 signer_not_authorised`, `503 log_unavailable`.

### POST /v1/links/start
Signed. Body: `identity` (permanent number), `platform` (ID from `/v1/platforms`), `subject` (required for email, domain, Fediverse; OAuth gets it from the platform), optional `method` (domains support `dns_txt` and `well_known`). Response `201` with `state, method, expiresAt, challenge`. Keep `state` private. Starting or completing a proof does not add the account to the card; a published version does.

### Share / embed snippets
```markdown
[![Veil card](https://veil.rip/o/veil/badge.svg)](https://veil.rip/o/veil)
```
```html
<iframe src="https://veil.rip/o/veil/embed" title="Veil organisation card"
  width="560" height="200" loading="lazy" referrerpolicy="no-referrer"></iframe>
<div data-veil-org="2"></div>   <!-- people: data-veil-card="N" -->
<script src="https://veil.rip/embed.js" async></script>
```
CSP: allow `frame-src https://veil.rip`, and `script-src https://veil.rip` if using `embed.js`. Options: `data-theme`, `data-lang`. The SVG badge reports server status at generation time and may be cached; the widget verifies in each visitor's browser.

### Developer API responses

Read [API keys and shared quotas](api-keys.md) for management access, pagination and the quota response. An owner overview includes `owner`, `suspended`, `limits`, `quota`, `usage`, `history`, `keys`, `next`, `audit` and `permissions`. Secret material is never returned by overview or list calls. Creation alone returns a one-time `secret` with key metadata.

The quota endpoint returns HTTP 200 with `owner`, `key`, `quota`, `rate`, `resource` and `retryAfter`. Its status read does not spend the primary allowance. Minute buckets refill continuously and daily caps reset at midnight UTC.

### GET /v1/integrations and /{id}

Optional `lang=en|it`. The index has `revision`, `language`, `baseUrl`, `documentationUrl`, `groups` and entry summaries. A detail has `revision`, `language` and `entry`. Endpoint entries expose `responses`, `responseObjects`, `responseHeaders` and `errorDetails`, plus request parameters and existing summaries. A matching `If-None-Match` returns 304 with no body. Cache by revision, entry and language; the public reference can be cached for five minutes.
