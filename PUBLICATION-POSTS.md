# Messaggi pronti per la pubblicazione / Ready-to-post announcements

Sostituisci `[LINK_GITHUB]` solo **dopo** aver pubblicato il repository. Il proprietario ha scelto di essere citato pubblicamente soltanto come **Gianpaolo**. Non allegare log con seriale o username macOS.

## Italiano — forum Hi-Fi / gruppi Facebook

**Rotel RT-12: radio Internet recuperata senza sostituire il modulo Reciva!**

Il 27 ottobre 2026 Gianpaolo è riuscito, con supporto tecnico AI, a riportare online il suo Rotel RT-12 fermo al vecchio firmware `V265-a-254-a-301-a-007`, dopo la chiusura dei server Reciva.

Partendo dai firmware originali dell'archivio Rotel, abbiamo realizzato un server locale temporaneo sul Mac per installare la versione intermedia `V266-a-137-a-031`. Dopo un ripristino *Factory Default* del solo modulo Internet Radio, l'apparecchio ha potuto aggiornarsi autonomamente dai server ufficiali Rotel fino alla versione `V266-a-137-a-038`.

**Risultato verificato: le radio Internet funzionano nuovamente.** La prova fotografica mostra Deep House Radio in riproduzione a 192 kbps MP3.

Abbiamo preparato una guida in italiano e inglese con codice, checksum, foto e problemi incontrati: [LINK_GITHUB]

⚠️ È un caso riuscito su **un solo RT-12**, non una garanzia per altri apparecchi. La procedura di flashing è rischiosa e potrebbe rendere inutilizzabile il modulo; chi volesse provarla deve leggere prima tutte le avvertenze. Non siamo affiliati a Rotel e non distribuiamo firmware proprietari.

Se altri proprietari hanno recuperato modelli simili, ci farebbe piacere confrontare le esperienze.

## English — GitHub / Reddit / Hi-Fi forums

**Success story: Rotel RT-12 Internet Radio restored after the Reciva shutdown — no replacement module!**

On October 27, 2026, Gianpaolo recovered his RT-12, with AI-assisted technical support, from the old `V265-a-254-a-301-a-007` Reciva service pack.

We used Rotel's original firmware files, a small temporary DNS/HTTP server on a Mac, and a locally adjusted version of the vendor's original installer wrapper to reach `V266-a-137-a-031`. A *Module-only Factory Default* restored access to the radio's Settings menu. We then used Rotel's own update service to reach `V266-a-137-a-038`, performed the recommended Module-only reset, and confirmed **working Internet Radio playback** (Deep House Radio, 192 kbps MP3).

We documented the commands, source code, checksums, limitations, photos and troubleshooting in English and Italian: [LINK_GITHUB]

⚠️ This is **one verified field recovery**, not a universal fix and not a claim to have been first. Flashing carries a real permanent-brick risk. The scripts generalized for other LAN IPs have not been tested on another radio. No copyrighted Rotel firmware binaries are redistributed, and this is not official Rotel support.

I'd love to hear from other RT-12 and Reciva owners who have attempted similar recoveries.

## Suggested repository metadata

- **Repository name:** `rotel-rt12-reciva-recovery`
- **Short description:** `One verified RT-12 Reciva recovery: legacy firmware bridge, official upgrade to V266-a-137-a-038, and working Internet Radio.`
- **Topics:** `rotel`, `rt12`, `reciva`, `internet-radio`, `firmware-recovery`, `macos`, `python`, `hifi`
- **Visibility:** public, only after checking privacy and license notices.
