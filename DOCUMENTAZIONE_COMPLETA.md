# =====================================================
# AMBULATORIO INFERMIERISTICO - CODICE COMPLETO
# =====================================================
# Questo file contiene la documentazione completa per
# ricreare l'applicativo identico
# =====================================================

## STRUTTURA PROGETTO

```
/app/
├── backend/
│   ├── server.py          # API FastAPI
│   ├── requirements.txt   # Dipendenze Python
│   └── .env              # Variabili ambiente
├── frontend/
│   ├── src/
│   │   ├── App.js        # Entry point React
│   │   ├── App.css       # Stili principali
│   │   ├── index.css     # Stili globali
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── SelectAmbulatorioPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── AgendaPage.jsx
│   │   │   ├── PazientiPage.jsx
│   │   │   ├── PatientDetailPage.jsx
│   │   │   ├── ModulisticaPage.jsx
│   │   │   └── StatistichePage.jsx
│   │   └── components/
│   │       ├── Layout.jsx
│   │       ├── BodyMap.jsx
│   │       ├── SchedaMedicazioneMED.jsx
│   │       ├── SchedaImpiantoPICC.jsx
│   │       └── SchedaGestionePICC.jsx
│   ├── package.json
│   └── .env
```

## CREDENZIALI UTENTI

| Username    | Password    | Ambulatori                        |
|-------------|-------------|-----------------------------------|
| Domenico    | infermiere  | PTA Centro + Villa delle Ginestre |
| Antonella   | infermiere  | PTA Centro + Villa delle Ginestre |
| Giovanna    | infermiere  | Solo PTA Centro                   |
| Oriana      | infermiere  | Solo PTA Centro                   |
| G.Domenico  | infermiere  | Solo PTA Centro                   |

## FUNZIONALITÀ PRINCIPALI

1. **Due Ambulatori Separati**
   - PTA Centro: gestisce PICC e MED
   - Villa delle Ginestre: solo PICC

2. **Agenda**
   - Slot 30 minuti (08:30-13:00, 15:00-17:00)
   - Max 2 pazienti per slot
   - Festività italiane + Palermo (Santa Rosalia 15/7)

3. **Pazienti**
   - Tipi: PICC, MED, PICC+MED
   - Stati: In Cura, Dimesso, Sospeso
   - Cartella clinica con anagrafica e schede

4. **Schede Medicazione**
   - MED: Fondo, Margini, Cute, Essudato, Medicazione
   - PICC: Impianto + Gestione Mensile

5. **Statistiche**
   - Export PDF e Excel
   - Confronto periodi

## DATABASE MONGODB

Collections:
- patients
- appointments
- schede_medicazione_med
- schede_impianto_picc
- schede_gestione_picc
- photos

## API ENDPOINTS

- POST /api/auth/login
- GET /api/patients
- POST /api/patients
- PUT /api/patients/{id}
- GET /api/appointments
- POST /api/appointments
- GET /api/statistics
- GET /api/documents
