# Recupero Rotel RT-12 dopo la chiusura Reciva

**Caso reale verificato il 27 ottobre 2026:** un RT-12 è passato da `v265-a-254-a-301-a-007` a `v266-a-137-a-031` usando un server temporaneo sul Mac, quindi a `v266-a-137-a-038` tramite aggiornamento Rotel. Le radio Internet sono tornate a funzionare.

> **AVVERTENZA:** procedura sperimentale con rischio concreto di danneggiare definitivamente il modulo streaming. Il successo riguarda **un solo esemplare**, codice hardware `633`, firmware iniziale esatto `v265-a-254-a-301-a-007`, software principale `V1.26`. Non utilizzare su altri firmware o hardware senza verifica indipendente. Non eseguire se non sei disposto a perdere il modulo. La variante parametrica dei programmi inclusi è **non collaudata su un altro apparecchio**.

## 1. Prima di cominciare

- Verifica sul dispositivo il **Service Pack completo** in `NETWORK → Settings → Version` e il codice hardware. La stringa deve essere esattamente `v265-a-254-a-301-a-007`, con `hw=633` e `sv=03` nella richiesta di aggiornamento. Altri modelli/revisioni possono richiedere file diversi.
- Usa preferibilmente un cavo Ethernet tra RT-12 e router. Evita alimentazione instabile.
- Sul Mac serve Python 3 recente. Il Mac e il Rotel devono essere nella stessa rete privata, **non nella rete ospiti**.
- Prepara una copia delle stazioni e delle impostazioni: il `Factory Default` cancella preselezioni e impostazioni di rete.
- Non devi modificare il DNS globale del router né scollegare altri dispositivi: cambia solo le impostazioni DNS del Rotel.

## 2. Scarica direttamente da Rotel

Scarica nella cartella `~/Downloads/RotelTest` i file:

