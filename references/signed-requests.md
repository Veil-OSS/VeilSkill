# Device-signed requests

Source: https://veil.rip/docs/signed-requests plus the per-endpoint pages and the format 2 contract. Read this when preparing a card change, a signed pairing read or API-key management. Public reads and `POST /v1/verify` do not need a device signature.

## Ground rules

- An **active authorised device key** with the role its endpoint requires signs each management request. Never ask the user to paste a private key, never generate or store one on their behalf, and never send one to Veil. Prepare the unsigned version and request bytes, explain what must be signed, and let the owner sign on their own device.
- Public CORS does not open device-signing headers to other websites. External clients use local or server flows. Veil's own pages sign with the enrolled browser device.
- A publication is ready only after its log entry appears in a witnessed checkpoint. If a request times out, read the card's current versions before sending again.
- Check `format` in `GET /v1/log` before you build a version. veil.rip is on format 2 since 28 October 2026, and a format 1 `record` sent there answers `400 wrong_format`.

## Request signature

This layer is the same in both formats. Headers: `X-Public-Key`, `X-Signature`. Ed25519 keys and signatures are hex. Composite keys and signatures are base64 and add `X-Signature-Alg: mldsa65-ed25519`.

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

Do not append a newline after the final timestamp in signed GET bytes.

The JSON body of a POST, PATCH or DELETE carries `nonce` (fresh, single use, 16 to 128 characters of letters, digits, `_`, `-`) and `timestamp` (Unix **milliseconds**, within 2 minutes of the server clock). The request signature covers the method, the exact path and the exact body, so sign the bytes you actually send.

Limits: 10 signed writes per minute per key, 30 writes per minute per IP, and separate budgets for account-linking steps.

## API-key management

A bearer key cannot authorise these calls. A person manages their own card, and an organisation requires an accepted owner. Signed GET requests inspect the account, keys and private receipts. `POST /v1/developer/accounts/{n}/keys` creates a key and `DELETE /v1/developer/accounts/{n}/keys/{id}` revokes it for good.

Creation takes `label`, optional `scopes` and `expiresInDays`, plus the common nonce and timestamp. HTTP 201 returns `key` metadata and `secret` once. Management writes accept at most 8 KiB and reject unknown fields. These actions produce private signed receipts and do not publish an identity version or a public log entry. Read [api-keys.md](api-keys.md) for the response shapes and lifecycle.

## A version in format 2

`POST /v1/identities`, `POST /v1/identities/{n}/versions`, `POST /v1/organizations` and `POST /v1/organizations/{n}/versions` take this body, signed as a request by the key that signs the label (`X-Public-Key`):

```json
{"label": "{\"auth\":[...],\"body\":\"<body hash>\",\"identity\":\"<token>\",\"n\":2,\"prev\":\"<label hash of version 1>\",\"state\":\"<state root>\",\"time\":1793214324,\"v\":2}",
 "body": "{\"ops\":[...],\"salt\":\"<32 bytes, base64>\",\"v\":2}",
 "signature": "<signature of the label>",
 "pictureData": "<only when the picture changes>",
 "nonce": "...", "timestamp": 1793214324000}
```

