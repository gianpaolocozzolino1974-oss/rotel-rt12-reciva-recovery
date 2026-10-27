#!/usr/bin/env python3
"""Rotel RT-12 local update server. Defaults to SAFE, no-update mode.

ONLY --arm-update offers an executable update to the Rotel. This is an
experimental flash procedure with a permanent-brick risk. Do not use without
verifying the recipient, firmware version, and available recovery options.
"""

import argparse
import hashlib
import http.server
import ipaddress
from pathlib import Path
import socket
import struct
import threading
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit


FIRMWARE_NAME = "sp266-a-137-a-031.bin"
WRAPPER_NAME = "sp.266-a-137-a-031.LOCAL-UNTESTED.tar.bz2"
FIRMWARE_MD5 = "cdee3d618f809d26069dfa21efe139c8"
WRAPPER_SHA256 = "ff4789b37756e838903798e2d646d02e011678141ebd528c1e6e30622e6ed200"
UPDATE_HOST = "www.reciva.com"
CGI_PATHS = frozenset(("/cgi-local/service-pack.pl", "/cgi-local//service-pack.pl"))


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def checksum(path, algorithm):
    digest = hashlib.new(algorithm)
    with open(path, "rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def question(packet):
    if len(packet) < 17:
        raise ValueError("DNS packet too short")
    offset, labels = 12, []
    for _ in range(80):
        if offset >= len(packet):
            raise ValueError("Invalid DNS question")
        n = packet[offset]
        offset += 1
        if not n:
            break
        if n > 63 or offset + n > len(packet):
            raise ValueError("Invalid DNS label")
        labels.append(packet[offset:offset + n].decode("ascii", "replace"))
        offset += n
    else:
        raise ValueError("Too many DNS labels")
    if offset + 4 > len(packet):
        raise ValueError("Missing DNS question type")
    qtype, qclass = struct.unpack("!HH", packet[offset:offset + 4])
    return ".".join(labels).lower(), qtype, qclass, packet[12:offset + 4]


def response(packet, qdata, qtype, qclass, local_ip):
    answer = b""
    if qtype == 1 and qclass == 1:
        answer = b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, 30, 4) + socket.inet_aton(local_ip)
    return (packet[:2] + struct.pack("!HHHHH", 0x8180, 1, int(bool(answer)), 0, 0)
            + qdata + answer)


def dns_loop(sock, local_ip, router_ip, allowed_radio, stop):
    while not stop.is_set():
        try:
            data, origin = sock.recvfrom(4096)
        except socket.timeout:
            continue
        try:
            host, qtype, qclass, qdata = question(data)
        except ValueError:
            continue
        if origin[0] == allowed_radio and host == UPDATE_HOST:
            answer = response(data, qdata, qtype, qclass, local_ip)
            log(f"DNS Rotel {host} type={qtype} -> Mac")
        else:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as upstream:
                    upstream.settimeout(2)
                    upstream.sendto(data, (router_ip, 53))
                    answer, _ = upstream.recvfrom(4096)
            except OSError:
                answer = (data[:2] + struct.pack("!HHHHH", 0x8182, 1, 0, 0, 0)
                          + qdata)
        sock.sendto(answer, origin)


