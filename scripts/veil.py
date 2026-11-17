#!/usr/bin/env python3
"""
Veil client: stdlib-only CLI for every public Veil read and for verification of
signed messages, files and releases. It covers lookups by ID or by name, the reads
of log format 2 (authority, statements, labels, members, set paths), account alerts,
card statements, public keys from elsewhere and the canary.
Signed writes are intentionally NOT implemented: they need the owner's private
device key, which this tool never touches. A file is hashed here and only its
hash is sent.

-- ZephyrVerrater
"""
import argparse
import base64
import hashlib
import json
import ipaddress
import math
import os
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import NamedTuple
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://veil.pub"
UA = "veil-skill-client/1.3"
MAX_WAIT = 30


class Response(NamedTuple):
    status: int
    body: bytes
    headers: dict


def origin(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username is not None or parsed.password is not None:
        raise ValueError("Use an HTTP(S) URL without embedded credentials")
    return parsed.scheme, parsed.hostname.lower(), parsed.port or (443 if parsed.scheme == "https" else 80)


def key_transport(url):
    scheme, host, _ = origin(url)
    if scheme == "https" or host == "localhost":
        return
    try:
        if ipaddress.ip_address(host).is_loopback:
            return
    except ValueError:
        pass
    raise ValueError("API keys require HTTPS; HTTP is supported only on loopback")


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urljoin(req.full_url, newurl)
        if req.has_header("Authorization"):
            key_transport(target)
            if origin(target) != origin(req.full_url):
                raise ValueError("Refusing to send an API key to another origin")
        return super().redirect_request(req, fp, code, msg, headers, target)


def retry_delay(value):
    if value is None:
        return 2
    try:
        wait = float(value)
        if not math.isfinite(wait):
            return None
    except (ValueError, OverflowError):
        try:
            wait = parsedate_to_datetime(value).timestamp() - time.time()
        except (ValueError, TypeError, OverflowError):
            return None
    if wait < 0:
        wait = 0
    return wait if wait <= MAX_WAIT else None


def request(method, path, body=None, base=BASE, dry_run=False, api_key=None, if_none_match=None):
    origin(base)
    if path.startswith("/") and not path.startswith("//"):
        url = base.rstrip("/") + path
    else:
        url = path
    origin(url)
    data = None
    headers = {"Accept": "application/json", "User-Agent": UA}
    if api_key is not None:
        if origin(url) != origin(base):
            raise ValueError("Refusing to send an API key outside the configured API origin")
        key_transport(url)
        if not api_key or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in api_key):
            raise ValueError("The API-key environment variable must contain one nonempty credential")
        headers["Authorization"] = "Bearer " + api_key
    if if_none_match is not None:
        headers["If-None-Match"] = if_none_match
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if dry_run:
        preview = dict(headers)
        if "Authorization" in preview:
            preview["Authorization"] = "Bearer [redacted]"
        print(json.dumps({"method": method, "url": url, "headers": preview, "body": body}, indent=2))
        return None
    opener = urllib.request.build_opener(SafeRedirect())
    read_only = method == "GET" or (method == "POST" and urllib.parse.urlsplit(url).path == "/v1/verify")
    for attempt in (0, 1):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with opener.open(req, timeout=30) as r:
                return Response(r.status, r.read(), {k.lower(): v for k, v in r.headers.items()})
        except urllib.error.HTTPError as e:
            with e:
                result = Response(e.code, e.read(), {k.lower(): v for k, v in e.headers.items()})
            try:
                code = json.loads(result.body).get("error", {}).get("code")
            except (ValueError, AttributeError):
                code = None
            transient = code in (None, "rate_limited", "busy", "log_unavailable")
            if read_only and result.status in (429, 503) and transient and attempt == 0:
                wait = retry_delay(result.headers.get("retry-after"))
                if wait is not None:
                    time.sleep(wait)
                    continue
            return result


