# Responses, headers and errors

Sources: [response guide](https://veil.rip/docs/errors) and [live contract JSON](https://veil.rip/v1/integrations). The guide lists 77 searchable error codes. Use the relevant endpoint's details when you implement a branch.

## Read a contract

```bash
python scripts/veil.py doc lookup
python scripts/veil.py doc verify-message
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
- Alias lookup can return `available: false` with a `claimed`, `reserved_name`, `publishing` or `quarantined` status.
- A full card can return `proof: null` when the server cannot verify the log at that moment. Keep it unverified.
- In format 2 a card can also return `index: null` (the server could not read or check the card's index bundle) or `index.statements: null` (it could not read or prove the chain of staff statements). Treat both as an unknown status, never as good standing.
- In format 2 the card's top-level `standing` is the server's view. The verified value is `index.value.standing`.
- A quota status call can return 200 with a positive `retryAfter`, even though ordinary requests would be blocked.

Read `Content-Type` before choosing a parser. Cards and API results use JSON. Images, scripts, signed log notes and tiles have other types. OAuth callbacks return HTML even on failure. Raw resources on the log host follow their own protocol, and proxies or the CDN can return HTML errors too.

Published PNG image URLs accept `size=64` or `size=128` for a smaller display thumbnail. Keep the current `v` hash from `logo.url`. Small images and animated APNGs may keep their original bytes. Omit `size` to get the exact published image. Use the original SVG and GIF URLs, which keep GIF and APNG animation. `size` on SVG or GIF, or any value other than 64 or 128, is `400 invalid_parameter`. A thumbnail is for display only: verify the original bytes against the hash in the signed version. [Image contract](https://veil.rip/docs/logo).

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

Branch on HTTP status and `error.code`. The English `error.message` can change and is meant for people. Verification reasons such as `bad_signature` or `unknown_key` are verdict data inside an HTTP 200, not the request error envelope.

| HTTP / code | Meaning | Next step |
|---|---|---|
| 400 `invalid_parameter`, `invalid_json` | Invalid input | Correct the named field or body |
| 400 `wrong_format` | The request or read belongs to the other log format | Read `format` in `GET /v1/log` (absent means 1) and use that format's shape |
| 401 `missing_signature`, `invalid_signature`, `stale_timestamp` | Request authentication failed | Correct the signing bytes, headers or clock, and sign with a fresh nonce |
| 401 `invalid_api_key` | The bearer key is unusable | Use an active key. Never retry anonymously by accident |
| 403 scope or authority error | The credential cannot perform the operation | Check the endpoint's scope or role |
| 404 `not_found` | No matching resource | Check the identifier. Temporary resources may have expired or been used |
| 409 conflict | State changed or an operation already happened | Read the current state before preparing another signed operation |
| 410 `erased` | The card was erased or removed | Stop accepting it as current authority and read its public receipt |
| 410 `proof_expired` | A temporary proof session expired | Start a fresh linking session |
| 413 `payload_too_large` | The body exceeds a limit | Shrink it. Card versions and logo previews take 3 MiB, API-key management 8 KiB, other signed requests 64 KiB |
| 422 validation error | Domain rules fail | Correct the input named in the message |
| 429 `rate_limited` | A request quota is exhausted | Wait at least `Retry-After` seconds |
| 429 `too_many_attempts` | A proof session exhausted its attempt limit | Start a fresh proof. Waiting for a request quota does not help |
| 503 `busy`, `log_unavailable` | Temporary service or log failure | Honour `Retry-After` when present and keep verification unsuccessful |

### Format 2 write errors

A card owner's signed writes on a format 2 log can also return these codes. The live catalogue lists the first three. The others come from the service and are not in the catalogue yet.

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

Format 2 also sets day limits per card: at most 16 keys, 32 linked accounts and 500 invitations added in 24 hours, pending versions included. Beyond that the answer is `429 rate_limited` with `Retry-After: 86400`.

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

The bundled client retries a read or message verification at most once for a transient 429 or 503. It waits the advertised interval only when that interval is at most 30 seconds, and longer waits return the original error. It never retries before `Retry-After`, and it does not retry a proof's `too_many_attempts` response. For a long-running integration, share a retry budget across workers and use bounded backoff with jitter.

After a signed write fails or times out, check the current card or operation state. Then prepare a fresh nonce and signature if another operation is still needed. The bundled client does not send signed writes.
