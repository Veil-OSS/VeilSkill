# Responses, headers and errors

Sources: [response guide](https://veil.rip/docs/errors) and [live contract JSON](https://veil.rip/v1/integrations). The guide contains 74 searchable error codes; use the relevant endpoint's details when implementing a branch.

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
| `responses[]` | Success/redirect status, `contentType`, description, `fields` and selected examples |
| `responses[].fields[]` | Field `name`, descriptive `type` and meaning |
| `responseObjects[]` | Named nested types, their `typeName` and fields |
| `responseHeaders[]` | Header name, expected value or condition, description |
| `errorDetails[]` | HTTP `status`, stable `code`, `description`, recovery `action` and `scope` |
| `response`, `errors` | Retained summary text and status/code strings |

A type containing `null` accepts a null value. `optional` means the field can be absent. Preserve the difference between absent, null, zero and an empty array. Field descriptions can include literal identifiers in Markdown backticks. Static response examples have illustrative values; replace placeholders with the actual response from the request.

`errorDetails.scope` distinguishes endpoint-specific errors, shared request errors and errors from using an optional API key. Only documented access modes apply; a published signed endpoint does not become an anonymous browser API.

## Interpret the result

HTTP 200 means the call was processed. Inspect its data before making an authorisation decision:

- Verification can return `valid: false`. `reason` explains the negative verdict; `signatureOk` alone is insufficient.
- Alias lookup can return `available: false` with a claimed, reserved, publishing or quarantined status.
- A full card can return `proof: null` when current log verification is unavailable. Keep it unverified.
- A quota status call can return 200 with a positive `retryAfter`, even though ordinary requests would be blocked.

Read `Content-Type` before choosing a parser. Cards and API results use JSON; images, scripts, signed log notes and tiles have other types. OAuth callbacks return HTML even on failure. Raw resources on the log host use their own protocol. Proxies or the CDN can return HTML errors too.

Published PNG image URLs accept `size=64` or `size=128` for a smaller display thumbnail. Keep the current `v` hash from `logo.url`. Small images and animated APNGs may retain their original bytes; omit `size` to obtain the exact published image. Use the original SVG/GIF URLs; GIF and APNG animation is preserved. A derivative is presentation data; verify the original bytes in the signed record. [Image contract](https://veil.rip/docs/logo).

The client pretty-prints JSON and text. Use `--output` for exact bytes of an image or tile; an HTTP error never overwrites that output file.

## Error envelope

```json
{
  "error": {
    "code": "invalid_parameter",
    "message": "Supply exactly one lookup parameter"
  }
}
```

Branch on HTTP status and `error.code`. The English `error.message` can change and is for people. Verification reasons such as `bad_signature` or `unknown_key` are HTTP-200 verdict data, not the request error envelope.

| HTTP / code | Meaning | Next step |
|---|---|---|
| 400 `invalid_parameter`, `invalid_json` | Invalid input | Correct the named field or body |
| 401 `missing_signature`, `invalid_signature`, `stale_timestamp` | Request authentication failed | Correct signing bytes, headers or clock; sign with a fresh nonce |
| 401 `invalid_api_key` | Bearer key is unusable | Use an active key; never silently retry anonymously |
| 403 scope or authority error | The credential cannot perform the operation | Check the endpoint's scope or role |
| 404 `not_found` | No matching resource | Check the identifier; temporary resources may be expired or used |
| 409 conflict | State changed or an operation already happened | Read current state before preparing another signed operation |
| 410 `erased` | Card was erased or removed | Stop accepting it as current authority and read its public receipt |
| 410 `proof_expired` | Temporary proof session expired | Start a fresh linking session |
| 413 `payload_too_large`, 422 validation error | Body exceeds a limit or domain rules fail | Correct input; API-key management bodies are limited to 8 KiB |
| 429 `rate_limited` | A request quota is exhausted | Wait at least `Retry-After` seconds |
| 429 `too_many_attempts` | A proof session exhausted its attempt limit | Start a fresh proof; waiting for a request quota is insufficient |
| 503 `busy`, `log_unavailable` | Temporary service or log failure | Honour `Retry-After` when present and keep verification unsuccessful |

A 410 `erased` response adds `erased`, `n`, `closedAt`, `token` and `logIndexes`. Staff removal can add `removed`, `category` and `logIndex`. This is historical evidence and does not restore the card's authority.

## Caching and retries

The documentation catalogue and entry API return ETags and permit five minutes of public caching. Send the received ETag in `If-None-Match`; 304 has no body and requires reusing the representation stored with that tag and language. An API-key response uses `no-store`, so do not persist it in a shared cache.

Use `--include-headers` to print HTTP status and response headers to stderr without changing the response body on stdout. `--if-none-match` sends a validator. A 304 does not overwrite `--output`.

The bundled client retries a read or message verification at most once for a transient 429/503. It waits the advertised interval only when that interval is at most 30 seconds; longer waits return the original error. It never retries before `Retry-After`, and does not retry a proof's `too_many_attempts` response. For a long-running integration, share a retry budget across workers and use bounded backoff with jitter.

Check the current card or operation state after a signed write fails or times out. Then prepare a fresh nonce and signature if another operation is still needed. The bundled client does not send signed writes.
