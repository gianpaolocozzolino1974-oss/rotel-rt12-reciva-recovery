# Rotel RT-12 Reciva Recovery — a successful real-world case

**Italiano:** [Guida completa](GUIDA-IT.md) · **English:** [Full guide](GUIDE-EN.md) · [Technical record](TECHNICAL-RECORD.md)

On **27 October 2026**, **Gianpaolo** recovered his Rotel RT-12 with original `v265-a-254-a-301-a-007` Internet Radio software **without replacing its streaming module**. It ultimately reached **`v266-a-137-a-038`**, and Internet Radio playback was verified on the device; a photo shows **Deep House Radio, MP3 at 192 kbps**.

This is **one observed success**, not evidence of a universal solution, nor a claim to be the first ever recovery. Other hardware revisions or firmware releases might behave differently.

## Observed path

```text
RT-12 SP265-a-254-a-301-a-007
  → local Mac DNS + HTTP responder for legacy Reciva update request
  → official Rotel SP266-a-137-a-031 binary, official wrapper with ONE local URL change
  → SETUP → FACTORY DEFAULT → Module YES (Main NO)
  → SP266-a-137-a-031 verified on the display
  → normal DHCP + vendor's own upgrade service
  → SP266-a-137-a-038 verified on the display
  → SETUP → FACTORY DEFAULT → Module YES (Main NO)
  → Internet Radio playback verified
```

## Safety, scope and attribution

- **HIGH RISK:** Flashing the wrong software, interrupting a flash or running a modified installer can permanently disable the radio module. Do not experiment on a unit you cannot afford to lose.
- The exact *tested* environment was one RT-12, hardware code `633`, software `v265-a-254-a-301-a-007`, Rotel Main `V1.26`, wired Ethernet and a Mac running Python 3.14.6.
- `scripts/rotel_upgrade_server_tested.py` is an **unaltered copy of the script used successfully**, bound to the exact tested wrapper checksum and specific LAN configuration. It is **not portable without changes**.
- `scripts/rotel_upgrade_server_portable.py` and `scripts/build_local_wrapper.py` are **subsequent generalized adaptations, not device-tested**. Review the source and checksums independently before using them.
- Nothing is automatically installed by opening or extracting this repository. The server defaults to no-update diagnostic mode; flashing must be explicitly enabled.
- Never interrupt an active write. Rotel's manual states upgrades can take **15–60 minutes** and should reboot automatically at completion.
- Do not run `SIPORT UPGRADE`: that controls a different subsystem. Reset the **Module** only if appropriate and after backing up your presets; never confuse it with **Main**.
- **No Rotel copyrighted `.bin` or executable wrapper is distributed here.** Obtain originals from Rotel's website. The local builder transforms a copy on your own computer and preserves the vendor's flashing executable, MD5 check and Wi-Fi guard.
- Credit: **Gianpaolo**, RT-12 owner and field tester, with AI-assisted diagnosis and tooling. Only his first name is used publicly, by his request.

## Project contents

| File | Purpose |
| --- | --- |
| [GUIDA-IT.md](GUIDA-IT.md) | Full Italian walkthrough |
| [GUIDE-EN.md](GUIDE-EN.md) | Full English walkthrough |
| [TECHNICAL-RECORD.md](TECHNICAL-RECORD.md) | Verified facts, checksums, HTTP traces, uncertainties |
| [scripts/rotel_upgrade_server_tested.py](scripts/rotel_upgrade_server_tested.py) | Exact server source used in the successful case |
| [scripts/rotel_upgrade_server_portable.py](scripts/rotel_upgrade_server_portable.py) | Parameterized, **not device-tested** community variant |
| [scripts/build_local_wrapper.py](scripts/build_local_wrapper.py) | Rebuild a local-only wrapper from the original Rotel archive |
| [photos/rotel_rt12_playing_radio.jpg](photos/rotel_rt12_playing_radio.jpg) | Device displaying a working Internet Radio station |

## Official sources

- Rotel firmware archive: <https://www.rotelupgrade.com/binaries/>
- Original firmware: <https://www.rotelupgrade.com/binaries/sp266-a-137-a-031.bin>
- Original wrapper: <https://www.rotelupgrade.com/wrappers/sp.266-a-137-a-031.tar.bz2>
- Rotel Internet Radio upgrade instructions: <https://www.rotel.com/sites/default/files/software/Internet_Radio_Update_Instructions.pdf>
- Rotel release notes: <https://www.rotel.com/sites/default/files/software/RCX_RT_Internet_Radio_Release_Notes.pdf>
- Rotel RT-12 manual: <https://www.rotel.com/sites/default/files/product/manuals/RT-12-OM.pdf>
- Rotel Reciva module update guidance: <https://rotel.com/blog/reciva-4>

## Before attempting recovery

Read the full guide, confirm the **exact** installed service pack and hardware ID, and determine whether your device already supports Rotel's own upgrade server. This legacy workaround was only verified for `v265-a-254-a-301-a-007`, hardware `633`.

This repository is independent community documentation, **not endorsed or supported by Rotel**.