def emit(result, output=None, include_headers=False):
    if result is None:
        return
    status, body, headers = result
    if include_headers:
        print("HTTP {}".format(status), file=sys.stderr)
        for name, value in sorted(headers.items()):
            print("{}: {}".format(name, value), file=sys.stderr)
    if status >= 400:
        if not include_headers:
            print("HTTP {}".format(status), file=sys.stderr)
        if "retry-after" in headers and not include_headers:
            print("Retry-After: " + headers["retry-after"], file=sys.stderr)
        try:
            text = json.dumps(json.loads(body), indent=2, ensure_ascii=False)
        except ValueError:
            text = body.decode("utf-8", "replace")
        print(text, file=sys.stderr)
        raise SystemExit(1)
    if status == 304:
        return
    if output is not None:
        Path(output).write_bytes(body)
        return
    if not body:
        return
    media = headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if media.startswith(("image/", "audio/", "video/")) or media == "application/octet-stream":
        raise ValueError("Use --output FILE to save this binary response without changing its bytes")
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("Use --output FILE to save this response without changing its bytes") from None
    try:
        text = json.dumps(json.loads(text), indent=2, ensure_ascii=False)
    except ValueError:
        pass
    print(text)


def seg(value):
    return urllib.parse.quote(str(value), safe="")


def q(**params):
    clean = {k: v for k, v in params.items() if v is not None}
    return ("?" + urllib.parse.urlencode(clean)) if clean else ""


LOOKUP = ("account", "discord", "github", "email", "domain", "fediverse", "key", "fingerprint")
HASHES = ("sha256", "sha512", "blake2b512")


def file_hash(path, alg):
    h = hashlib.new("blake2b" if alg == "blake2b512" else alg)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def signature_text(path):
    data = Path(path).read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return base64.b64encode(data).decode("ascii")


