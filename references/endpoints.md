# Veil endpoint reference

Source: `https://veil.rip/v1/integrations` (catalogue revision `f6645f1895567561`) and the per-endpoint pages under `https://veil.rip/docs/{id}`. Every row's `id` is the docs slug and the key for `GET /v1/integrations/{id}` (full live contract with examples).

Base URL `https://veil.rip` unless the Base column says `log` (host `https://log.veil.rip`).

Access levels: **public** = no key; **public-write** = unauthenticated write, rate-limited; **signed** = owner's device-key signature (see `signed-requests.md`); **private-code** = secret token in the URL; **provider-callback** = OAuth redirect target.

Contents: [Guides](#guides) · [Find people and cards](#find-people-and-cards) · [Keys and signatures](#keys-and-signatures) · [Versions and changes](#versions-and-changes) · [Organisations and public status](#organisations-and-public-status) · [Share and embed](#share-and-embed) · [Transparency log](#transparency-log) · [Manage a card](#manage-a-card) · [Service reference](#service-reference) · [Detailed contracts](#detailed-contracts)

## Guides

`start` (docs root), `browser-apps`, `message-verification`, `sharing`, `proofs`, `signed-requests`, `limits`, `api-reference` at `https://veil.rip/docs[/{id}]`. Key facts from them are folded into `SKILL.md` and this folder.

## Find people and cards

| id | Method | Path | Access | Summary |
|---|---|---|---|---|
| lookup | GET | `/v1/lookup` | public | Find the card holding one exact account, key or fingerprint |
| person-card | GET | `/u/{card}.json` (also `/u/{card}`, `/v1/identities/{n}`) | public | Full public card, signed record, proof, recent history |
| organisation-card | GET | `/o/{card}.json` (also `/o/{card}`, `/v1/organizations/{n}`) | public | Organisation, signed membership record, links, proof |
| summary | GET | `/v1/identities/{n}/summary` | public | Current metadata without records, proofs, history |
| aliases | GET | `/v1/aliases/{kind}/{alias}` | public | Check alias availability / resolve to permanent card |
| platforms | GET | `/v1/platforms` | public | Supported platforms, proof methods, availability |

## Keys and signatures

| id | Method | Path | Access | Summary |
|---|---|---|---|---|
| key-info | GET | `/v1/keys/{key}` | public | Card holding a key and its validity period |
| key-at-time | GET | `/v1/keys/{key}/active-at` | public | Was a key active at a given time |
| verify-message | POST | `/v1/verify` | public | Check a signature block or key+message+signature (read-only POST) |
| grant-key | GET | `/v1/grant-key` | public | Public key that signs account-linking grants |

## Versions and changes

| id | Method | Path | Access | Summary |
|---|---|---|---|---|
| versions | GET | `/v1/identities/{n}/versions` | public | Page canonical records, signatures, openings |
| history | GET | `/v1/identities/{n}/history` | public | Older version events and surrounding account transfers |
| version-proof | GET | `/v1/identities/{n}/versions/{k}/proof` | public | Inclusion proof for version k under current checkpoint |
| events | GET | `/v1/identities/{n}/events` | public | Takeover and publication-reconciliation events |
| takeovers | GET | `/v1/takeovers` | public | Account transfer requests involving a card |

## Organisations and public status

| id | Method | Path | Access | Summary |
|---|---|---|---|---|
| memberships | GET | `/v1/identities/{n}/orgs` | public | A person's memberships or an organisation's members |
| staff-roles | GET | `/v1/staff` | public | Veil's official organisation and staff role powers |
| moderation | GET | `/v1/identities/{n}/moderation` | public | Public status and moderation actions for a card |
| moderation-entries | GET | `/v1/moderation/entries` | public | Page public moderation, badge, badge-removal log entries |
| badge-catalogue | GET | `/v1/badges/catalogue` | public | Badge IDs, labels, assignment rules |
| card-badges | GET | `/v1/identities/{n}/badges` | public | A card's badges and removed-badge history |

## Share and embed

| id | Method | Path | Access | Summary |
|---|---|---|---|---|
| oembed | GET | `/oembed` | public | oEmbed for a Veil person, organisation or `/v/` URL |
| badge-image | GET | `/{kind}/{card}/badge.svg` | public | SVG status badge for README/profile/signature |
| card-image | GET | `/{kind}/{card}/card.png` | public | 1200x630 PNG social preview |
| logo | GET | `/{kind}/{n}/logo.{format}` | public | Currently published logo or photo |
| widget | GET | `/{kind}/{card}/embed` | public (iframe only) | Read-only card that verifies in the visitor's browser |
| embed-loader | GET | `/embed.js` | public | Turns `data-veil-card` / `data-veil-org` elements into card frames |
| preview-image | GET | `/preview.png` | public | General directory preview image |
| verify-page | GET | `/verify` | public (page) | Browser-side message check (data after `#` stays local) |
| verify-link | GET | `/v/{n}/{signature}` | public (page) | Shared verification link with server-made social preview |
| snippet-builder | GET | `/embed` | public (iframe) | Copy a link, badge or widget with live preview |

`kind` is `u` (person) or `o` (organisation).

## Transparency log

| id | Method | Path | Base | Access | Summary |
|---|---|---|---|---|---|
| log-state | GET | `/v1/log` | directory | public | Active log, checkpoint and witness state seen by the server |
| log-about | GET | `/{log}/` | log | public (page) | Log origin, verification key, daily request allowance, contact |
| log-checkpoint | GET | `/{log}/checkpoint` | log | public | Signed size and Merkle root |
| log-policy | GET | `/{log}/policy` | log | public | Log key, witness keys, quorum rule |
| log-witnesses | GET | `/{log}/witnesses` | log | public | Each witness's latest stored cosignature |
| log-hash-tiles | GET | `/{log}/tile/{level}/{index}` (also `.p/{width}`) | log | public | C2SP hash tiles for inclusion/consistency proofs |
| log-entry-tiles | GET | `/{log}/tile/entries/{index}` (also `.p/{width}`) | log | public | C2SP bundles of public log entries |

`{log}` is the log's path segment on `https://log.veil.rip`; read the origin from `GET /v1/log` or the log's `about` page (`https://log.veil.rip/`) rather than guessing it.

## Manage a card

All need the owner's device key unless noted. Never handle owner private keys (see `signed-requests.md`).

| id | Method | Path | Access | Summary |
|---|---|---|---|---|
| create-person | POST | `/v1/identities` | signed | Publish first record, signed by the key named in it |
| publish-person | POST | `/v1/identities/{n}/versions` | signed | Change keys, linked accounts, alias, other signed fields |
| create-organisation | POST | `/v1/organizations` | signed | First org record, signed by founder's active person key |
| publish-organisation | POST | `/v1/organizations/{n}/versions` | signed | Org change authorised by accepted owner/admin; role rules apply |
| salt-ticket | POST | `/v1/salt-tickets` | public-write | Server half of first-version salt, before device picks its half |
| start-link | POST | `/v1/links/start` | signed | Begin OAuth, email, domain or Fediverse proof |
| complete-link | POST | `/v1/links/{state}/complete` | signed | Complete a proof with the same key that started it |
| link-state | GET | `/v1/links/{state}` | private-code | Resume a proof with its secret state token |
| oauth-callback | GET | `/v1/links/callback/{platform}` | provider-callback | Redirect target for Veil's Discord/GitHub OAuth app |
| request-device | POST | `/v1/device-requests` | public-write | Temporary pairing code for a new device's public key |
| read-device-request | GET | `/v1/device-requests/{code}` | signed | Read a pairing request with an active person key |
| invite-accept | POST | `/v1/orgs/{n}/invites/{id}/accept` | signed | Invited person accepts; body has nonce and timestamp |
| invite-decline | POST | `/v1/orgs/{n}/invites/{id}/decline` | signed | Invited person declines; body has nonce and timestamp |
| cancel-takeover | POST | `/v1/takeovers/{id}/cancel` | signed | Current account holder cancels an open transfer |
| logo-preview-create | POST | `/v1/logo-previews` | signed | Validate a profile image/org logo before publishing |
| logo-preview-read | GET | `/v1/logo-previews/{hash}.{format}` | private-code | Temporary image via preview URL returned to creator |
| request-erasure | POST | `/v1/identities/{n}/erase` | signed | Active person key or org owner requests erasure (24h cancellation window) |
| cancel-erasure | POST | `/v1/identities/{n}/erase/cancel` | signed | Authorised key cancels pending erasure |
| submit-report | POST | `/v1/identities/{n}/reports` | signed | Active person key reports a card |

## Service reference

| id | Method | Path | Access | Summary |
|---|---|---|---|---|
| catalogue | GET | `/v1/integrations` | public | Guides and endpoint index as JSON (has `revision`) |
| catalogue-entry | GET | `/v1/integrations/{id}` | public | One guide or endpoint contract with examples |

Staff-only administration APIs exist but are outside the integration reference.

---

## Detailed contracts

Captured from the docs pages. Anything not listed here: use `scripts/veil.py doc <id>`.

### GET /v1/lookup
Exactly one query param. Errors: `400 invalid_parameter`, `404 not_found`.
- `discord` stable numeric user ID, 17-20 digits
- `github` numeric account ID (not login)
- `email` complete address
- `domain` exact domain, no trailing dot; IDNs as ASCII A-label
- `fediverse` complete `@user@server`
- `key` Ed25519 public key in hex, or full composite key in base64 (URL-encode)
- `fingerprint` 12 words (English or Italian) or 60 digits

Response: `identity` (short card), `match` (normalised query), `takeover` (pending transfer, when present). Then fetch the full card for its proof.

### GET /u/{card}.json and /o/{card}.json
`card` = permanent number or current alias. Without `.json`, send `Accept: application/json`. `/v1/identities/{n}` and `/v1/organizations/{n}` require the permanent number. Person card has `n, id, url, type, keys, links, proof, historyBefore`. Organisation JSON `type` is `organization`; includes members, logo, signed record, proof. Errors: `404 not_found`, `410 erased` (public tombstone), `503 log_unavailable` (person card).

### GET /v1/identities/{n}/summary
Fields: `n, url, name, initials, type, version, keys, orgs, badges, nameHidden, logo`. Errors `404`, `410`.

### GET /v1/aliases/{kind}/{alias}
`kind` is `u` or `o`. `alias`: 3-32 ASCII letters/digits/hyphen/underscore, starts with a letter, ends with letter or digit. Response: `available`, `status`, `identity` when claimed, `quarantineDays`, `reusableAt`, `reservedFor`. Availability does not reserve a name. Error `400 invalid_parameter`.

### GET /v1/platforms
Returns `platforms` with IDs, translated labels, methods, availability, organisation support. Use it to build account-linking choices.

### GET /v1/keys/{key}
`key` = 64 hex chars of an Ed25519 key (including the Ed25519 half of a composite key). Response: `identity, device, role, state, addedIn, revokedIn, validFrom, validUntil`; composite keys also give the full key. Errors `400`, `404`.

### GET /v1/keys/{key}/active-at
Query `t` = Unix seconds (default now; range 0..253402300799). Response: `at, active, reason, validFrom, validUntil`; reason is `active`, `not_yet_valid` or `revoked`.

### POST /v1/verify
No request-signing headers. JSON body, either:
- block mode: `block` (full pasted signature block, max 32768 chars), optional `at` (Unix seconds, default now). Cannot be combined with `key/message/signature/platform/subject`.
- raw mode: `key`, `message` (exact UTF-8 text), `signature` (Ed25519 hex; composite keys and signatures base64), optional pair `platform` + `subject` to check account ownership at `at`.

Response: `valid` (overall), `signatureOk`, `identity`, `device`, `keyState`, `account`, `reason`; block mode also returns the parsed block and matching key. Errors: `400 invalid_block`, `400 invalid_parameter`. Use `fetch(..., {credentials: "omit"})` from browsers.

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
