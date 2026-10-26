#!/usr/bin/env python3
"""
Veil client: stdlib-only CLI for every public Veil read and message verification.
Signed writes are intentionally NOT implemented: they need the owner's private
device key, which this tool never touches.

-- ZephyrVerrater
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://veil.rip"
UA = "veil-skill-client/1.0"
MAX_WAIT = 30


def request(method, path, body=None, base=BASE, dry_run=False):
    url = path if path.startswith("http") else base.rstrip("/") + path
    data = None
    headers = {"Accept": "application/json", "User-Agent": UA}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if dry_run:
        print(json.dumps({"method": method, "url": url, "body": body}, indent=2))
        return None
    for attempt in (0, 1):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", "replace")
            if e.code in (429, 503) and attempt == 0:
                try:
                    wait = min(float(e.headers.get("Retry-After", "2")), MAX_WAIT)
                except ValueError:
                    wait = 2
                time.sleep(wait)
                continue
            return e.code, text
        except urllib.error.URLError as e:
            sys.exit(f"network error: {e.reason}")


def emit(result):
    if result is None:
        return
    status, text = result
    try:
        out = json.dumps(json.loads(text), indent=2, ensure_ascii=False)
    except ValueError:
        out = text
    if status >= 400:
        print(f"HTTP {status}", file=sys.stderr)
        print(out, file=sys.stderr)
        sys.exit(1)
    print(out)


def q(**params):
    clean = {k: v for k, v in params.items() if v is not None}
    return ("?" + urllib.parse.urlencode(clean)) if clean else ""


def main():
    p = argparse.ArgumentParser(description="Veil (veil.rip) public API client")
    p.add_argument("--base", default=BASE, help="override base URL")
    p.add_argument("--dry-run", action="store_true", help="print the request, do not send")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("lookup", help="find a card by exactly one account/key")
    g = s.add_mutually_exclusive_group(required=True)
    for name in ("discord", "github", "email", "domain", "fediverse", "key", "fingerprint"):
        g.add_argument(f"--{name}")

    s = sub.add_parser("card", help="full person card + proof"); s.add_argument("card")
    s = sub.add_parser("org", help="full organisation card + proof"); s.add_argument("card")
    s = sub.add_parser("summary", help="small metadata, no proof"); s.add_argument("n")
    s = sub.add_parser("alias", help="check/resolve an alias"); s.add_argument("kind", choices=["u", "o"]); s.add_argument("alias")
    sub.add_parser("platforms", help="supported account platforms")
    s = sub.add_parser("key", help="who holds this key"); s.add_argument("key")
    s = sub.add_parser("key-active", help="was key active at time t"); s.add_argument("key"); s.add_argument("--t", type=int)

    s = sub.add_parser("verify", help="verify a signature block or raw signature")
    s.add_argument("--block"); s.add_argument("--block-file")
    s.add_argument("--at", type=int, help="trusted publication time, Unix seconds")
    s.add_argument("--key"); s.add_argument("--message"); s.add_argument("--signature")
    s.add_argument("--platform"); s.add_argument("--subject")

    s = sub.add_parser("versions", help="signed versions"); s.add_argument("n")
    s.add_argument("--after", type=int); s.add_argument("--limit", type=int); s.add_argument("--latest", action="store_true")
    s = sub.add_parser("history", help="card history"); s.add_argument("n"); s.add_argument("--before", type=int); s.add_argument("--limit", type=int)
    s = sub.add_parser("proof", help="inclusion proof for a version"); s.add_argument("n"); s.add_argument("k")
    s = sub.add_parser("events", help="account events"); s.add_argument("n"); s.add_argument("--after", type=int)
    s = sub.add_parser("takeovers", help="account transfers"); s.add_argument("identity")
    sub.add_parser("log", help="directory log state")
    sub.add_parser("catalogue", help="machine-readable endpoint index")
    s = sub.add_parser("get", help="GET any public path, e.g. /v1/identities/1/orgs"); s.add_argument("path")
    s = sub.add_parser("doc", help="live contract for one endpoint id"); s.add_argument("id")

    a = p.parse_args()
    b, d = a.base, a.dry_run

    def get(path):
        emit(request("GET", path, base=b, dry_run=d))

    c = a.cmd
    if c == "lookup":
        params = {k: getattr(a, k) for k in ("discord", "github", "email", "domain", "fediverse", "key", "fingerprint")}
        get("/v1/lookup" + q(**params))
    elif c == "card": get(f"/u/{urllib.parse.quote(a.card)}.json")
    elif c == "org": get(f"/o/{urllib.parse.quote(a.card)}.json")
    elif c == "summary": get(f"/v1/identities/{a.n}/summary")
    elif c == "alias": get(f"/v1/aliases/{a.kind}/{urllib.parse.quote(a.alias)}")
    elif c == "platforms": get("/v1/platforms")
    elif c == "key": get(f"/v1/keys/{a.key}")
    elif c == "key-active": get(f"/v1/keys/{a.key}/active-at" + q(t=a.t))
    elif c == "verify":
        if a.block or a.block_file:
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
            sys.exit("give --block/--block-file, or --key --message --signature")
        if a.at is not None:
            body["at"] = a.at
        emit(request("POST", "/v1/verify", body, base=b, dry_run=d))
    elif c == "versions": get(f"/v1/identities/{a.n}/versions" + q(after=a.after, limit=a.limit, latest="true" if a.latest else None))
    elif c == "history": get(f"/v1/identities/{a.n}/history" + q(before=a.before, limit=a.limit))
    elif c == "proof": get(f"/v1/identities/{a.n}/versions/{a.k}/proof")
    elif c == "events": get(f"/v1/identities/{a.n}/events" + q(after=a.after))
    elif c == "takeovers": get("/v1/takeovers" + q(identity=a.identity))
    elif c == "log": get("/v1/log")
    elif c == "catalogue": get("/v1/integrations")
    elif c == "get":
        if not a.path.startswith("/") and not a.path.startswith("http"):
            sys.exit("path must start with /")
        get(a.path)
    elif c == "doc": get(f"/v1/integrations/{urllib.parse.quote(a.id)}")


if __name__ == "__main__":
    main()
