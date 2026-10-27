# Rotel RT-12 Internet Radio recovery after the Reciva shutdown

## Verified result

On **27 October 2026**, one RT-12 was recovered **without replacing the Reciva module**. The owner confirmed:

- **Before:** Internet Radio `v265-a-254-a-301-a-007`; hardware code `633`; Rotel Main software `V1.26`.
- **Local network upgrade:** Official Rotel `v266-a-137-a-031` firmware, delivered using a temporary Mac DNS/HTTP server and a locally rebuilt official wrapper.
- **Important recovery step:** After the local flash, `Network → Settings` did not open. A **Factory Default of Module only** through the separate remote-control SETUP menu restored it. The display then confirmed `v266-a-137-a-031`.
- **Official network upgrade:** After restoring DHCP and turning off the local server, the RT-12 contacted the Rotel update service and upgraded to `v266-a-137-a-038`.
- **Final Factory Default of Module only**, as Rotel advises following the new streaming update.
- **Result:** Internet Radio played successfully; see the photo of *Deep House Radio — 192 kbps MP3*.

This is a reproducible **case record, not a safety guarantee**. The portable scripts supplied alongside the exact tested server are new adaptations and have **not** been flashed on another device. Wrong firmware, power loss, incompatible hardware, or a corrupt installer could brick your radio. Nothing in this repository should be treated as an official Rotel support procedure.

## Prerequisites and exact matching

The observed device started with **exactly** `v265-a-254-a-301-a-007` and Reciva hardware code `633`, reporting `sv=03` in the firmware request. **Do not attempt this on another version or hardware code simply because it is an RT-12.** Do not assume it works on RT-09, RT-1570, RCX-1500 or RDG-1520.

Use a stable wired Ethernet connection, adequate uninterrupted power, and a Mac with Python 3. The Mac and radio must be on the same trusted non-guest LAN. Changing the radio's DNS **does not require changing DNS for all devices on your router**. Back up presets first: Factory Default removes them and resets networking.

## Obtain original vendor files

Download directly from Rotel, into a folder such as `~/Downloads/RotelTest`:

1. <https://www.rotelupgrade.com/binaries/sp266-a-137-a-031.bin>
2. <https://www.rotelupgrade.com/wrappers/sp.266-a-137-a-031.tar.bz2>

The original `.bin` is **15,728,640 bytes**. These are the checksums observed in the successful case:

```text
sp266-a-137-a-031.bin             MD5     cdee3d618f809d26069dfa21efe139c8
sp.266-a-137-a-031.tar.bz2        SHA256  620ab7082c982404eb0eedcbbdb9145e2e865424a8454890ad7e210f4ae15335
```

Check them on macOS using `md5 FILE` and `shasum -a 256 FILE`. The firmware and vendor executables are **not redistributed** in this project. Older vendor websites may have TLS/certificate problems; never trust a download with a mismatching hash.

## Create the local wrapper

The observed case changed exactly one line in the vendor's `built-servicepack/install-me`: the firmware download URL was replaced with the local Mac URL. The vendor's binary `firmware_upgrade`, its expected firmware MD5 and its Wi-Fi hardware safety check remained untouched.

From the repository root, replace the sample Mac IP with your real LAN IP:

```bash
python3 scripts/build_local_wrapper.py \
  --official-wrapper "$HOME/Downloads/RotelTest/sp.266-a-137-a-031.tar.bz2" \
  --firmware "$HOME/Downloads/RotelTest/sp266-a-137-a-031.bin" \
  --mac-ip 192.168.178.83 \
  --output-dir "$HOME/Downloads/RotelTest"
```

The builder checks the original hashes and outputs `sp.266-a-137-a-031.LOCAL-UNTESTED.tar.bz2` along with its SHA-256. Write that value down. This is a **generalized, offline-tested builder**, not an additional radio-tested installation method.

For reference, the actual locally modified archive in the successful case had SHA-256 `ff4789b37756e838903798e2d646d02e011678141ebd528c1e6e30622e6ed200` and embedded URL `http://192.168.178.83/sp266-a-137-a-031.bin`. A rebuild with different archive metadata may have a different SHA-256 even with the same script substitution; compare the content and provenance.

## Check server communication in SAFE mode first

The temporary Python server listens on the Mac's DNS **UDP 53** and HTTP **TCP 80**. It redirects `www.reciva.com` **only when the request comes from the specified radio IP**, forwarding other DNS queries to your router. In safe mode it answers update checks with `none` and does not offer firmware updates.

Replace all example IP addresses with your actual LAN values:

```bash
sudo python3 scripts/rotel_upgrade_server_portable.py \
  --mac-ip 192.168.178.83 \
  --rotel-ip 192.168.178.114 \
  --router-ip 192.168.178.1 \
  --directory "$HOME/Downloads/RotelTest"
```

If port 53 is occupied, inspect with `sudo lsof -nP -iUDP:53 -iTCP:80`. On the tested Mac, Internet Sharing was temporarily turned off **only after confirming no other devices relied on it**. Do not terminate Apple's `mDNSResponder` or disturb other household devices to free the port.

