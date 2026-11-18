# -*- coding: utf-8 -*-
"""
check_us_region_and_ipv6.py
Zero-dependency local diagnostic for IPv6 precedence, DNS resolution purity,
and Google / Gemini / Claude / GitHub TLS handshake health.
"""
import socket
import ssl
import time

TARGETS = [
    ("Google Accounts / Family", " families.google.com".strip(), 443),
    ("Google Pay Profile", "pay.google.com", 443),
    ("Gemini Web / API", "gemini.google.com", 443),
    ("Anthropic Claude", "claude.ai", 443),
    ("GitHub API", "api.github.com", 443),
]


def inspect_target(label, host, port=443, timeout=5.0):
    t0 = time.perf_counter()
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except Exception as e:
        return {"label": label, "host": host, "ok": False, "error": f"DNS failed: {e}"}

    dns_ms = round((time.perf_counter() - t0) * 1000, 1)
    first_family = "IPv6" if infos and infos[0][0] == socket.AF_INET6 else "IPv4"
    v4_list = sorted({i[4][0] for i in infos if i[0] == socket.AF_INET})
    v6_list = sorted({i[4][0] for i in infos if i[0] == socket.AF_INET6})

    ctx = ssl.create_default_context()
    t1 = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            peer_ip = s.getpeername()[0]
            with ctx.wrap_socket(s, server_hostname=host) as ss:
                tls_ms = round((time.perf_counter() - t1) * 1000, 1)
                return {
                    "label": label,
                    "host": host,
                    "ok": True,
                    "dns_ms": dns_ms,
                    "tls_ms": tls_ms,
                    "preferred_family": first_family,
                    "connected_ip": peer_ip,
                    "ipv4_count": len(v4_list),
                    "ipv6_count": len(v6_list),
                    "tls_ver": ss.version(),
                }
    except Exception as e:
        return {
            "label": label,
            "host": host,
            "ok": False,
            "dns_ms": dns_ms,
            "preferred_family": first_family,
            "ipv4_count": len(v4_list),
            "ipv6_count": len(v6_list),
            "error": str(e),
        }


def main():
    print("================================================================")
    print("  AI & Google Region / IPv6 Precedence Self-Check Tool v1.1")
    print("================================================================")
    v6_preferred = 0
    for label, host, port in TARGETS:
        r = inspect_target(label, host, port)
        if r.get("preferred_family") == "IPv6":
            v6_preferred += 1
        if r["ok"]:
            print(
                f"[PASS] {label:24s} | pref={r['preferred_family']} | dns={r['dns_ms']:>5}ms | tls={r['tls_ms']:>6}ms | ip={r['connected_ip']}"
            )
        else:
            print(
                f"[WARN] {label:24s} | pref={r.get('preferred_family')} | err={r['error']}"
            )

    print("----------------------------------------------------------------")
    if v6_preferred > 0:
        print(
            f"[NOTICE] Detected {v6_preferred} endpoint(s) preferring IPv6 first. If your ISP IPv6 bypasses rule routing, region-sensitive services may misdetect your location."
        )
    else:
        print("[OK] All tested endpoints prefer IPv4 or clean tunnel interfaces.")
    print(
        "Companion Guide & Pre-configured MetaCubeX (.mrs) Desktop Client: https://sketchsketch942008-star.github.io/Xiaopohu-Desktop/"
    )


if __name__ == "__main__":
    main()
