# Technical record: one successful Rotel RT-12 recovery

Field test by **Gianpaolo** (first name only by choice). This page distinguishes **observations** from inferences. It is not a blanket compatibility claim.

## Hardware and software tested

| Item | Observed |
| --- | --- |
| Radio | Rotel RT-12 |
| Original Reciva SP | `v265-a-254-a-301-a-007` |
| Hardware ID in old update request | `hw=633` |
| Firmware's serial schema field | `sv=03` |
| Rotel Main software | `V1.26` (displayed as `V1.2.6`) |
| Intermediate SP | `v266-a-137-a-031` |
| Final SP | `v266-a-137-a-038` |
| Radio network | Wired Ethernet, DHCP via FRITZ!Box except while testing Mac DNS |
| Computer | macOS, Python 3.14.6 |
| Result | Internet Radio station playing; display showed `Deep House Radio / 192 kbps MP3` |
| Date | 2026-10-27 (Europe/Rome) |

The private case used Mac `192.168.178.83`, radio `192.168.178.114`, router `192.168.178.1`. These are non-routable example LAN addresses only. **The serial number and owner's macOS username have deliberately been omitted.**

## Official files and observed hashes

```text
sp265-a-254-a-301-a-007.bin         initial firmware image (not used for install)
sp266-a-137-a-031.bin               15,728,640 bytes
  MD5 cdee3d618f809d26069dfa21efe139c8
sp.266-a-137-a-031.tar.bz2          vendor's original upgrade wrapper
  SHA256 620ab7082c982404eb0eedcbbdb9145e2e865424a8454890ad7e210f4ae15335
sp.266-a-137-a-031.LOCAL-UNTESTED.tar.bz2   local wrapper used in this test
  SHA256 ff4789b37756e838903798e2d646d02e011678141ebd528c1e6e30622e6ed200
```

Original binaries were obtained from:

- <https://www.rotelupgrade.com/binaries/sp266-a-137-a-031.bin>
- <https://www.rotelupgrade.com/wrappers/sp.266-a-137-a-031.tar.bz2>

The wrapper contained `built-servicepack/install-me`, `built-servicepack/firmware_upgrade` and `built-servicepack/progress_simple`. Its install script downloaded the official 15 MiB firmware over HTTPS and validated its MD5 before invoking `firmware_upgrade -c -f mtd.bin`. It also had an explicit `zd1211` hardware-compatibility guard. The successful local archive **only substituted the HTTP download URL** with `http://192.168.178.83/sp266-a-137-a-031.bin`; original flash executable, MD5 verification and guard were preserved. **The vendor executable and modified archive are not distributed here.**

The radio's old updater contacted the legacy URL:

```text
Host: www.reciva.com
GET /cgi-local//service-pack.pl?serial=[redacted]&sp=v265-a-254-a-301-a-007&hw=633&sv=03&check=1
```

The local server first returned `none`, and the radio displayed **No Upgrade Available**. After explicitly enabling the update mode, the relevant log entries were:

```text
GET .../service-pack.pl?serial=[redacted]&sp=v265-a-254-a-301-a-007&hw=633&sv=03&check=1
  -> UPDATE OFFER (armed)
GET .../service-pack.pl?serial=[redacted]&sp=v265-a-254-a-301-a-007&hw=633&sv=03&check=0
  -> UPDATE WRAPPER URL (armed)
GET /sp.266-a-137-a-031.LOCAL-UNTESTED.tar.bz2
  -> 200 - local file
GET /sp266-a-137-a-031.bin
  -> 200 - local file
```

**Important:** HTTP `200` alone proves only that the file was offered, not that a complete flash succeeded. Later, `NETWORK → Settings → Version → Service Pack` definitively displayed **`v266-a-137-a-031`**, following the Module-only Factory Default.

## What went wrong temporarily and how it recovered

After the first firmware update, the radio reached its network menu and Media Player worked, but choosing **Settings** did not open the menu. Several reboots and attempts at entering Settings were unhelpful. SSH `Dropbear_0.43` was reachable on port 22, but a modern OpenSSH client could not complete the old handshake, even when temporarily offering legacy algorithms. **No SSH password or recovery commands were used.**

The effective step was the main Rotel remote-control **SETUP → FACTORY DEFAULT**, with separate lines for **Main** and **Module**:

1. Keep `Main = NO`.
2. Press `SEL/ENT`, then `DOWN` to highlight `Module = YES`.
3. Press `SEL/ENT` to perform a Module-only reset.

Afterwards, Settings opened and confirmed `v266-a-137-a-031`.

Using normal router DHCP (with the Mac server stopped), `Settings → Upgrade Firmware` then reached Rotel's own upgrade system, entered **Writing Firmware — Do Not Turn Off**, and completed. The display subsequently showed **`v266-a-137-a-038`**. A further **Module-only Factory Default** restored/activated the final streaming service. The user confirmed actual Internet Radio playback.

## Things NOT proven

- This is **one RT-12** field test. No independent reproduction on other units or hardware revisions.
- The project has not proven that it works with firmware other than `v265-a-254-a-301-a-007` or `hw` other than `633`.
- The generalized Python scripts and wrapper builder supplied here have **not** been used to flash another unit. The exact tested server script is also included for transparency.
- No claim of being the **first in the world** is supported. Other communities have documented attempts, including [a 2022 GitHub issue about the RT-12 and Reciva patching](https://github.com/jisotalo/reciva-radio-patching/issues/15).
- It is not known whether vendor update services or downloads will remain available indefinitely.

## Firmware versus main software

Do not confuse the **Rotel Main V1.26** shown under the general remote-control `SETUP → VERSION` with the Reciva **Service Pack v266-a-137-a-038** shown under `NETWORK → Settings → Version`.

The main software did **not** need another update in this case. Rotel documents V1.26 as the RT-12 Main release. The recovery only changed the Internet Radio Service Pack and module settings.

## Privacy and licensing

No user serial number, personal computer path, household public IP, keys or credentials are included. Example RFC1918 LAN IPs appear only because they were part of the reproduced test configuration. The software supplied here is original community tooling; the Rotel firmware/flash binaries are **not part of the distribution** and should be downloaded from the rights holder.