class Handler(http.server.BaseHTTPRequestHandler):
    mac_ip = None
    rotel_ip = None
    firmware = None
    wrapper = None
    armed = False

    def log_message(self, format, *args):
        pass

    def safe_log(self, result):
        parts = urlsplit(self.path)
        args = urlencode([(k, "[omesso]" if k.lower() == "serial" else v)
                          for k, v in parse_qsl(parts.query, keep_blank_values=True)])
        log(f"HTTP {self.client_address[0]} {self.command} "
            f"Host={self.headers.get('Host', '-')} "
            f"Path={parts.path}{'?' + args if args else ''} -> {result}")

    def send_data(self, content, kind="text/plain; charset=utf-8", send_body=True):
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        if send_body:
            self.wfile.write(content)

    def do_HEAD(self):
        self.handle_read(send_body=False)

    def do_GET(self):
        self.handle_read(send_body=True)

    def handle_read(self, send_body):
        origin_ip = self.client_address[0]
        if origin_ip not in (self.mac_ip, self.rotel_ip):
            return self.reject(403)
        parts = urlsplit(self.path)
        host = self.headers.get("Host", "").split(":", 1)[0].lower()
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        if (origin_ip == self.rotel_ip and host == UPDATE_HOST
                and parts.path in CGI_PATHS and self.command == "GET"):
            if query.get("sp") != "v265-a-254-a-301-a-007" or query.get("hw") != "633" or query.get("sv") != "03":
                return self.reject(412)
            if query.get("check") == "1":
                if self.armed:
                    body = f"http://{self.mac_ip}/{WRAPPER_NAME}\n".encode()
                    self.safe_log("UPDATE OFFER (armed)")
                else:
                    body = b"none\n"
                    self.safe_log("NO UPDATE (safe mode)")
                return self.send_data(body)
            if query.get("check") == "0" and self.armed:
                self.safe_log("UPDATE WRAPPER URL (armed)")
                return self.send_data(f"http://{self.mac_ip}/{WRAPPER_NAME}\n".encode())
            return self.reject(404)
        if parts.query or host != self.mac_ip:
            return self.reject(404)
        if parts.path == f"/{FIRMWARE_NAME}":
            target = self.firmware
        elif parts.path == f"/{WRAPPER_NAME}":
            target = self.wrapper
        else:
            return self.reject(404)
        self.safe_log(f"200 - local file {target.name}")
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(target.stat().st_size))
        self.end_headers()
        if send_body:
            with open(target, "rb") as source:
                while data := source.read(1024 * 64):
                    self.wfile.write(data)

    def reject(self, code):
        self.safe_log(str(code))
        self.send_error(code, "No update content")

    def do_POST(self):
        self.reject(405)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mac-ip", required=True)
    parser.add_argument("--rotel-ip", required=True)
    parser.add_argument("--router-ip", default="192.168.178.1")
    parser.add_argument("--directory", required=True, type=Path,
                        help="Directory with the matching 15 MiB firmware and local wrapper")
    parser.add_argument("--dns-port", type=int, default=53)
    parser.add_argument("--http-port", type=int, default=80)
    parser.add_argument("--arm-update", action="store_true",
                        help="DANGER: offer a real flash update instead of responding none")
    args = parser.parse_args()
    for address in (args.mac_ip, args.rotel_ip, args.router_ip):
        ipaddress.IPv4Address(address)
    firmware = args.directory / FIRMWARE_NAME
    wrapper = args.directory / WRAPPER_NAME
    for file, algorithm, expected in ((firmware, "md5", FIRMWARE_MD5),
                                       (wrapper, "sha256", WRAPPER_SHA256)):
        if not file.is_file() or checksum(file, algorithm) != expected:
            parser.error(f"File missing or wrong {algorithm}: {file}")
    Handler.mac_ip = args.mac_ip
    Handler.rotel_ip = args.rotel_ip
    Handler.firmware = firmware
    Handler.wrapper = wrapper
    Handler.armed = args.arm_update
    dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        dns.bind((args.mac_ip, args.dns_port))
        dns.settimeout(.5)
        server = http.server.ThreadingHTTPServer((args.mac_ip, args.http_port), Handler)
    except OSError as exc:
        dns.close()
        parser.error(f"Ports unavailable: {exc}")
    stop = threading.Event()
    t = threading.Thread(target=dns_loop, args=(dns, args.mac_ip, args.router_ip,
                                                args.rotel_ip, stop), daemon=True)
    t.start()
    if args.arm_update:
        log("*** ATTENZIONE: AGGIORNAMENTO REALE ABILITATO. RISCHIO DANNO PERMANENTE. ***")
    else:
        log("Modalita' SICURA: il Rotel riceve sempre 'none'; nessun aggiornamento proposto.")
    log(f"DNS su {args.mac_ip}:{args.dns_port}; HTTP su {args.mac_ip}:{args.http_port}")
    log("Ctrl+C per arrestare, dopo aver ripristinato DHCP sul Rotel.")
    try:
        server.serve_forever(poll_interval=.5)
    except KeyboardInterrupt:
        log("Arresto server")
    finally:
        stop.set()
        server.server_close()
        t.join(timeout=2)
        dns.close()


if __name__ == "__main__":
    main()
