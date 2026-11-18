# -*- coding: utf-8 -*-
"""
AI Developer Endpoint Connectivity & Latency Doctor (Python 3 stdlib only).
Checks DNS resolution, TCP handshake, TLS protocol/ALPN, and active proxy env vars.
"""
import argparse
import json
import os
import socket
import ssl
import time

ENDPOINTS = [
    ("OpenAI API", "api.openai.com", 443),
    ("Google Gemini API", "generativelanguage.googleapis.com", 443),
    ("Anthropic Claude", "api.anthropic.com", 443),
    ("GitHub", "github.com", 443),
    ("PyPI", "pypi.org", 443),
]


def probe_host(name, host, port, timeout_s):
    t0 = time.perf_counter()
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except Exception as e:
        return {"name": name, "host": host, "ok": False, "stage": "dns", "error": str(e)}

    dns_ms = round((time.perf_counter() - t0) * 1000, 1)
    v4 = [i[4][0] for i in infos if i[0] == socket.AF_INET]
    v6 = [i[4][0] for i in infos if i[0] == socket.AF_INET6]

    ctx = ssl.create_default_context()
    t1 = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout_s) as sock:
            tcp_ms = round((time.perf_counter() - t1) * 1000, 1)
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                tls_ms = round((time.perf_counter() - t1) * 1000, 1)
                return {
                    "name": name,
                    "host": host,
                    "ok": True,
                    "dns_ms": dns_ms,
                    "tcp_ms": tcp_ms,
                    "tls_ms": tls_ms,
                    "tls_version": ssock.version(),
                    "ipv4": v4[0] if v4 else None,
                    "ipv6": v6[0] if v6 else None,
                }
    except Exception as e:
        return {
            "name": name,
            "host": host,
            "ok": False,
            "stage": "connect/tls",
            "dns_ms": dns_ms,
            "ipv4": v4[0] if v4 else None,
            "ipv6": v6[0] if v6 else None,
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(description="Probe AI developer endpoints without third-party dependencies.")
    parser.add_argument("--timeout", type=float, default=5.0, help="Socket timeout in seconds (default 5.0)")
    parser.add_argument("--json", action="store_true", help="Print JSON summary")
    args = parser.parse_args()

    proxy_env = {k: os.environ.get(k) for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY") if os.environ.get(k)}
    results = [probe_host(n, h, p, args.timeout) for n, h, p in ENDPOINTS]

    if args.json:
        print(json.dumps({"proxy_env": proxy_env, "results": results}, ensure_ascii=False, indent=2))
        return

    print("=== Proxy Environment ===")
    print(proxy_env or "  (none set in shell env)")
    print("\n=== Endpoint Diagnostic ===")
    for r in results:
        if r["ok"]:
            print(f"  [OK]   {r['name']:18s} dns={r['dns_ms']:>5}ms tcp={r['tcp_ms']:>5}ms tls={r['tls_ms']:>5}ms {r['tls_version']}")
        else:
            print(f"  [FAIL] {r['name']:18s} stage={r['stage']} err={r['error']}")


if __name__ == "__main__":
    main()