1. [`sp266-a-137-a-031.bin`](https://www.rotelupgrade.com/binaries/sp266-a-137-a-031.bin)
2. [`sp.266-a-137-a-031.tar.bz2`](https://www.rotelupgrade.com/wrappers/sp.266-a-137-a-031.tar.bz2)

Sito indice: <https://www.rotelupgrade.com/binaries/>. In alcuni browser il vecchio sito presenta problemi di certificato HTTPS. Non disabilitare indiscriminatamente le verifiche TLS; controlla gli hash riportati sotto rispetto alla fonte originale.

Controlli su macOS:

```bash
md5 "$HOME/Downloads/RotelTest/sp266-a-137-a-031.bin"
shasum -a 256 "$HOME/Downloads/RotelTest/sp.266-a-137-a-031.tar.bz2"
```

Hash attesi:

```text
firmware BIN MD5:             cdee3d618f809d26069dfa21efe139c8
wrapper originale SHA-256:   620ab7082c982404eb0eedcbbdb9145e2e865424a8454890ad7e210f4ae15335
```

**Non usare file con hash diversi.** Il progetto non distribuisce questi binari di proprietà Rotel.

## 3. Prepara il wrapper per l'IP del tuo Mac

La procedura verificata ha modificato **solo l'URL del download del `.bin`** nello script `built-servicepack/install-me` dell'archivio originale; eseguibile di flashing, protezione per determinati chip Wi-Fi e controllo MD5 sono rimasti invariati.

Esempio: Mac `192.168.178.83`, Rotel `192.168.178.114`, FRITZ!Box `192.168.178.1`. **Sostituisci gli IP con i tuoi.** Dalla cartella del progetto:

```bash
python3 scripts/build_local_wrapper.py \
  --official-wrapper "$HOME/Downloads/RotelTest/sp.266-a-137-a-031.tar.bz2" \
  --firmware "$HOME/Downloads/RotelTest/sp266-a-137-a-031.bin" \
  --mac-ip 192.168.178.83 \
  --output-dir "$HOME/Downloads/RotelTest"
```

Il programma verifica gli hash originali, produce `sp.266-a-137-a-031.LOCAL-UNTESTED.tar.bz2` e stampa **il suo SHA-256**: salvalo per il passo successivo. Non modificare manualmente l'eseguibile di flashing.

**Nota di riproducibilità:** l'archivio modificato nel caso reale aveva SHA-256 `ff4789b37756e838903798e2d646d02e011678141ebd528c1e6e30622e6ed200` con URL `http://192.168.178.83/sp266-a-137-a-031.bin`. Un archivio ricreato successivamente può avere un diverso SHA-256 a causa dei metadati dell'archivio; in tal caso verificane contenuto e provenienza. La procedura con lo script builder incluso non è stata provata su un secondo Rotel.

## 4. Avvia il server in modalità SICURA

Il server combina un DNS limitato e un HTTP server. Intercetta `www.reciva.com` **solo dal Rotel autorizzato**, inoltrando le altre richieste DNS al router. Per default risponde `none` alla ricerca di aggiornamenti e non propone installazioni.

Se macOS segnala la porta `53` occupata, controlla `sudo lsof -nP -iUDP:53 -iTCP:80`. Nel caso testato era attiva **Condivisione Internet** sul Mac; è stata disabilitata temporaneamente dopo aver verificato che nessun dispositivo la utilizzasse. **Non terminare `mDNSResponder`**, non disattivare servizi necessari ad altri utenti.

Esempio (variante parametrica del progetto):

```bash
sudo python3 scripts/rotel_upgrade_server_portable.py \
  --mac-ip 192.168.178.83 \
  --rotel-ip 192.168.178.114 \
  --router-ip 192.168.178.1 \
  --directory "$HOME/Downloads/RotelTest"
```

Sul Rotel, in `NETWORK → Settings → Network Config → Edit Config`, imposta `Auto DHCP = NO` e soltanto sul Rotel configura:

| Campo | Esempio |
| --- | --- |
| IP | `192.168.178.114` |
| Subnet mask | `255.255.255.0` |
| Gateway | `192.168.178.1` |
| DNS primario | `192.168.178.83` (Mac) |

Verifica con `ping -c 4 192.168.178.114`, quindi prova `Settings → Upgrade Firmware`. In **modalità SICURA** deve apparire `No Upgrade Available`, con un log del server simile a `NO UPDATE (safe mode)`. Se questo non funziona, **fermarsi**.

## 5. Aggiornamento locale (alto rischio)

1. Ripristina `Auto DHCP = YES` sul Rotel prima di fermare il server diagnostico.
2. Ferma il server con `Control+C`.
3. Riavvialo con **`--arm-update`** e **`--wrapper-sha256`** impostato all'hash SHA-256 del wrapper creato al passo 3:

```bash
sudo python3 scripts/rotel_upgrade_server_portable.py \
  --mac-ip 192.168.178.83 \
  --rotel-ip 192.168.178.114 \
  --router-ip 192.168.178.1 \
  --directory "$HOME/Downloads/RotelTest" \
  --wrapper-sha256 INSERISCI_QUI_I_64_CARATTERI_SHA256 \
  --arm-update
```

4. Riconfigura sul **solo Rotel** IP statico e DNS del Mac come al passo 4.
5. Dopo il controllo del ping, vai in `Settings → Upgrade Firmware`. **Confermare YES può avviare la scrittura irreversibile**. Non farlo finché non hai verificato versione esatta, hardware, hash, alimentazione e backup.
6. La sequenza HTTP osservata nel caso reale è descritta in [TECHNICAL-RECORD.md](TECHNICAL-RECORD.md). Il Rotel ha scaricato il wrapper e poi il BIN, ha eseguito l'aggiornamento e ha richiesto un recupero del menu tramite reset Module.

**Non spegnere, non mettere in standby, non scollegare Ethernet e non terminare il server durante un'installazione.** Il manuale Rotel avverte che l'operazione può richiedere **15–60 minuti** e che il dispositivo dovrebbe riavviarsi automaticamente. In caso di schermata inattesa, documenta lo stato senza iniziare un secondo flashing alla cieca.

## 6. Ripristino del solo modulo dal menu generale

Nel caso verificato, dopo il passaggio a `v266-a-137-a-031`, l'elemento `Settings` del menu NETWORK non si apriva, pur con Media Player e ping funzionanti. Il comando risolutivo è stato il **Factory Default del Module** usando il menu generale del telecomando, non il menu NETWORK.

1. Premi **SETUP** sul telecomando (menu generale Rotel).
2. Apri `3 FACTORY DEFAULT`.
3. **Lascia `Main = NO`**.
4. Con `Main` su NO, premi **SEL/ENT**, poi **freccia GIÙ**: questo consente di evidenziare `Module = YES` sui modelli con lo stesso menu.
5. Premi **SEL/ENT** per eseguire il reset **solo dopo aver verificato `Main NO / Module YES`**.
6. Attendi il ritorno al menu e prova `NETWORK → Settings → Version → Service Pack`.

Nel caso reale è comparso `v266-a-137-a-031`: il flashing precedente era dunque riuscito e il reset aveva ripristinato l'accesso a Settings.

Rotel prevede il Factory Default dopo il cambio del servizio streaming. Questa operazione **cancella le impostazioni del modulo**, comprese rete e preselezioni. Non scegliere `Main YES` e non scegliere `SIPORT UPGRADE` per questa procedura.

## 7. Ultimo aggiornamento ufficiale e test radio

1. Ripristina `Auto DHCP = YES` sul Rotel e conferma che riceva il DNS dal router.
2. Ferma il server temporaneo sul Mac (`Control+C`).
3. Usa `NETWORK → Settings → Upgrade Firmware` normalmente, **senza server locale**. Nel caso reale il Rotel ha trovato e installato in autonomia `v266-a-137-a-038` dai server Rotel.
4. Attendi che l'installazione termini e verifica `Settings → Version → Service Pack = v266-a-137-a-038`.
5. Esegui nuovamente il **Factory Default del solo Module** dal menu SETUP generale (passo 6) per attivare correttamente il nuovo servizio.
6. Apri `NETWORK → Internet Radio`, seleziona una stazione e verifica il playback.

**Risultato reale:** Internet Radio funzionante, fotografia del display con *Deep House Radio — 192 kbps MP3*.

## Errori comuni e limiti

- `Finding Gateway / Reciva Server Not Responding`: firmware vecchio o server storico non raggiungibile; non è necessariamente un guasto Ethernet.
- `Timeout getting IP address` / `DNS servers invalid`: risolvere prima IP, subnet e DNS, preferendo Ethernet.
- `Port 53 in use` su Mac: controlla servizi locali come Condivisione Internet; **non forzare l'arresto di processi di sistema**.
- `Settings` non si apre dopo il flashing: nel caso verificato ha risposto al reset `SETUP → FACTORY DEFAULT → Module YES`.
- SSH/Telnet **non sono richiesti** dalla procedura. Il vecchio SSH Dropbear 0.43 del dispositivo di prova non ha completato lo scambio delle chiavi con OpenSSH moderno.
- Se non conosci l'hardware/firmware esatto, il dispositivo non risponde, oppure il wrapper non supera le verifiche, **fermati**. Il recupero di moduli realmente bloccati può richiedere assistenza specializzata o attrezzatura hardware.

## Crediti e fonti

**Credito: Gianpaolo**, proprietario del Rotel RT-12 e autore della prova pratica, con supporto AI per diagnosi e script. Per sua scelta viene pubblicato soltanto il nome. Software e firmware Rotel appartengono ai rispettivi titolari.

- [Rotel: istruzioni aggiornamento Internet Radio](https://www.rotel.com/sites/default/files/software/Internet_Radio_Update_Instructions.pdf)
- [Rotel: note di rilascio](https://www.rotel.com/sites/default/files/software/RCX_RT_Internet_Radio_Release_Notes.pdf)
- [Rotel: manuale RT-12](https://www.rotel.com/sites/default/files/product/manuals/RT-12-OM.pdf)
- [Rotel: aggiornamento software e hardware Reciva](https://rotel.com/blog/reciva-4)
- [Rotel: domanda/risposta reset modelli affini](https://rotel.com/en-ca/node/611)