- `label` and `body` are the canonical texts, the exact bytes that are hashed and signed. The server re-encodes and compares, and refuses a text that is not in canonical form (`invalid_record`). It also reads a JSON object and encodes it canonically, but the signature still has to match those canonical bytes.
- `signature` signs `"veil-rubrica:identity-version:v2\n"` + label, in hex for Ed25519 and base64 for a composite key.
- Version 1 also needs `clientSalt` and `saltTicket` (below).
- The label has `auth`, `body`, `identity`, `n`, `prev`, `state`, `time`, `v` and, for an organisation only, `signer`. `identity` is base64url of a fresh 16-byte token in version 1 and never changes. `n` starts at 1 and grows by one. `prev` is `null` for version 1, then the label hash of the previous version in standard base64. `time` is Unix **seconds**, within 5 minutes of the server clock. `v` is the integer 2.
- `label.body` is `SHA-256("veil-rubrica:body:v2\n" + body)` in standard base64.
- The body has `ops`, `salt` and `v`. `salt` is 32 random bytes in standard base64. The device draws it for every version after the first.
- `label.state` is the state root after the version. Compute it from the new state and the body salt as [format-2.md](format-2.md#hashes-and-encodings) shows. `GET /v1/identities/{n}/sets/{set}/path?key=` gives the path of one item, so you can update a set root without downloading the whole set.

`auth` holds the operations that change who can sign, in the order they apply, and the body holds all the others. The server applies `auth` first, then `ops`. An authority operation in the body, or another operation in `auth`, is `invalid_op`. Each list holds at most 1000 operations.

### Person operations

| List | Operation | Who may sign |
|---|---|---|
| `auth` | `{"op":"addKey","key","alg","role"}`, `role` is `device` or `recovery` | Any active key adds a device. A device registers a recovery key only while none is active, otherwise only the recovery key replaces itself |
| `auth` | `{"op":"revokeKey","key"}` | Any active key revokes a device while another key stays active. Only the recovery key revokes the recovery key, and only while replacing itself in the same version |
| body | `{"op":"device","key","device"}` | Any active key. Names or renames a key. Every key that `auth` adds needs one in the same body |
| body | `{"op":"name","name"}` | Any active key |
| body | `{"op":"alias","alias"}`, `alias` is a lowercase name or `null` to release it | Any active key |
| body | `{"op":"picture","picture"}`, `picture` is `{type, sha256, size}` or `null` | Any active key |
| body | `{"op":"addLink","platform","subject","display","grant"}` | Any active key, with the grant string from the linking APIs |
| body | `{"op":"removeLink","platform","subject"}` | Any active key |
| body | `{"op":"joinOrg","org","role","grant"}` | Any active key, with the grant from accepting the invitation |
| body | `{"op":"leaveOrg","org"}` | Any active key |

### Organisation operations

An organisation has no keys of its own. A member signs, and `label.signer` names that member's card and current version: `{"identity": "<member token>", "n": <member's current version>}`. The signing key must be active in that version, which must still be the member's latest when the organisation's version enters the log. The body never carries `signer`.

| List | Operation | Who may sign |
|---|---|---|
| `auth` when the role before or after is `owner` or `admin` (any staff role in the Veil organisation), otherwise body | `{"op":"invite","member","role"}` | Owners. Administrators for roles below owner |
| same rule | `{"op":"role","member","role"}` | Owners |
| same rule | `{"op":"remove","member"}` | Owners. Administrators for members below owner |
| body | `{"op":"name","name"}`, `{"op":"picture","picture"}` | Owners and administrators |
| body | `{"op":"alias","alias"}` | Owners |
| body | `{"op":"addLink",...}`, `{"op":"removeLink",...}` | Owners and administrators |

A role change takes effect at once, with no new acceptance. An organisation always keeps at least one accepted owner (`last_owner`). Roles are `owner`, `admin`, `moderator`, `support` and `member`.

### Version 1

- A person: `auth` holds exactly one `addKey` with role `device`, and that key signs. The body holds `name` and the `device` op for that key, plus optional `picture` and `alias`. Links arrive later, with their proofs.
- An organisation: `auth` is exactly `[{"member": "<founder token>", "op": "invite", "role": "owner"}]`, the founder is `label.signer`, and an active key of the founder signs. The body holds `name` and an optional `picture`.
- `clientSalt` and `saltTicket` are required. Get a ticket with `POST /v1/salt-tickets` (`{"ticket", "serverSalt", "expiresAt", "format": 2}`, valid 10 minutes, single use). `serverSalt` is 16 bytes in hex. Draw 16 bytes of your own and send them as `clientSalt` in base64url (22 characters). `body.salt` is the server half followed by your half. The label names the body by hash, so you know the whole salt before you sign.
- The label hash of version 1, in hex, is the card's `id`. Check that the `id` in the response matches.

### Pictures

A picture is named by hash: `{"type": "image/png", "sha256": "<64 lowercase hex>", "size": <bytes>}`. `type` is `image/png` (APNG included), `image/gif` or `image/svg+xml`. `size` is 1 to 2,097,152 bytes (2 MiB). PNG and GIF are at most 512 by 512 pixels, and SVG follows a closed list of elements and attributes. When a version brings a new picture, send its bytes as `pictureData`, standard padded base64 on one line. An unchanged picture needs no bytes, and bytes sent anyway must match. `{"op":"picture","picture":null}` removes it. Check an image first with `POST /v1/logo-previews`, which still takes the whole image as `{"logo": {"type", "data"}}`.

### Server checks and limits

The server checks, in order: shape, `identity`, `n`, `prev` and time, then the body hash, then authority (the signing key is active for a person, and for an organisation the member in `signer` has the role, has accepted and signs with a key active in version `signer.n`), then the label signature, then the operations on the current state with their grants, then the placement of each operation, then the state root and finally the picture. A key that cannot sign for the card never gets its operations read.

- At most 64 active keys per person (`422 keys_limit`) and 1024 owners and administrators per organisation (`422 authority_limit`). A revocation or removal in the same version frees the place.
- At most 100,000 members and pending invitations per organisation (`422 members_limit`).
- Per card in 24 hours: 16 keys, 32 linked accounts and 500 invitations added, pending versions included. Beyond that, `429 rate_limited` with `Retry-After: 86400`. A card founds at most 3 organisations a day.
- A version that changes nothing is `invalid_op` or `invalid_record`. The one exception is the empty version, with `auth` and `ops` both empty, which moves the card's latest version, for example after cancelling an erasure.
- While an erasure is pending the card cannot publish (`409 erase_pending`).
- An organisation's version waits (`409 version_conflict`) while the signing member's card has its own version pending in the log, and a person's version waits while an organisation version signed by that person is pending.
- The request body may be up to 3 MiB on these four routes.

Canonical JSON: object keys sorted by UTF-16 code units, array order preserved, no whitespace outside strings, only integers in the JavaScript safe range, UTF-8 strings already in NFC, booleans and null. Do not normalise or trim signed text after signing. The outer request body need not be canonical.

## A version in format 1

The earlier log `log.veil.rip/test-1` is frozen, so this shape matters only to read its history or for another server that runs format 1. A format 1 version is one `record` signed over `"veil-rubrica:identity-version:v1\n"` + its canonical JSON, sent as `{record, signature, logoData?, nonce, timestamp}` with optional `clientSalt` and `saltTicket`. The record has `v: 1`, `identity`, `n`, `prev` (the previous commitment in base64), `name`, `time`, optional `type` and `alias`, the full `keys` history (`key, alg, device, role, since, revoked`) and `links` history (`platform, subject, display, since, removed, grant`), and `orgs` or `members`. Since 27 October 2026 a picture is `logo: {type, sha256, size}` with the bytes in `logoData`. Versions published earlier carry `{type, data}` and stay valid.

## Typical flows in format 2

**New card:** `POST /v1/salt-tickets` (public-write), draw the device's salt half, build the version 1 body and label, let the owner sign the label and the request, then `POST /v1/identities` with `label, body, signature, clientSalt, saltTicket, nonce, timestamp` (and `pictureData` with a picture). Success is `201` with `n, id, url, token, version, commitment, logIndex, publishedAt, checkpoint`.

**Link an account:** `POST /v1/links/start` with `{identity, platform, subject?, method?}` returns `201 {state, method, expiresAt, challenge}`. Keep `state` private. OAuth platforms redirect through `GET /v1/links/callback/{platform}`. Then `POST /v1/links/{state}/complete` with the same key returns the grant, and the next version carries `{"op":"addLink","platform","subject","display","grant"}`. Starting or completing a proof does not add the account by itself.

**Add a device:** the new device calls `POST /v1/device-requests`, an existing device reads `GET /v1/device-requests/{code}` (signed GET) and publishes a version with `addKey` in `auth` and the matching `device` op in the body.

**Join an organisation:** after the organisation's version invites the person, `POST /v1/orgs/{n}/invites/{id}/accept` returns the grant, and the person's next version carries `{"op":"joinOrg","org","role","grant"}`. `POST /v1/orgs/{n}/invites/{id}/decline` refuses.

**Erasure:** `POST /v1/identities/{n}/erase` with `time`, `signature` (over `"veil-rubrica:erase:v1\n"` + token + `"\n"` + time), `closing`, `nonce` and `timestamp`. `closing` is `{"text": "<canonical entry without signature>", "signature": "..."}` for the entry `{"key","kind":"closed","latest","signer":{"identity","n"},"time","token","v":2}`, signed over `"veil-rubrica:close-entry:v2\n"` + text by the same key as the request. `latest` is the label hash of `current.label`. `signer` is the card itself for a person, or the owner's card for an organisation. Without it the answer is `422 closing_required`. There is a 24-hour cancellation window. `POST /v1/identities/{n}/erase/cancel` cancels it, and the device then publishes an empty version so that the closing signed earlier no longer counts.

## Write errors

`422 invalid_op`, `422 label_mismatch`, `422 invalid_record`, `422 invalid_record_signature`, `401 missing_signature`, `403 signer_not_authorised`, `409 version_conflict` (read the versions again, rebuild and sign again), `409 salt_ticket_invalid`, `400 wrong_format`, `503 log_unavailable`, and the format 2 codes in [responses-and-errors.md](responses-and-errors.md#format-2-write-errors). Read the endpoint's `errorDetails` for recovery. After a timeout, check the current card or operation state before preparing another signed request.

For exact per-endpoint bodies run `python scripts/veil.py doc <id>` (for example `publish-person` or `complete-link`). Their notes cover format 2, while their body tables still list the format 1 fields first.