On the radio, navigate to `NETWORK → Settings → Network Config → Edit Config`, choose **Auto DHCP NO**, then set:

| Field | Successful-case example |
| --- | --- |
| IP | `192.168.178.114` |
| Netmask | `255.255.255.0` |
| Gateway | `192.168.178.1` |
| Primary DNS | `192.168.178.83` (Mac) |

Test `ping -c 4 192.168.178.114`. Then choose `Settings → Upgrade Firmware` **while the server is in safe mode**. It should show **No Upgrade Available**, with the server logging `NO UPDATE (safe mode)`. If this validation fails, **STOP**.

## Risky step: offer the original vendor upgrade over the LAN

1. Restore the radio to **Auto DHCP YES** before stopping the safe DNS server.
2. Stop the server with `Control+C`.
3. Start it again with **explicit** `--arm-update` **and** the independently checked SHA-256 printed by the local wrapper builder:

```bash
sudo python3 scripts/rotel_upgrade_server_portable.py \
  --mac-ip 192.168.178.83 \
  --rotel-ip 192.168.178.114 \
  --router-ip 192.168.178.1 \
  --directory "$HOME/Downloads/RotelTest" \
  --wrapper-sha256 REPLACE_WITH_THE_64_CHARACTER_SHA256 \
  --arm-update
```

4. Configure **only the radio** with the same static IP, gateway and Mac DNS as before; re-test ping.
5. Choose `Settings → Upgrade Firmware`. A confirmation such as **Are You Sure? YES/NO** may appear. **YES may initiate actual flashing**. Stop here unless you accept a permanent-brick risk and have verified all files, IDs, network and power conditions.
6. The successful sequence involved `/cgi-local//service-pack.pl?...&check=1`, then `check=0`, the local wrapper, and finally the local `.bin`. See [TECHNICAL-RECORD.md](TECHNICAL-RECORD.md).

**Never turn off, unplug Ethernet, enter standby or stop the server during flashing.** Rotel's manual warns of a **15–60 minute** possible duration and says the device should reboot automatically. If the UI becomes unresponsive, do not blindly flash again.

## The crucial Module-only Factory Default

After the first flash, our `NETWORK → Settings` entry would not open, despite Media Player and LAN ping continuing to work. The separate **remote-control SETUP** menu worked. On this RT-12:

1. Press **SETUP** on the remote (not NETWORK's Settings).
2. Select `3 FACTORY DEFAULT`.
3. Leave **`Main = NO`** (Main firmware is a separate subsystem).
4. Press **SEL/ENT**, then **DOWN** to highlight **`Module = YES`**.
5. Check `Main NO / Module YES` carefully. Press **SEL/ENT** to reset the **Module only**.
6. Afterwards, `NETWORK → Settings → Version → Service Pack` successfully reported **`v266-a-137-a-031`**.

This **erases module presets and network settings**. This exact menu sequence was essential in the successful case. Do not select `Main YES` or `SIPORT UPGRADE` as part of this process.

## Finish with the vendor's own updater

1. Set the radio back to **Auto DHCP YES**; stop the temporary Python server (`Control+C`).
2. From the radio's normal network connection, use `Settings → Upgrade Firmware` **without** any local DNS override. The tested unit discovered and installed **`v266-a-137-a-038`** from Rotel's own service.
3. Allow the vendor updater to finish fully, then verify `Settings → Version → Service Pack`.
4. Follow Rotel's recommendation to perform **Factory Default of Module only again** after the latest update.
5. Open `NETWORK → Internet Radio` and tune a station. The recovered unit displayed **Deep House Radio / 192 kbps MP3** and played normally.

## Troubleshooting / boundaries

- Older firmware can show `Finding Gateway`, `Reciva Server Not Responding`, or `No Internet` following the 2021 Reciva shutdown.
- A missing DHCP lease or invalid DNS must be fixed before attempting any firmware install; avoid guest Wi-Fi isolation.
- If macOS says `Address already in use`, identify which process owns TCP 80 or UDP 53. Do not kill system services.
- An RT-12's main `SETUP → VERSION` displays **Main software** (in this case `V1.26`); this is **not** the Internet Radio Service Pack version.
- SSH, Telnet, JTAG, board disassembly and alternate firmware patchers were **not used** in the successful recovery. The exposed Dropbear 0.43 port 22 on the tested module would not complete key exchange with modern macOS OpenSSH.
- If any firmware/hardware/checksum differs, or if something unexpected happens during installation, **stop and seek expert advice**. There is no guarantee of recovery.

## Sources and credit

Official [Rotel update instructions](https://www.rotel.com/sites/default/files/software/Internet_Radio_Update_Instructions.pdf), [release notes](https://www.rotel.com/sites/default/files/software/RCX_RT_Internet_Radio_Release_Notes.pdf), [RT-12 manual](https://www.rotel.com/sites/default/files/product/manuals/RT-12-OM.pdf), [Reciva upgrade guidance](https://rotel.com/blog/reciva-4), and [factory-reset FAQ for related models](https://rotel.com/en-ca/node/611).

Field test by **Gianpaolo**, RT-12 owner, with AI-assisted research and code. Only his first name appears publicly at his request. This repository is not affiliated with Rotel.
