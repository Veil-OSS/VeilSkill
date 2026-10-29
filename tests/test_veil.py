import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from email.utils import formatdate
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("veil_client", ROOT / "scripts/veil.py")
veil = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(veil)
KEY = "test-key-used-only-on-loopback"


@contextlib.contextmanager
def server(answer):
    calls = []

    class Handler(BaseHTTPRequestHandler):
        def handle_call(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            calls.append({"path": self.path, "method": self.command, "headers": dict(self.headers), "body": body})
            status, headers, data = answer(calls)
            self.send_response(status)
            self.send_header("Content-Length", str(len(data)))
            for name, value in headers.items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(data)

        do_GET = do_POST = handle_call

        def log_message(self, *args):
            pass

    http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=lambda: http.serve_forever(poll_interval=0.01), daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:{}".format(http.server_port), calls
    finally:
        http.shutdown()
        http.server_close()
        thread.join()


def ok(_):
    return 200, {"Content-Type": "application/json"}, b'{"ok":true}'


def error(status, code, headers=None):
    return status, dict({"Content-Type": "application/json"}, **(headers or {})), json.dumps({"error": {"code": code, "message": "Test response"}}).encode()


class ClientTest(unittest.TestCase):
    def test_anonymous_reads_do_not_pick_up_an_ambient_key(self):
        with server(ok) as (base, calls), patch.dict(os.environ, {"VEIL_API_KEY": KEY}):
            response = veil.request("GET", "/v1/platforms", base=base)
        self.assertEqual(200, response.status)
        self.assertNotIn("Authorization", calls[0]["headers"])

    def test_bearer_read_uses_configured_origin(self):
        with server(ok) as (base, calls):
            self.assertEqual(200, veil.request("GET", "/v1/rate-limit", base=base, api_key=KEY).status)
        self.assertEqual("Bearer " + KEY, calls[0]["headers"]["Authorization"])

    def test_dry_run_redacts_credentials_and_sends_nothing(self):
        with server(ok) as (base, calls), contextlib.redirect_stdout(io.StringIO()) as output:
            veil.request("GET", "/v1/rate-limit", base=base, api_key=KEY, dry_run=True)
        self.assertEqual([], calls)
        self.assertNotIn(KEY, output.getvalue())
        self.assertEqual("Bearer [redacted]", json.loads(output.getvalue())["headers"]["Authorization"])

    def test_key_cannot_be_sent_to_an_absolute_foreign_url(self):
        with server(ok) as (base, calls), server(ok) as (other, other_calls):
            with self.assertRaises(ValueError):
                veil.request("GET", other + "/v1/platforms", base=base, api_key=KEY)
        self.assertEqual([], calls)
        self.assertEqual([], other_calls)

    def test_key_cannot_follow_a_cross_origin_redirect(self):
        with server(ok) as (other, other_calls):
            with server(lambda _: (302, {"Location": other + "/target"}, b"")) as (base, calls):
                with self.assertRaises(ValueError):
                    veil.request("GET", "/redirect", base=base, api_key=KEY)
        self.assertEqual(1, len(calls))
        self.assertEqual([], other_calls)

    def test_same_origin_redirect_keeps_credential(self):
        def answer(calls):
            return (302, {"Location": "/target"}, b"") if len(calls) == 1 else ok(calls)
        with server(answer) as (base, calls):
            self.assertEqual(200, veil.request("GET", "/redirect", base=base, api_key=KEY).status)
        self.assertEqual(["Bearer " + KEY] * 2, [c["headers"]["Authorization"] for c in calls])

    def test_key_transport_refuses_cleartext_nonloopback(self):
        with self.assertRaises(ValueError):
            veil.request("GET", "/v1/platforms", base="http://203.0.113.1", api_key=KEY)

    def test_embedded_url_credentials_are_rejected(self):
        with self.assertRaises(ValueError):
            veil.request("GET", "/v1/platforms", base="https://name:password@example.com")

    def test_invalid_key_never_falls_back_or_retries(self):
        with server(lambda _: error(401, "invalid_api_key")) as (base, calls), patch.object(veil.time, "sleep") as sleep:
            self.assertEqual(401, veil.request("GET", "/v1/platforms", base=base, api_key=KEY).status)
        self.assertEqual(1, len(calls))
        self.assertEqual("Bearer " + KEY, calls[0]["headers"]["Authorization"])
        sleep.assert_not_called()

    def test_short_retry_after_is_respected(self):
        def answer(calls):
            return error(429, "rate_limited", {"Retry-After": "2"}) if len(calls) == 1 else ok(calls)
        with server(answer) as (base, calls), patch.object(veil.time, "sleep") as sleep:
            self.assertEqual(200, veil.request("GET", "/v1/platforms", base=base).status)
        self.assertEqual(2, len(calls))
        sleep.assert_called_once_with(2)

    def test_long_retry_after_does_not_trigger_an_early_retry(self):
        with server(lambda _: error(429, "rate_limited", {"Retry-After": "120"})) as (base, calls), patch.object(veil.time, "sleep") as sleep:
            self.assertEqual(429, veil.request("GET", "/v1/platforms", base=base).status)
        self.assertEqual(1, len(calls))
        sleep.assert_not_called()

    def test_readonly_verification_gets_at_most_one_transient_retry(self):
        with server(lambda _: error(503, "busy", {"Retry-After": "1"})) as (base, calls), patch.object(veil.time, "sleep") as sleep:
            self.assertEqual(503, veil.request("POST", "/v1/verify", {"block": "test"}, base=base).status)
        self.assertEqual(2, len(calls))
        sleep.assert_called_once_with(1)
        self.assertEqual(calls[0]["body"], calls[1]["body"])

    def test_a_signed_write_would_not_be_retried(self):
        with server(lambda _: error(503, "busy", {"Retry-After": "1"})) as (base, calls), patch.object(veil.time, "sleep") as sleep:
            self.assertEqual(503, veil.request("POST", "/v1/identities", {}, base=base).status)
        self.assertEqual(1, len(calls))
        sleep.assert_not_called()

    def test_proof_attempt_limit_is_not_a_retryable_quota(self):
        with server(lambda _: error(429, "too_many_attempts", {"Retry-After": "1"})) as (base, calls), patch.object(veil.time, "sleep") as sleep:
            self.assertEqual(429, veil.request("GET", "/proof", base=base).status)
        self.assertEqual(1, len(calls))
        sleep.assert_not_called()

    def test_retry_after_http_dates(self):
        now = 1793059200
        with patch.object(veil.time, "time", return_value=now):
            self.assertEqual(12, veil.retry_delay(formatdate(now + 12, usegmt=True)))
            self.assertIsNone(veil.retry_delay(formatdate(now + 120, usegmt=True)))

    def test_nonfinite_or_malformed_waits_do_not_retry(self):
        for value in ("nan", "inf", "not-a-time", "1e999"):
            with self.subTest(value=value):
                self.assertIsNone(veil.retry_delay(value))

    def test_binary_output_preserves_exact_bytes(self):
        payload = b"\x89PNG\x00\xff\x00test"
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "image.png"
            veil.emit(veil.Response(200, payload, {"content-type": "image/png"}), output=p)
            self.assertEqual(payload, p.read_bytes())

    def test_binary_requires_explicit_file_output(self):
        with self.assertRaises(ValueError):
            veil.emit(veil.Response(200, b"\x00\xff", {"content-type": "application/octet-stream"}))

    def test_an_error_does_not_overwrite_an_output_file(self):
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stderr(io.StringIO()) as stderr:
            p = Path(folder) / "response.json"
            p.write_bytes(b"saved")
            with self.assertRaises(SystemExit) as failure:
                veil.emit(veil.Response(429, b'{"error":{"code":"rate_limited"}}', {"retry-after": "120"}), output=p)
            self.assertEqual(1, failure.exception.code)
            self.assertEqual(b"saved", p.read_bytes())
            self.assertIn("Retry-After: 120", stderr.getvalue())

    def test_not_modified_keeps_saved_representation(self):
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stderr(io.StringIO()) as stderr:
            p = Path(folder) / "cached.json"
            p.write_bytes(b"cached")
            veil.emit(veil.Response(304, b"", {"etag": 'W/"test"'}), output=p, include_headers=True)
            self.assertEqual(b"cached", p.read_bytes())
            self.assertIn("HTTP 304", stderr.getvalue())

    def test_headers_do_not_change_json_stdout(self):
        with contextlib.redirect_stderr(io.StringIO()) as stderr, contextlib.redirect_stdout(io.StringIO()) as stdout:
            veil.emit(veil.Response(200, b'{"remaining":600}', {"x-ratelimit-limit": "600"}), include_headers=True)
        self.assertEqual({"remaining": 600}, json.loads(stdout.getvalue()))
        self.assertIn("x-ratelimit-limit: 600", stderr.getvalue())

    def test_conditional_header_reaches_server(self):
        with server(lambda _: (304, {"ETag": 'W/"cached"'}, b"")) as (base, calls):
            response = veil.request("GET", "/v1/integrations", base=base, if_none_match='W/"cached"')
        self.assertEqual(304, response.status)
        self.assertEqual('W/"cached"', calls[0]["headers"]["If-None-Match"])

    def test_cli_reads_a_key_from_the_named_environment_variable(self):
        with server(ok) as (base, calls):
            r = subprocess.run([sys.executable, str(ROOT / "scripts/veil.py"), "--base", base, "--api-key-env", "VEIL_TEST_KEY", "quota"], capture_output=True, text=True, env=dict(os.environ, VEIL_TEST_KEY=KEY))
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual("/v1/rate-limit", calls[0]["path"])
        self.assertEqual("Bearer " + KEY, calls[0]["headers"]["Authorization"])
        self.assertNotIn(KEY, r.stdout + r.stderr)

    def test_quota_without_credential_option_stops_before_network(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts/veil.py"), "quota"], capture_output=True, text=True)
        self.assertEqual(2, r.returncode)
        self.assertIn("--api-key-env", r.stderr)

    def test_cli_supports_italian_guide_metadata(self):
        with server(ok) as (base, calls):
            r = subprocess.run([sys.executable, str(ROOT / "scripts/veil.py"), "--base", base, "doc", "errors", "--lang", "it"], capture_output=True, text=True)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual("/v1/integrations/errors?lang=it", calls[0]["path"])

    def test_cli_builds_format_2_read_paths(self):
        cases = [
            (["version", "1", "1"], "/v1/identities/1/versions/1"),
            (["authority", "1", "--after", "0", "--limit", "50"], "/v1/identities/1/authority?after=0&limit=50"),
            (["statements", "1", "--from", "11", "--size", "412"], "/v1/identities/1/statements?from=11&size=412"),
            (["labels", "1"], "/v1/identities/1/labels"),
            (["members", "2", "--prefix", "gA==", "--bits", "1"], "/v1/organizations/2/members?prefix=gA%3D%3D&bits=1"),
            (["set-path", "1", "links", "--key", "github\n109546049"], "/v1/identities/1/sets/links/path?key=github%0A109546049"),
        ]
        with server(ok) as (base, calls):
            for args, path in cases:
                with self.subTest(args=args):
                    r = subprocess.run([sys.executable, str(ROOT / "scripts/veil.py"), "--base", base] + args, capture_output=True, text=True)
                    self.assertEqual(0, r.returncode, r.stderr)
                    self.assertEqual(path, calls[-1]["path"])
                    self.assertEqual("GET", calls[-1]["method"])
                    self.assertNotIn("Authorization", calls[-1]["headers"])

    def test_statements_requires_the_cursor_from_the_card(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts/veil.py"), "statements", "1"], capture_output=True, text=True)
        self.assertEqual(2, r.returncode)
        self.assertIn("--from", r.stderr)


if __name__ == "__main__":
    unittest.main()
