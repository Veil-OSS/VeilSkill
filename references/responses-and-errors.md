# Responses, headers and errors

Sources: [response guide](https://veil.pub/docs/errors) and [live contract JSON](https://veil.pub/v1/integrations). The guide lists 139 searchable error codes. Use the relevant endpoint's details when you implement a branch. The same contracts are in `GET /openapi.json`, where every error response shares the `Error` schema and lists its codes in `x-veil-error-codes`.

## Read a contract

```bash
python scripts/veil.py doc lookup
python scripts/veil.py doc verify-message
python scripts/veil.py doc verify-file
python scripts/veil.py doc rate-limit
python scripts/veil.py doc errors --lang it
```

The detail response has `revision`, `language` and `entry`. An endpoint entry includes:

| Metadata | Contents |
|---|---|
| `responses[]` | Success or redirect status, `contentType`, description, `fields` and selected examples |
| `responses[].fields[]` | Field `name`, descriptive `type` and meaning |
| `responseObjects[]` | Named nested types, their `typeName` and fields |
| `responseHeaders[]` | Header name, expected value or condition, description |
| `errorDetails[]` | HTTP `status`, stable `code`, `description`, recovery `action` and `scope` |
| `response`, `errors` | The earlier summary text and status and code strings |

A type containing `null` accepts a null value. `optional` means the field can be absent. Keep absent, null, zero and an empty array apart. Field descriptions can include literal identifiers in Markdown backticks. Static response examples have illustrative values, so replace them with the actual response.

`errorDetails.scope` tells endpoint errors, shared request errors and errors from an optional API key apart. Only the documented access modes apply. A published signed endpoint does not become an anonymous browser API.

## Interpret the result

HTTP 200 means the call was processed. Inspect its data before an authorisation decision:

- Verification can return `valid: false`. `reason` explains the negative verdict, and `signatureOk` alone is not enough.
- File verification can return `valid: false` with `reason: "hash_mismatch"` (the signature holds, the file is another one) or `"not_in_list"` (the signed list has no line for that name).
- A lookup by name can return a match with `stale: true`. The platform's last word on that name is more than 2 days old, so show the ID and the date `recorded` and do not open the card unasked.
- A lookup can return `alert`: the owner declared that account stolen, abandoned or moved. Show it first. It is the server's word until you check the alert's entry in the log.
- Alias lookup can return `available: false` with a `claimed`, `reserved_name`, `publishing` or `quarantined` status.
- A full card can return `proof: null` when the server cannot verify the log at that moment. Keep it unverified.
- In format 2 a card can also return `index: null` (the server could not read or check the card's index bundle) or `index.statements: null` (it could not read or prove the chain of staff statements). Treat both as an unknown status, never as good standing.
- In format 2 the card's top-level `standing` is the server's view. The verified value is `index.value.standing`.
- A card's `waiting` lists versions in the log that the witnesses have not cosigned yet. The card still shows the version before.
- A link's `check` (`ok`, `failing` or `unreachable`, with `lastOk`) is the server's periodic re-check of a proof. It is not signed.
- `GET /v1/canary` can return `status: "stale"` or `"none"`. Count the 35 days from the signed date yourself.
- A quota status call can return 200 with a positive `retryAfter`, even though ordinary requests would be blocked.

HTTP 202 on a signed write sent with `Prefer: respond-async` means the log holds the entry and the witnesses have not cosigned it yet. `witnessed` is false, and `publishedAt` and `checkpoint` are null. Read the version (or the statement) again every 2 seconds until `witnessed` is true. Until then the change is not published.

Read `Content-Type` before choosing a parser. Cards and API results use JSON. Images, scripts, key files (`text/plain`), contact files (`text/vcard`), Atom feeds, signed log notes and tiles have other types. Account addresses such as `/github/<login>` answer with a `302`. OAuth callbacks return HTML even on failure. Raw resources on the log host follow their own protocol, and proxies or the CDN can return HTML errors too.

Published PNG image URLs accept `size=64` or `size=128` for a smaller display thumbnail. Keep the current `v` hash from `logo.url`. Small images and animated APNGs may keep their original bytes. Omit `size` to get the exact published image. Use the original SVG and GIF URLs, which keep GIF and APNG animation. `size` on SVG or GIF, or any value other than 64 or 128, is `400 invalid_parameter`. A thumbnail is for display only: verify the original bytes against the hash in the signed version. [Image contract](https://veil.pub/docs/logo).

The client pretty-prints JSON and text. Use `--output` for the exact bytes of an image or tile. An HTTP error never overwrites that output file.

## Error envelope

```json
{
  "error": {
    "code": "invalid_parameter",
    "message": "Supply exactly one lookup parameter"
  }
}
```

Branch on HTTP status and `error.code`. The English `error.message` can change and is meant for people. Verification reasons such as `bad_signature`, `unknown_key` or `hash_mismatch` are verdict data inside an HTTP 200, not the request error envelope.

Some errors add fields beside `error`. A lookup's `404 not_found` and `409 ambiguous` carry `understood`, and `ambiguous` also carries `candidates`. A `410 erased` carries the public receipt.

Codes and documented fields stay. New ones can appear, so treat an unknown code by its HTTP status. A call that is going away answers with `Deprecation` and `Sunset` headers at least 90 days before, and the [changelog](https://veil.pub/docs/changelog) announces it.

The endpoints under `/oidc/` are the exception. They follow OAuth and answer `{"error": "...", "error_description": "..."}` with `Cache-Control: no-store`. [sign-in.md](sign-in.md) covers them.

| HTTP / code | Meaning | Next step |
|---|---|---|
| 400 `invalid_parameter`, `invalid_json` | Invalid input | Correct the named field or body |
| 400 `wrong_format` | The request or read belongs to the other log format | Read `format` in `GET /v1/log` (absent means 1) and use that format's shape |
| 401 `missing_signature`, `invalid_signature`, `stale_timestamp` | Request authentication failed | Correct the signing bytes, headers or clock, and sign with a fresh nonce |
| 401 `invalid_api_key` | The bearer key is unusable | Use an active key. Never retry anonymously by accident |
| 403 scope or authority error | The credential cannot perform the operation | Check the endpoint's scope or role |
| 400 `hash_needed`, `invalid_file_signature` | A file check without its hash, or a signature that cannot be read | Send the hash the signature uses, and the signature as the tool wrote it |
| 404 `not_found` | No matching resource | Check the identifier. Temporary resources may have expired or been used |
| 409 `ambiguous` | A lookup's readings lead to more than one card | Show every entry of `candidates` and let the reader choose |
| 409 conflict | State changed or an operation already happened | Read the current state before preparing another signed operation |
| 410 `erased` | The card was erased or removed | Stop accepting it as current authority and read its public receipt |
| 410 `proof_expired` | A temporary proof session expired | Start a fresh linking session |
| 413 `payload_too_large` | The body exceeds a limit | Shrink it. Card versions and logo previews take 3 MiB, API-key management 8 KiB, other signed requests 64 KiB |
| 422 validation error | Domain rules fail | Correct the input named in the message |
| 422 `file_needed` | The signature covers the file's own bytes, which the server never receives | Verify on `https://veil.pub/verify`, or sign a checksum list |
| 429 `rate_limited` | A request quota is exhausted | Wait at least `Retry-After` seconds |
| 429 `too_many_attempts` | A proof session exhausted its attempt limit | Start a fresh proof. Waiting for a request quota does not help |
| 429 `alert_quota`, `statement_quota` | The card published 10 alerts or 10 statements in 24 hours | Wait for the window to pass |
| 503 `busy`, `log_unavailable` | Temporary service or log failure | Honour `Retry-After` when present and keep verification unsuccessful |

### Format 2 write errors

A card owner's signed writes on a format 2 log can also return these codes. The live catalogue lists them all.

| HTTP / code | When |
|---|---|
| 400 `wrong_format` | A format 1 `record` sent to a format 2 log |
| 422 `label_mismatch` | `prev`, `body`, `auth` or `state` of the label is not what the chain, the body and the operations give |
| 422 `invalid_op` | An operation is unknown, malformed, not allowed for this card type or version, in the wrong list, or changes nothing |
| 422 `keys_limit` | The version would leave a person more than 64 active keys |
| 422 `authority_limit` | The version would leave an organisation more than 1024 owners and administrators (every staff role counts in the Veil organisation) |
| 422 `members_limit` | An invitation beyond 100,000 members and pending invitations |
| 422 `closing_required` | An erasure request without its signed closing entry |
| 422 `bad_entry` | The signed closing entry is malformed or stale. The message names the field |
| 409 `signer_stale` | `signer.n` of a signed entry is behind the signer's current version. Sign again |
| 409 `erase_pending` | The card has a pending erasure. Cancel it before publishing |

Format 2 also sets day limits per card: at most 16 keys, 32 linked accounts and 500 invitations added in 24 hours, pending versions included. Beyond that the answer is `429 rate_limited` with `Retry-After: 86400`. A card can have at most 4 versions waiting for the witnesses.

### Keys from elsewhere

Adding an SSH, OpenPGP, minisign, Ed25519 or ML-DSA public key to a person's card can return these codes, all `422` except the last.

| Code | When |
|---|---|
| `private_key_material` | The text holds a private key. Nothing is stored. Treat that key as exposed |
| `key_unsupported` | A type the directory does not hold: an SSH key on a security key (`sk-...`), ECDSA P-521, an SSH certificate, an OpenPGP key other than version 4 |
| `key_weak` | RSA under 2048 bits, DSA, or an RSA signature made with SHA-1 (`ssh-rsa`) |
| `key_expired`, `key_revoked` | The OpenPGP key or its signing subkey expired, or the key carries a revocation |
| `key_extra_packets` | The OpenPGP key still carries a photo, another person's certification or other material a card does not keep |
| `external_limit` | More than 16 keys on the card, or an operation over 16 KiB |
| `proof_invalid` | The key's signature over the challenge does not verify |
| `proof_stale` | The cited checkpoint was cosigned more than 7 days ago, or `proof.at` is older than 7 days or ahead of the server's clock |
| `proof_anchor` | The cited checkpoint is not from this log, lacks its signature or the quorum, or has another root at that size |
| `409 key_already_used` | Another card holds the key, or an Ed25519 key is a card's device key |

### Alerts, statements and Linked Roles

| HTTP / code | When |
|---|---|
| 409 `alert_in_force`, `alert_not_in_force` | The account already has that alert, or `regained` was sent for an account without one |
| 422 `account_not_linked` | The alert names an account the card does not hold |
| 409 `already_retracted` | The statement was retracted before |
| 422 `invalid_statement`, `bad_entry` | The statement or its log entry is malformed. The message names the field |
| 404 `linked_roles_off` | This server has Linked Roles turned off |
| 422 `no_discord_link` | The card has no verified Discord account |
| 409 `discord_account_alert` | The card declared that Discord account stolen, abandoned or moved |
| 409 `not_in_good_standing` | The card is closing, has a takeover open or its name is hidden |
| 403 `veil_suspended` | The Veil staff suspended the card |
| 429 `too_many_starts` | More than 20 connections started for the card in an hour. Every start counts |

### Pictures

`422 invalid_logo` starts its message with a reason. Since 27 October 2026 a new version names its picture by hash and sends the bytes beside it, which adds three reasons:

- `inline`: the version carries the image itself (`{type, data}`) instead of `{type, sha256, size}`.
- `missing`: a new picture arrived without its bytes (`pictureData` in format 2, `logoData` in format 1).
- `mismatch`: the bytes do not have the declared size or SHA-256, or arrived for a version without a picture.

Malformed bytes give `base64`, `empty` or `too_large`. The other reasons describe the image itself: `shape`, `type`, `not_png`, `png_size`, `png_unreadable`, `not_gif`, `gif_size`, `gif_unreadable`, `not_svg`, `svg_unreadable`, `svg_doctype`, `svg_element`, `svg_attribute`, `svg_event`, `svg_href`, `svg_url`, `svg_style`, `svg_size`, `svg_too_complex`.

### Erased cards

A 410 `erased` response adds `erased`, `n`, `closedAt`, `token` and `logIndexes`. A staff removal adds `removed`, `category` and `logIndex`. On a format 2 log it also carries `closed` (the signed closing entry with its inclusion proof and an optional `signerN`), `format`, `id`, `type`, `index` and `authority`, so a reader can check the closing. [format-2.md](format-2.md#closings) explains the check. The receipt is historical evidence and does not restore the card's authority.

## Caching and retries

Card JSON (`/u/{card}.json`, `/o/{card}.json`, `/v1/identities/{n}`, `/v1/organizations/{n}`, also by alias) carries a weak `ETag` and `Cache-Control: private, no-cache, must-revalidate`. Send the tag in `If-None-Match`. The server rebuilds the card with its current visibility, moderation and proof, and answers `304` with no body only when the bytes are identical. Keep cards in a private cache, never a shared one.

The documentation catalogue and entry API return ETags and permit five minutes of public caching. A full page of `GET /v1/identities/{n}/labels` never changes and is served as immutable. A 304 has no body and means you reuse the representation stored with that tag (and that language, for the catalogue). It does not refresh any verification: freshness of the checkpoint still depends on the current time. An API-key response uses `no-store`, so do not persist it in a shared cache.

Use `--include-headers` to print the HTTP status and response headers to stderr without changing the body on stdout. `--if-none-match` sends a validator. A 304 does not overwrite `--output`.

The bundled client retries a read or a verification at most once for a transient 429 or 503. It waits the advertised interval only when that interval is at most 30 seconds, and longer waits return the original error. It never retries before `Retry-After`, and it does not retry a proof's `too_many_attempts` response. For a long-running integration, share a retry budget across workers and use bounded backoff with jitter.

After a signed write fails or times out, check the current card or operation state. Then prepare a fresh nonce and signature if another operation is still needed. The bundled client does not send signed writes.
