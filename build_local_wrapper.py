#!/usr/bin/env python3
"""Create a *local-only* RT-12 update wrapper from the official Rotel archive.

No Rotel binaries are redistributed by this repository. This generalized
builder has been checked offline, but the resulting packages have NOT been
tested on additional devices. Flashing an unsupported radio may brick it.
"""

import argparse
import copy
import hashlib
import io
import ipaddress
from pathlib import Path
import tarfile


ORIGINAL_SHA256 = "620ab7082c982404eb0eedcbbdb9145e2e865424a8454890ad7e210f4ae15335"
BIN_MD5 = "cdee3d618f809d26069dfa21efe139c8"
BIN_NAME = "sp266-a-137-a-031.bin"
RESULT_NAME = "sp.266-a-137-a-031.LOCAL-UNTESTED.tar.bz2"
ORIGINAL_URL = b"https://www.rotelupgrade.com/binaries/sp266-a-137-a-031.bin"
INSTALLER_PATH = "built-servicepack/install-me"
EXPECTED_FILES = {"built-servicepack", INSTALLER_PATH,
                  "built-servicepack/firmware_upgrade", "built-servicepack/progress_simple"}


def digest(path, algorithm):
    h = hashlib.new(algorithm)
    with open(path, "rb") as source:
        while chunk := source.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def build(official_wrapper, firmware, mac_ip, output_dir):
    ipaddress.IPv4Address(mac_ip)
    if digest(official_wrapper, "sha256") != ORIGINAL_SHA256:
        raise ValueError("The official wrapper is not the exact verified archive")
    if digest(firmware, "md5") != BIN_MD5:
        raise ValueError("Wrong firmware: expected official SP266-a-137-a-031 MD5")
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / RESULT_NAME
    if output.exists():
        raise FileExistsError(f"Already exists; move it away before building: {output}")
    new_url = f"http://{mac_ip}/{BIN_NAME}".encode("ascii")
    with tarfile.open(official_wrapper, "r:bz2") as source:
        members = source.getmembers()
        if {m.name for m in members} != EXPECTED_FILES:
            raise ValueError("Unexpected archive contents")
        installed = next(m for m in members if m.name == INSTALLER_PATH)
        script = source.extractfile(installed).read()
        if script.count(ORIGINAL_URL) != 1:
            raise ValueError("Unexpected official installer; refusing substitution")
        if BIN_MD5.encode() not in script or b"grep -q zd1211" not in script:
            raise ValueError("Firmware hash or original hardware guard missing")
        replacement = script.replace(ORIGINAL_URL, new_url)
        # Only the firmware download URL changes. The vendor flash executable,
        # checksum guard, and hardware guard remain unmodified.
        with tarfile.open(output, "w:bz2") as target:
            for member in members:
                data = replacement if member.name == INSTALLER_PATH else (
                    source.extractfile(member).read() if member.isfile() else None)
                info = copy.copy(member)
                if data is not None:
                    info.size = len(data)
                    target.addfile(info, io.BytesIO(data))
                else:
                    target.addfile(info)
    print(f"Created: {output}")
    print(f"SHA-256: {digest(output, 'sha256')}")
    print("Only one URL was changed; official device guards remain in place.")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official-wrapper", required=True, type=Path)
    parser.add_argument("--firmware", required=True, type=Path)
    parser.add_argument("--mac-ip", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    build(args.official_wrapper, args.firmware, args.mac_ip, args.output_dir)


if __name__ == "__main__":
    main()
