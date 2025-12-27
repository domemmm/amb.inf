# 🏥 Ambulatorio Infermieristico - Documentazione Completa

## Indice
1. [Panoramica](#panoramica)
2. [Requisiti di Sistema](#requisiti-di-sistema)
3. [Struttura del Progetto](#struttura-del-progetto)
4. [Installazione e Setup](#installazione-e-setup)
5. [Configurazione](#configurazione)
6. [Credenziali Utenti](#credenziali-utenti)
7. [Funzionalità Principali](#funzionalità-principali)
8. [API Endpoints](#api-endpoints)
9. [Schema Database MongoDB](#schema-database-mongodb)
10. [Componenti Frontend](#componenti-frontend)
11. [Avvio dell'Applicazione](#avvio-dellapplicazione)
12. [Troubleshooting](#troubleshooting)

---

## Panoramica

**Ambulatorio Infermieristico** è un'applicazione web full-stack per la gestione di ambulatori infermieristici. Supporta due tipi di pazienti:
- **PICC** (Peripherally Inserted Central Catheter) - Cateteri venosi centrali
- **MED** (Medicazioni) - Medicazioni e trattamenti generali

### Tecnologie Utilizzate
| Stack | Tecnologia |
|-------|------------|
| **Backend** | FastAPI (Python 3.11+) |
| **Frontend** | React 19 |
| **Database** | MongoDB |
| **Autenticazione** | JWT |
| **UI Framework** | Tailwind CSS + Shadcn/UI |

---

## Requisiti di Sistema

### Requisiti Minimi
- **Node.js**: v18.0.0 o superiore
- **Python**: 3.11 o superiore
- **MongoDB**: 6.0 o superiore
- **Yarn**: 1.22+ (package manager per frontend)
- **pip**: Package manager per Python

### Dipendenze Chiave
**Backend (Python):**
- FastAPI 0.110.1
- Motor 3.3.1 (driver MongoDB async)
- PyJWT 2.10.1
- Pydantic 2.6.4
- bcrypt 4.1.3

**Frontend (Node.js):**
- React 19.0.0
- React Router DOM 7.5.1
- Axios 1.8.4
- date-fns 4.1.0
- Lucide React (icone)

---

## Struttura del Progetto

```
/app/
├── backend/
│   ├── server.py           # Server FastAPI principale con tutti gli endpoint
│   ├── requirements.txt    # Dipendenze Python
│   └── .env                # Variabili d'ambiente backend
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                     # Componenti Shadcn/UI
│   │   │   ├── BodyMap.jsx             # SVG interattivo per mappatura lesioni
│   │   │   ├── Layout.jsx              # Layout principale app
│   │   │   ├── SchedaGestionePICC.jsx  # Tabella gestione mensile PICC
│   │   │   ├── SchedaImpiantoPICC.jsx  # Form impianto PICC
│   │   │   └── SchedaMedicazioneMED.jsx # Form medicazione MED
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx           # Pagina login
│   │   │   ├── SelectAmbulatorioPage.jsx # Selezione ambulatorio
│   │   │   ├── DashboardPage.jsx       # Home con 4 pulsanti principali
│   │   │   ├── AgendaPage.jsx          # Gestione agenda appuntamenti
│   │   │   ├── PazientiPage.jsx        # Lista pazienti
│   │   │   ├── PatientDetailPage.jsx   # Dettaglio paziente
│   │   │   ├── ModulisticaPage.jsx     # Documenti e moduli
│   │   │   └── StatistichePage.jsx     # Statistiche
│   │   ├── hooks/
│   │   │   └── use-toast.js
│   │   ├── lib/
│   │   │   └── utils.js                # Utility functions
│   │   ├── App.js                      # Componente principale React
│   │   ├── App.css
│   │   ├── index.js                    # Entry point
│   │   └── index.css                   # Stili Tailwind
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env                            # Variabili d'ambiente frontend
│
└── README_COMPLETO.md                  # Questo file
```

---

## Installazione e Setup

### 1. Clonare il Repository
```bash
git clone <repository-url>
cd app
```

### 2. Setup Backend
```bash
# Navigare nella cartella backend
cd backend

# Creare virtual environment (opzionale ma consigliato)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure: venv\Scripts\activate  # Windows

# Installare dipendenze
pip install -r requirements.txt
```

### 3. Setup Frontend
```bash
# Navigare nella cartella frontend
cd frontend

# Installare dipendenze (USARE YARN, NON NPM!)
yarn install
```

### 4. Configurare MongoDB
Assicurarsi che MongoDB sia installato e in esecuzione:
```bash
# Verificare stato MongoDB
mongod --version

# Avviare MongoDB (se non già in esecuzione)
sudo systemctl start mongod  # Linux
# oppure: brew services start mongodb-community  # Mac
```

---

## Configurazione

### File `.env` Backend (`/app/backend/.env`)
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="ambulatorio_infermieristico"
CORS_ORIGINS="*"
JWT_SECRET="ambulatorio-infermieristico-secret-key-2024"
```

### File `.env` Frontend (`/app/frontend/.env`)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```

**⚠️ IMPORTANTE:** Per la produzione, modificare:
- `CORS_ORIGINS` con i domini consentiti
- `JWT_SECRET` con una chiave sicura
- `REACT_APP_BACKEND_URL` con l'URL del server di produzione

---

## Credenziali Utenti

L'applicazione ha **5 utenti predefiniti** con permessi specifici per ambulatorio:

| Username | Password | Ambulatori Accessibili |
|----------|----------|------------------------|
| `Domenico` | `infermiere` | PTA Centro, Villa delle Ginestre |
| `Antonella` | `infermiere` | PTA Centro, Villa delle Ginestre |
| `Giovanna` | `infermiere` | Solo PTA Centro |
| `Oriana` | `infermiere` | Solo PTA Centro |
| `G.Domenico` | `infermiere` | Solo PTA Centro |

### Ambulatori
| ID | Nome | Tipi Pazienti |
|----|------|---------------|
| `pta_centro` | PTA Centro | PICC + MED |
| `villa_ginestre` | Villa delle Ginestre | Solo PICC |

---

## Funzionalità Principali

### 1. 📅 Agenda
- Visualizzazione giornaliera con slot da 30 minuti
- Orari: 08:30-13:00 (mattina), 15:00-17:00 (pomeriggio)
- Colonne separate per PICC e MED
- Gestione automatica giorni festivi (inclusa Santa Rosalia per Palermo)
- Navigazione rapida tra i giorni
- Creazione appuntamenti con selezione paziente e prestazioni multiple

### 2. 👥 Pazienti
- Creazione rapida paziente (Nome, Cognome, Tipo)
- Tre tipi: PICC, MED, PICC+MED
- Stati: In cura, Dimesso, Sospeso
- Ricerca per nome/cognome

### 3. 📋 Cartella Clinica Paziente

#### Per pazienti MED:
- **BodyMap SVG interattivo** per segnare posizione lesioni
- **Scheda Medicazione** con campi:
  - Fondo lesione (granuleggiante, fibrinoso, necrotico, infetto, biofilmato)
  - Margini (attivi, piantati, in estensione, a scogliera)
  - Cute perilesionale (integra, secca, arrossata, macerata, ipercheratosica)
  - Essudato (quantità e tipo)
  - Medicazione effettuata
  - Prossimo cambio

#### Per pazienti PICC:
- **Scheda Impianto** con dati del catetere
- **Scheda Gestione Mensile** (tabella con voci giornaliere)

### 4. 📄 Modulistica
- Documenti PDF scaricabili per MED e PICC
- Consensi informati
- Brochure informative

### 5. 📊 Statistiche
- Dati aggregati dall'agenda
- Filtri per anno/mese/tipo
- Conteggio accessi e pazienti unici
- Breakdown per prestazione

---

## API Endpoints

### Autenticazione
| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login utente |
| GET | `/api/auth/me` | Info utente corrente |

### Pazienti
| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/patients` | Lista pazienti |
| POST | `/api/patients` | Crea paziente |
| GET | `/api/patients/{id}` | Dettaglio paziente |
| PUT | `/api/patients/{id}` | Aggiorna paziente |
| DELETE | `/api/patients/{id}` | Elimina paziente |

### Appuntamenti
| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/appointments` | Lista appuntamenti |
| POST | `/api/appointments` | Crea appuntamento |
| PUT | `/api/appointments/{id}` | Aggiorna appuntamento |
| DELETE | `/api/appointments/{id}` | Elimina appuntamento |

### Schede Medicazione MED
| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/schede-medicazione-med` | Lista schede paziente |
| POST | `/api/schede-medicazione-med` | Crea nuova scheda |
| PUT | `/api/schede-medicazione-med/{id}` | Aggiorna scheda |

### Schede PICC
| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/schede-impianto-picc` | Lista schede impianto |
| POST | `/api/schede-impianto-picc` | Crea scheda impianto |
| GET | `/api/schede-gestione-picc` | Lista schede gestione mensile |
| POST | `/api/schede-gestione-picc` | Crea scheda gestione |
| PUT | `/api/schede-gestione-picc/{id}` | Aggiorna scheda gestione |

### Foto
| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/photos` | Lista foto paziente |
| POST | `/api/photos` | Upload foto |
| DELETE | `/api/photos/{id}` | Elimina foto |

### Statistiche
| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/statistics` | Ottieni statistiche |
| GET | `/api/statistics/compare` | Compara periodi |

### Calendario
| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/calendar/holidays` | Giorni festivi |
| GET | `/api/calendar/slots` | Slot orari disponibili |

---

## Schema Database MongoDB

### Collection: `patients`
```javascript
{
  id: "uuid",
  nome: "string",
  cognome: "string",
  tipo: "PICC" | "MED" | "PICC_MED",
  ambulatorio: "pta_centro" | "villa_ginestre",
  status: "in_cura" | "dimesso" | "sospeso",
  data_nascita: "YYYY-MM-DD",
  codice_fiscale: "string",
  telefono: "string",
  email: "string",
  medico_base: "string",
  anamnesi: "string",
  terapia_in_atto: "string",
  allergie: "string",
  lesion_markers: [{ x: number, y: number, note: "string" }],
  discharge_reason: "string",
  discharge_notes: "string",
  suspend_notes: "string",
  created_at: "ISO datetime",
  updated_at: "ISO datetime"
}
```

### Collection: `appointments`
```javascript
{
  id: "uuid",
  patient_id: "uuid",
  patient_nome: "string",
  patient_cognome: "string",
  ambulatorio: "pta_centro" | "villa_ginestre",
  data: "YYYY-MM-DD",
  ora: "HH:MM",
  tipo: "PICC" | "MED",
  prestazioni: ["string"],
  note: "string",
  completed: boolean,
  created_at: "ISO datetime"
}
```

### Collection: `schede_medicazione_med`
```javascript
{
  id: "uuid",
  patient_id: "uuid",
  ambulatorio: "string",
  data_compilazione: "YYYY-MM-DD",
  fondo: ["granuleggiante", "fibrinoso", ...],
  margini: ["attivi", "piantati", ...],
  cute_perilesionale: ["integra", "secca", ...],
  essudato_quantita: "assente" | "moderato" | "abbondante",
  essudato_tipo: ["sieroso", "ematico", "infetto"],
  medicazione: "string",
  prossimo_cambio: "YYYY-MM-DD",
  firma: "string",
  foto_ids: ["uuid"],
  created_at: "ISO datetime"
}
```

### Collection: `schede_impianto_picc`
```javascript
{
  id: "uuid",
  patient_id: "uuid",
  ambulatorio: "string",
  data_impianto: "YYYY-MM-DD",
  tipo_catetere: "string",
  sede: "string",
  braccio: "dx" | "sn",
  vena: "basilica" | "cefalica" | "brachiale",
  exit_site_cm: "string",
  ecoguidato: boolean,
  igiene_mani: "string",
  precauzioni_barriera: boolean,
  disinfettante: "string",
  sutureless_device: boolean,
  medicazione_trasparente: boolean,
  controllo_rx: boolean,
  controllo_ecg: boolean,
  modalita: "emergenza" | "urgenza" | "elezione",
  motivazione: "string",
  operatore: "string",
  note: "string",
  allegati: ["string"],
  created_at: "ISO datetime"
}
```

### Collection: `schede_gestione_picc`
```javascript
{
  id: "uuid",
  patient_id: "uuid",
  ambulatorio: "string",
  mese: "YYYY-MM",
  giorni: {
    "1": { lavaggio_mani: "Sì", ispezione: "OK", ... },
    "2": { ... },
    // ...fino a 31
  },
  note: "string",
  created_at: "ISO datetime",
  updated_at: "ISO datetime"
}
```

### Collection: `photos`
```javascript
{
  id: "uuid",
  patient_id: "uuid",
  ambulatorio: "string",
  tipo: "MED" | "PICC",
  descrizione: "string",
  data: "YYYY-MM-DD",
  image_data: "base64 string",
  created_at: "ISO datetime"
}
```

---

## Componenti Frontend

### Componenti Principali

| File | Descrizione |
|------|-------------|
| `App.js` | Entry point, routing, context providers |
| `Layout.jsx` | Layout principale con sidebar e header |
| `BodyMap.jsx` | SVG interattivo corpo umano per mappatura lesioni |
| `SchedaGestionePICC.jsx` | Tabella gestione mensile PICC |
| `SchedaImpiantoPICC.jsx` | Form dati impianto PICC |
| `SchedaMedicazioneMED.jsx` | Form scheda medicazione |

### Pagine

| File | Descrizione |
|------|-------------|
| `LoginPage.jsx` | Form login |
| `SelectAmbulatorioPage.jsx` | Selezione ambulatorio |
| `DashboardPage.jsx` | Home con 4 pulsanti (Agenda, Pazienti, Modulistica, Statistiche) |
| `AgendaPage.jsx` | Griglia agenda con slot orari |
| `PazientiPage.jsx` | Lista pazienti con filtri |
| `PatientDetailPage.jsx` | Dettaglio paziente con tabs |
| `ModulisticaPage.jsx` | Lista documenti scaricabili |
| `StatistichePage.jsx` | Dashboard statistiche |

---

## Avvio dell'Applicazione

### Sviluppo Locale

**Terminale 1 - Backend:**
```bash
cd /app/backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminale 2 - Frontend:**
```bash
cd /app/frontend
yarn start
```

L'applicazione sarà disponibile su:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001
- **Documentazione API:** http://localhost:8001/docs

### Produzione

**Backend con Gunicorn:**
```bash
cd /app/backend
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

**Frontend Build:**
```bash
cd /app/frontend
yarn build
# I file statici saranno in /app/frontend/build
```

---

## Troubleshooting

### Errori Comuni

**1. Errore MongoDB Connection:**
```
Error: Connection refused to localhost:27017
```
**Soluzione:** Verificare che MongoDB sia in esecuzione.

**2. CORS Error:**
```
Access-Control-Allow-Origin missing
```
**Soluzione:** Verificare `CORS_ORIGINS` nel `.env` backend.

**3. Token JWT scaduto:**
```
Token scaduto / 401 Unauthorized
```
**Soluzione:** Effettuare nuovo login.

**4. Errore "removeChild" React:**
Se si verifica un errore DOM legato a `removeChild`, assicurarsi che `React.StrictMode` sia rimosso da `index.js`.

### Log e Debug

**Log Backend:**
```bash
tail -f /var/log/supervisor/backend.err.log
```

**Log Frontend:**
Aprire la console del browser (F12 → Console)

---

## Note Aggiuntive

### Giorni Festivi Italiani
L'applicazione include automaticamente i giorni festivi italiani, inclusa **Santa Rosalia (15 luglio)** specifica per Palermo.

### Limitazioni Slot Agenda
- Max 2 pazienti per slot per tipo (PICC/MED)
- Villa delle Ginestre gestisce solo pazienti PICC

### Sicurezza
- Token JWT con scadenza 24 ore
- Password hashata (per produzione, usare bcrypt)
- Verifica permessi ambulatorio su ogni richiesta API

---

## Contatti e Supporto

Per assistenza tecnica o segnalazione bug, creare una issue nel repository.

---

**Versione:** 1.0.0  
**Ultimo aggiornamento:** Dicembre 2024  
**Autore:** Ambulatorio Infermieristico Team
