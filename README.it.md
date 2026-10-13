# CustomGPT-to-Skill

<p align="center">
  <img src="docs/assets/logo.svg" alt="Logo CustomGPT-to-Skill" width="180">
</p>

<p align="center">
  <a href="#installazione"><img alt="Installa con npx" src="https://img.shields.io/badge/install-npx%20skills%20add-CB3837"></a>
  <img alt="Versione skill" src="https://img.shields.io/badge/skill-10.7.0-2F6BFF">
  <a href="LICENSE"><img alt="Licenza: MIT" src="https://img.shields.io/badge/licenza-MIT-green"></a>
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/language-english-2F6BFF"></a>
</p>

> ## I Custom GPT vengono dismessi
>
> OpenAI ha programmato la dismissione dei **Custom GPT per l'11 dicembre 2026**. Dopo quella data i GPT e le loro pagine diventano inaccessibili. Per i workspace Enterprise con una proroga approvata la data è l'11 febbraio 2027. Date e disponibilità possono variare per account o workspace: segui l'avviso nel tuo account. [[1]](#fonti)
>
> Il percorso consigliato da OpenAI è il flusso integrato **Migrate to plugin**. Per molti GPT è la risposta giusta. Per altri il plugin non è la destinazione migliore. In quel caso serve una conversione **Custom GPT → Skill**, ed è ciò che fa questo repository.

🇬🇧 [Read in English](README.md)