def main():
    p = argparse.ArgumentParser(description="Veil (veil.pub) public API client")
    p.add_argument("--base", default=BASE, help="override base URL")
    p.add_argument("--dry-run", action="store_true", help="preview the request with credentials redacted")
    p.add_argument("--api-key-env", metavar="NAME", help="read an optional bearer key from this environment variable")
    p.add_argument("--include-headers", action="store_true", help="write HTTP status and response headers to stderr")
    p.add_argument("--if-none-match", metavar="ETAG", help="send a conditional GET validator")
    p.add_argument("--output", metavar="FILE", help="save exact response bytes after a successful request")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("lookup", help="find a card by exactly one account, name, key or fingerprint")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--account", help="anything typed: a username, login, address, profile URL, key, fingerprint, card or alias")
    for name in LOOKUP[1:]:
        g.add_argument(f"--{name}")

    s = sub.add_parser("card", help="full person card + proof"); s.add_argument("card")
    s = sub.add_parser("org", help="full organisation card + proof"); s.add_argument("card")
    s = sub.add_parser("summary", help="small metadata, no proof"); s.add_argument("n")
    s = sub.add_parser("alias", help="check/resolve an alias"); s.add_argument("kind", choices=["u", "o"]); s.add_argument("alias")
    sub.add_parser("platforms", help="supported account platforms")
    s = sub.add_parser("key", help="who holds this key"); s.add_argument("key")
    s = sub.add_parser("key-active", help="was key active at time t"); s.add_argument("key"); s.add_argument("--t", type=int)

    s = sub.add_parser("verify", help="verify a signature block, a raw signature, or a signature over a file or release")
    s.add_argument("--block"); s.add_argument("--block-file")
    s.add_argument("--at", type=int, help="trusted publication time, Unix seconds")
    s.add_argument("--key"); s.add_argument("--message"); s.add_argument("--signature")
    s.add_argument("--platform"); s.add_argument("--subject")
    s.add_argument("--signature-file", help="file mode: the .sig, .asc, .minisig, clear-signed text or Veil block")
    s.add_argument("--file", help="file mode: hash this file here; only the hash and the name are sent")
    s.add_argument("--hash", choices=HASHES, default="sha256", help="the hash --file computes (default sha256)")
    for name in HASHES:
        s.add_argument(f"--{name}", help="file mode: the file's hash in hex, computed by you")
    s.add_argument("--name", help="file mode: the file's name, as a checksum list writes it")
    s.add_argument("--list-file", help="file mode: the checksum list a detached signature covers")
    s.add_argument("--format", choices=["ssh", "pgp", "minisign", "veil"])
    s.add_argument("--card", help="file mode: the signer's card number or alias")

    s = sub.add_parser("versions", help="signed versions"); s.add_argument("n")
    s.add_argument("--after", type=int); s.add_argument("--limit", type=int); s.add_argument("--latest", action="store_true")
    s = sub.add_parser("history", help="card history"); s.add_argument("n"); s.add_argument("--before", type=int); s.add_argument("--limit", type=int)
    s = sub.add_parser("proof", help="inclusion proof for a version"); s.add_argument("n"); s.add_argument("k")
    s = sub.add_parser("events", help="account events"); s.add_argument("n"); s.add_argument("--after", type=int)
    s = sub.add_parser("takeovers", help="account transfers"); s.add_argument("identity")
    s = sub.add_parser("version", help="format 2: one version whole"); s.add_argument("n"); s.add_argument("v")
    s = sub.add_parser("authority", help="format 2: versions that changed who can sign"); s.add_argument("n")
    s.add_argument("--after", type=int); s.add_argument("--limit", type=int)
    s = sub.add_parser("statements", help="format 2: next page of staff statements (follow index.statementsNext)"); s.add_argument("n")
    s.add_argument("--from", dest="start", type=int, required=True, help="prev of the last statement already read")
    s.add_argument("--size", type=int, required=True, help="checkpoint size of the card's index bundle")
    s = sub.add_parser("labels", help="format 2: the chain of labels"); s.add_argument("n")
    s.add_argument("--after", type=int); s.add_argument("--limit", type=int)
    s = sub.add_parser("members", help="format 2: one page of an organisation's members"); s.add_argument("n")
    s.add_argument("--prefix", help="standard base64 of the prefix bytes"); s.add_argument("--bits", type=int)
    s = sub.add_parser("set-path", help="format 2: sparse Merkle path of one state item"); s.add_argument("n")
    s.add_argument("set", choices=["keys", "links", "orgs", "members"])
    s.add_argument("--key", required=True, help="public key, platform and subject joined by a newline, or a card token")
    s = sub.add_parser("alerts", help="a card's account alerts (stolen, abandoned, moved, regained)"); s.add_argument("n")
    s = sub.add_parser("card-statements", help="a card's own signed statements"); s.add_argument("kind", choices=["u", "o"]); s.add_argument("card")
    s.add_argument("--before", type=int); s.add_argument("--limit", type=int)
    s = sub.add_parser("statement", help="one statement or alert by its log position"); s.add_argument("id")
    s = sub.add_parser("keys-file", help="a person's public keys from elsewhere as a text file"); s.add_argument("card")
    s.add_argument("--format", choices=["authorized_keys", "allowed_signers", "minisign", "pgp"])
    s.add_argument("--fp", help="keep one key by fingerprint or public key")
    sub.add_parser("canary", help="the warrant canary and its history")
    sub.add_parser("linked-roles", help="Discord Linked Roles: availability and the facts a server can ask for")
    sub.add_parser("log", help="directory log state")
    s = sub.add_parser("catalogue", help="machine-readable endpoint index")
    s.add_argument("--lang", choices=["en", "it"])
    sub.add_parser("openapi", help="the same reference as an OpenAPI 3.1 document")
    sub.add_parser("quota", help="inspect shared quotas without spending the primary allowance; requires --api-key-env")
    s = sub.add_parser("get", help="GET any public path, e.g. /v1/identities/1/orgs"); s.add_argument("path")
    s = sub.add_parser("doc", help="live contract for one endpoint or guide ID"); s.add_argument("id")
    s.add_argument("--lang", choices=["en", "it"])

    a = p.parse_args()
    b, d = a.base, a.dry_run
    if a.cmd == "quota" and not a.api_key_env:
        p.error("quota requires --api-key-env NAME")
    api_key = None
    if a.api_key_env:
        api_key = os.environ.get(a.api_key_env)
        if not api_key:
            if a.dry_run:
                api_key = "redacted-preview"
            else:
                p.error("Set the named API-key environment variable before making the request")

    def send(method, path, body=None):
        try:
            result = request(method, path, body, base=b, dry_run=d, api_key=api_key, if_none_match=a.if_none_match)
            emit(result, output=a.output, include_headers=a.include_headers)
        except (ValueError, OSError) as error:
            p.exit(1, "request error: {}\n".format(error))

    def get(path):
        send("GET", path)

    c = a.cmd
    if c == "lookup":
        params = {k: getattr(a, k) for k in LOOKUP}
        get("/v1/lookup" + q(**params))
    elif c == "card": get(f"/u/{urllib.parse.quote(a.card, safe='')}.json")
    elif c == "org": get(f"/o/{urllib.parse.quote(a.card, safe='')}.json")
    elif c == "summary": get(f"/v1/identities/{a.n}/summary")
    elif c == "alias": get(f"/v1/aliases/{a.kind}/{urllib.parse.quote(a.alias, safe='')}")
    elif c == "platforms": get("/v1/platforms")
    elif c == "key": get(f"/v1/keys/{a.key}")
    elif c == "key-active": get(f"/v1/keys/{a.key}/active-at" + q(t=a.t))
    elif c == "verify":
        given = [n for n in HASHES if getattr(a, n)]
        file_mode = a.signature_file or a.file or given or a.name or a.list_file or a.format or a.card
        if file_mode:
            if a.block or a.block_file or a.key or a.message is not None or a.signature or a.platform or a.subject:
                sys.exit("file mode cannot be combined with block/key/message/signature/platform/subject")
            if not a.signature_file:
                sys.exit("file mode needs --signature-file")
            if len(given) + (1 if a.file else 0) != 1:
                sys.exit("file mode needs exactly one of --file, --sha256, --sha512 or --blake2b512")
            body = {"signature": signature_text(a.signature_file)}
            if a.file:
                body[a.hash] = file_hash(a.file, a.hash)
            else:
                body[given[0]] = getattr(a, given[0]).lower()
            name = a.name or (os.path.basename(a.file) if a.file else None)
            if name:
                body["name"] = name
            if a.list_file:
                body["list"] = Path(a.list_file).read_text(encoding="utf-8")
            if a.format:
                body["format"] = a.format
            if a.card:
                body["card"] = a.card
        elif a.block or a.block_file:
            if a.key or a.message or a.signature or a.platform or a.subject:
                sys.exit("block mode cannot be combined with key/message/signature/platform/subject")
            block = a.block if a.block else open(a.block_file, encoding="utf-8").read()
            body = {"block": block}
        elif a.key and a.message is not None and a.signature:
            body = {"key": a.key, "message": a.message, "signature": a.signature}
            if bool(a.platform) != bool(a.subject):
                sys.exit("--platform and --subject must be given together")
            if a.platform:
                body.update(platform=a.platform, subject=a.subject)
        else:
            sys.exit("give --block/--block-file, --key --message --signature, or --signature-file with a file or its hash")
        if a.at is not None:
            body["at"] = a.at
        send("POST", "/v1/verify", body)
    elif c == "versions": get(f"/v1/identities/{a.n}/versions" + q(after=a.after, limit=a.limit, latest="true" if a.latest else None))
    elif c == "history": get(f"/v1/identities/{a.n}/history" + q(before=a.before, limit=a.limit))
    elif c == "proof": get(f"/v1/identities/{a.n}/versions/{a.k}/proof")
    elif c == "events": get(f"/v1/identities/{a.n}/events" + q(after=a.after))
    elif c == "takeovers": get("/v1/takeovers" + q(identity=a.identity))
    elif c == "version": get(f"/v1/identities/{seg(a.n)}/versions/{seg(a.v)}")
    elif c == "authority": get(f"/v1/identities/{seg(a.n)}/authority" + q(after=a.after, limit=a.limit))
    elif c == "statements": get(f"/v1/identities/{seg(a.n)}/statements" + q(**{"from": a.start, "size": a.size}))
    elif c == "labels": get(f"/v1/identities/{seg(a.n)}/labels" + q(after=a.after, limit=a.limit))
    elif c == "members": get(f"/v1/organizations/{seg(a.n)}/members" + q(prefix=a.prefix, bits=a.bits))
    elif c == "set-path": get(f"/v1/identities/{seg(a.n)}/sets/{a.set}/path" + q(key=a.key))
    elif c == "alerts": get(f"/v1/identities/{seg(a.n)}/alerts")
    elif c == "card-statements": get(f"/{a.kind}/{seg(a.card)}/statements.json" + q(before=a.before, limit=a.limit))
    elif c == "statement": get(f"/v1/statements/{seg(a.id)}")
    elif c == "keys-file": get(f"/u/{seg(a.card)}/keys.txt" + q(format=a.format, fp=a.fp))
    elif c == "canary": get("/v1/canary")
    elif c == "linked-roles": get("/v1/discord/linked-roles")
    elif c == "log": get("/v1/log")
    elif c == "catalogue": get("/v1/integrations" + q(lang=a.lang))
    elif c == "openapi": get("/openapi.json")
    elif c == "quota": get("/v1/rate-limit")
    elif c == "get":
        if not a.path.startswith("/") and not a.path.startswith("http"):
            sys.exit("path must start with /")
        get(a.path)
    elif c == "doc": get(f"/v1/integrations/{urllib.parse.quote(a.id, safe='')}" + q(lang=a.lang))


if __name__ == "__main__":
    main()