*I fatti su prodotti di terze parti sono stati verificati il 13 ottobre 2026; vedi [Fonti](#fonti).*

---

## Cosa succede l'11 dicembre

Le FAQ di migrazione di OpenAI descrivono cosa fa e cosa non fa la migrazione integrata. [[1]](#fonti)

| | |
|---|---|
| **Viene trasferito** | Le istruzioni del GPT diventano una skill dentro il nuovo plugin. I file Knowledge vengono copiati nei file di riferimento del plugin. Le app collegate vengono aggiunte al plugin come app. La migrazione usa l'ultima versione *pubblicata*. |
| **Non viene trasferito** | Le custom action. Il modello selezionato. Le impostazioni di condivisione (il plugin nasce privato e gli utenti esistenti non ottengono accesso). Le conversazioni esistenti non passano al plugin: OpenAI dice che restano accessibili dopo la dismissione. |
| **Da sapere** | OpenAI avverte che un plugin migrato può rispondere in modo diverso, quindi va testato. Il GPT originale diventa di sola lettura dopo la migrazione. Rendere pubblico un plugin richiede un processo di sottomissione separato. Solo il creatore (o un admin del workspace Enterprise) può migrare un GPT. |

Google fa una mossa simile: i Gemini Gems vengono sostituiti dalle Skills e Google inizierà a migrarli automaticamente il 17 novembre 2026. [[2]](#fonti) Maggiori dettagli in [docs/migration-landscape.md](docs/migration-landscape.md).

## Due strade

**1. Migrazione integrata a plugin (OpenAI).** Parti da qui quando il GPT è soprattutto istruzioni più file Knowledge, ti servono solo ChatGPT o Codex e puoi accettare di ritestare e ricondividere. Il GPT originale resta utilizzabile fino alla dismissione (di sola lettura dopo la migrazione).

**2. Conversione in Skill (questo repository).** Valutala quando vale almeno uno di questi punti:

- **Ti serve lo stesso pacchetto oltre ChatGPT.** `SKILL.md` è un formato basato su file che la documentazione API di OpenAI descrive come compatibile con lo standard aperto Agent Skills, e gli agenti dichiarativi di Microsoft 365 Copilot accettano skill personalizzate come zip con `SKILL.md` (anteprima, programma Frontier). Controlla i limiti di ciascun runtime. [[5]](#fonti) [[6]](#fonti)
- **Il GPT è stateful, conversazionale o socratico** e la persona deve sopravvivere ai follow-up. Il convertitore riconosce questi GPT, ti chiede come trattare la deriva della persona e può aggiungere un lock di sessione consapevole dell'host. Non dichiara mai di poter forzare la re-invocazione della skill da parte dell'host.
- **Il GPT ha un "control plane" a più livelli** (file che decidono cosa caricare, in che ordine e cosa prevale). Il convertitore classifica ogni artefatto e conserva sia l'originale canonico sia una forma eseguibile a runtime.
- **Vuoi possedere e verificare il risultato.** Una skill è una cartella di file di testo che puoi tenere in Git, rivedere, calcolare in hash e testare. I file Knowledge sono preservati byte per byte con un manifest SHA-256 e il convertitore include una suite di regressione.

Un plugin può contenere skill, e una skill può essere caricata da sola. [[3]](#fonti) [[4]](#fonti)

## Cosa fa questa skill

Le dai l'export di un Custom GPT (uno ZIP, oppure istruzioni più file Knowledge e un'icona opzionale). Poi:

1. **Inventaria** ogni file sorgente con il suo SHA-256 e individua la vera fonte delle istruzioni dal contenuto, non dal nome del file.
2. **Ti pone domande in linguaggio semplice.** Ogni decisione arriva con opzioni, motivazione e conseguenza pratica. Nulla viene generato finché non confermi. Le domande riguardano la strategia di control plane, l'eventuale validation harness, se il GPT è conversazionale e come trattare la deriva della persona, come gestire i file Knowledge DOCX e cosa fare se il pacchetto è troppo grande.
3. **Implementa le soluzioni scelte:** un `SKILL.md` che conserva le istruzioni, Knowledge preservata byte per byte con manifest, icone normalizzate, metadati UI per ChatGPT/Codex (`agents/openai.yaml`) e solo i file di supporto che aiutano davvero.
4. **Valida** il risultato con un report parametri deterministico, controlli strutturali, confronto dei manifest sorgente/target e controllo dimensione, poi consegna `skill.zip` e un dashboard di conversione che separa le validazioni *eseguite* da quelle *non eseguite*.

L'obiettivo è la **equivalenza funzionale di istruzioni, conoscenza e flusso di controllo**: la skill convertita riproduce ciò che il tuo GPT doveva fare, insieme alla sua Knowledge e ai suoi file di controllo. Testala su prompt reali, come dopo qualsiasi migrazione.

### Ambito e limiti attuali

- **Le Custom Action** sono segnalate come conversion gap espliciti. Una skill può includere uno script che chiama l'API dell'Action dove il runtime consente l'accesso alla rete; la generazione di tali script non fa ancora parte del convertitore. [[3]](#fonti) [[6]](#fonti)
- **Le capacità non supportate** sono segnalate come conversion gap. Il convertitore lavora su ciò che la sorgente definisce, quindi connettori, endpoint e segreti non vengono mai inventati.
- **Dimensione del pacchetto:** la soglia è 25 MiB compressi di default (`--limit-mib` la modifica). Oltre la soglia scegli tu: prima lossless, esternalizzare con riferimento, lossy con approvazione, oppure annullare. I DOCX restano originali; un mirror testuale è un aiuto opzionale al retrieval.
- **Le funzioni di piattaforma** come distribuzione sul GPT Store, memoria di piattaforma, voce e selezione del modello appartengono alla piattaforma, non al pacchetto skill.

## Skill o plugin: i compromessi

Prima i fatti verificati, poi l'esperienza dell'autore.

| | Plugin (OpenAI) | Skill (output di questo convertitore) |
|---|---|---|
| Cos'è | Raggruppa skill, app collegate, template di app ed estensioni [[4]](#fonti) | Istruzioni, esempi e codice in una cartella con `SKILL.md` [[3]](#fonti) |
| Custom Action | Vanno ricostruite, per esempio come app o server MCP personalizzato [[1]](#fonti) | Segnalate come conversion gap; uno script incluso può chiamare l'API dove il runtime consente l'accesso alla rete |
| App basate su MCP | Le app MCP locali girano su ChatGPT Desktop ma non su web o mobile; altre opzioni sono un'app del workspace o un'app ospitata su ChatGPT Sites [[4]](#fonti) | Non necessario per skill di sole istruzioni e conoscenza |
| Condivisione | I nuovi plugin nascono privati; la pubblicazione richiede una sottomissione [[1]](#fonti) [[4]](#fonti) | Condividi il pacchetto o il repository; la disponibilità dipende da prodotto e piano [[3]](#fonti) |
| Dimensione | Vedi la documentazione dei plugin per i limiti attuali | Soglia del convertitore: 25 MiB compressi di default. La Skills API di OpenAI documenta 50 MB per zip, 25 MB per file decompresso e 500 file; Agent Builder di Microsoft documenta 50 MB per zip e fino a 8 skill per agente. [[5]](#fonti) [[6]](#fonti) |
| Disponibilità | L'accesso ai plugin dipende da piano, workspace e regione [[4]](#fonti) | In ChatGPT le skill personali sono documentate per utenti Business, Enterprise, Healthcare ed Edu idonei, secondo le impostazioni del workspace. Controlla il tuo piano. [[3]](#fonti) |

**Note dell'autore (dall'esperienza con GPT conversazionali e socratici):** le skill convertite girano un po' più lente dei GPT originali. Chiunque installi una skill può leggerne istruzioni e file, quindi tieni i segreti fuori. La distribuzione è meno efficiente della condivisione di un link a un GPT. Per i GPT conversazionali stateful abbiamo scelto le skill perché la semantica si trasferisce intatta.

> Le skill girano con i permessi dell'agente che le carica. Rivedi qualsiasi skill, comprese le conversioni prodotte da questa, prima di installarla. Anche OpenAI analizza le skill caricate e ti invita a rivederle di persona. Vedi [SECURITY.md](SECURITY.md). [[3]](#fonti)

## Flusso

```text
Export del Custom GPT
  ↓
Inventario sorgente (SHA-256)
  ↓
Human-in-Control: Decision Awareness Guide → conferma esplicita
  ↓
Gate: control plane · harness · conversazionale · DOCX
  ↓
Conversion Parameter Report (deterministico, mostrato all'utente)
  ↓
Generazione del target (Skill + Knowledge preservata + icone)
  ↓
Regressione · validazione strutturale · confronto manifest · size gate
  ↓
skill.zip + dashboard di conversione
```

## Installazione

Installa direttamente da GitHub con la CLI aperta `skills`:

```bash
npx skills add jumpifequal/customgpt-to-skill
```

Controlla cosa rileva la CLI prima di installare:

```bash
npx skills add jumpifequal/customgpt-to-skill --list
```

Installazione globale per un agente specifico (gli identificatori sono elencati dalla CLI):

```bash
npx skills add jumpifequal/customgpt-to-skill -g -a codex -y
npx skills add jumpifequal/customgpt-to-skill -g -a claude-code -y
```

Installazione da clone locale:

```bash
git clone https://github.com/jumpifequal/customgpt-to-skill.git
cd customgpt-to-skill
npx skills add .
```

Verifica il repository prima dell'installazione o di un contributo:

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_repo.py
```

> `npx skills add` installa la skill; il repository non richiede `npm install`. Le icone sorgente SVG richiedono inoltre `cairosvg` (non necessario per la suite di test). Puoi anche caricare la cartella della skill come zip dove il tuo prodotto accetta skill.

## Avvio rapido

Allega l'export del tuo Custom GPT (oppure istruzioni, file Knowledge e un'icona opzionale) e scrivi:

```text
Use $customgpt-to-skill to convert my attached Custom GPT export into a validated Universal Skill package.
```

Trigger naturali tipici: *converti, porta, migra o ricostruisci questo Custom GPT come Skill*; *trasforma questo export GPT in una skill*; *rilancia la conversione GPT→skill con i nuovi file Knowledge*.

## Esempio pratico

*Illustrativo e abbreviato: formulazioni, file e valori dipendono dal tuo GPT.*

**1. Prepara l'input.** Metti in un unico ZIP le istruzioni del GPT e i file Knowledge che avevi caricato:

```text
contract-reviewer-gpt.zip
├── system_prompt.md          # le istruzioni del GPT
└── knowledge/
    ├── clause-playbook.docx
    ├── risk-matrix.csv
    └── glossary.md
```

**2. Invoca la skill** in un runtime dove è installata, con lo ZIP allegato:

```text
Usa $customgpt-to-skill per convertire l'export allegato del Custom GPT (contract-reviewer-gpt.zip) in un pacchetto Universal Skill validato.
```

**3. Rivedi la Decision Awareness Guide.** La skill inventaria i quattro file (percorso, dimensione, SHA-256), poi espone ogni decisione con opzioni e conseguenze:

```text
Inventario: 4 file. Istruzioni: system_prompt.md (individuato dal contenuto).
Knowledge: clause-playbook.docx, risk-matrix.csv, glossary.md.

Control plane: i tre file Knowledge sono PASSIVE_KB (evidenza, nessuna regola di routing o precedenza).
Classificazione conversazionale: NON_CONVERSATIONAL_CANDIDATE (task di revisione one-shot, nessuna persistenza di persona).
Harness: le istruzioni definiscono già schema di output e fallback, quindi vengono preservate (PRESERVE_EXISTING).

Decisione DOCX per clause-playbook.docx:
  PRESERVE_ORIGINAL_ONLY  tiene il file byte per byte; il retrieval può richiedere strumenti per documenti a runtime.
  PRESERVE_PLUS_DERIVED   (consigliata) tiene l'originale e aggiunge un mirror testuale per il retrieval.
  CONVERT_AND_REPLACE     pacchetto più piccolo; la semantica propria del DOCX può andare persa.

Rispondi CONFIRM ALL RECOMMENDED, oppure dimmi cosa cambiare.
```

**4. Conferma.**

```text
CONFIRM ALL RECOMMENDED
```

**5. Controlla il Conversion Parameter Report e il dashboard.** Prima di generare qualsiasi cosa, la skill mostra i parametri che userà:

| Parametro | Valore scelto | Origine | Motivazione | Conseguenza pratica |
|---|---|---|---|---|
| File DOCX nella Knowledge | 1 | DETECTED | `clause-playbook.docx` trovato nella sorgente | Si applica il gate DOCX |
| Strategia DOCX | `PRESERVE_PLUS_DERIVED` | HUMAN | Mantiene la fedeltà e dà al runtime un mirror testuale ricercabile | Originale tenuto byte per byte; il mirror è un aiuto all'accesso |
| Dimensione stimata del pacchetto | sotto 25 MiB | DERIVED | Dimensione compressa misurata dal size guard | Nessuna decisione di riduzione necessaria |

Poi consegna `skill.zip` e un dashboard di conversione: conteggio file sorgente e target, modalità di preservazione della Knowledge e stato del manifest, validazioni eseguite e non eseguite, capacità non supportate elencate come conversion gap (per esempio le custom action) e rischi residui.

**6. Installa e testa.** Carica `skill.zip` dove il tuo prodotto accetta skill (in ChatGPT: Skills → Create → Upload from your computer, secondo piano e impostazioni del workspace [[3]](#fonti)). Poi esegui i prompt che usi di solito con il tuo GPT e confronta le risposte con l'originale, come consiglia anche OpenAI dopo una migrazione a plugin. [[1]](#fonti)

## Moduli di supporto

| Script | Scopo |
|---|---|
| `build_inventory.py` | Inventario deterministico sorgente/target con hash |
| `kb_preserve.py` | Migrazione Knowledge byte per byte e manifest |
| `icon_convert.py` | Normalizzazione sicura delle icone PNG/SVG |
| `detect_conversational_gpt.py` | Classificazione conversazionale consultiva |
| `harness_profile_selector.py` | Raccomandazione consultiva della famiglia di harness |
| `decision_gate_guard.py` | Valida tutti i gate umani |
| `render_parameter_report.py` | Genera e valida il Conversion Parameter Report |
| `control_plane_guard.py` | Valida mappa di control plane e parità |
| `conversation_lock_guard.py` | Valida le integrazioni di conversation lock |
| `package_size_guard.py` | Dimensione compressa stimata rispetto al limite (default 25 MiB) |
| `validate_converted_skill.py` | Validazione strutturale e semantica della skill generata |
| `regression_self_test.py` | Self-regressione del convertitore (F001–F031) |

## Struttura del repository

```text
customgpt-to-skill/
├── .github/
│   └── workflows/
│       └── validate.yml
├── agents/
│   └── openai.yaml
├── assets/
│   ├── icon.png          # icona UI della skill (64×64)
│   └── icon.svg
├── docs/
│   ├── assets/
│   │   ├── logo.png      # logo del repository
│   │   └── logo.svg
│   ├── architecture.md
│   ├── decision-gates.md
│   ├── examples.md
│   ├── migration-landscape.md
│   └── runtime-tools.md
├── references/           # policy normative di conversione
├── scripts/              # helper deterministici e suite di regressione
├── tools/
│   └── validate_repo.py
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── README.it.md
├── SECURITY.md
├── SKILL.md              # punto di ingresso
└── requirements-dev.txt
```

## Documentazione

- [Panorama delle migrazioni (con fonti e date)](docs/migration-landscape.md)
- [Architettura](docs/architecture.md)
- [Decision gates](docs/decision-gates.md)
- [Runtime tools](docs/runtime-tools.md)
- [Esempi d'uso](docs/examples.md)
- [Changelog](CHANGELOG.md)

La documentazione tecnica in `docs/` è in inglese; `SKILL.md` e `references/` restano la fonte canonica.

## Vincoli di progetto

La skill preferisce deliberatamente:

- una decisione umana a un default silenzioso;
- originali preservati a conversioni comode;
- conversion gap espliciti a capacità inventate;
- regressione guidata dagli invarianti a una validità solo di schema;
- "validazione non eseguita" a un "validato" non verificabile.

## Versione

Skill `10.7.0`, vedi [CHANGELOG.md](CHANGELOG.md).

Autore: **Enrico Frumento**

## Licenza

MIT. Vedi [LICENSE](LICENSE).

## Fonti

Verificate il 13 ottobre 2026.

1. OpenAI Help Center, [Custom GPT retirement and migration FAQ](https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq).
2. TechCrunch, [Google is killing off Gemini's Gems in favor of 'skills'](https://techcrunch.com/2026/09/28/google-is-killing-off-geminis-gems-in-favor-of-skills/), 28 settembre 2026.
3. OpenAI Help Center, [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt).
4. OpenAI Help Center, [Plugins in ChatGPT](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt).
5. Microsoft Learn, [Add custom skills to your declarative agent in Agent Builder (preview)](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-skills).
6. OpenAI Developers, [Skills (API guide)](https://developers.openai.com/api/docs/guides/tools-skills).
