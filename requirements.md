# Ambulatorio Infermieristico - Requisiti e Architettura

## Problema Originale
Applicazione infermieristica professionale per la gestione di due ambulatori (PTA Centro e Villa delle Ginestre) con funzionalità di agenda, cartelle cliniche, modulistica e statistiche.

## Architettura Implementata

### Backend (FastAPI + MongoDB)
- **Autenticazione**: JWT con 5 utenti predefiniti
- **Endpoints**:
  - `/api/auth/login` - Login
  - `/api/patients` - CRUD pazienti
  - `/api/appointments` - Gestione appuntamenti agenda
  - `/api/schede-medicazione-med` - Schede medicazione MED
  - `/api/schede-impianto-picc` - Schede impianto PICC
  - `/api/schede-gestione-picc` - Schede gestione mensile PICC
  - `/api/photos` - Galleria foto pazienti
  - `/api/documents` - Modulistica
  - `/api/statistics` - Statistiche

### Frontend (React + Tailwind)
- **Pagine**:
  - Login
  - Selezione Ambulatorio
  - Dashboard (4 pulsanti principali)
  - Agenda (griglia giornaliera PICC/MED)
  - Pazienti (lista, creazione, cartella clinica)
  - Modulistica (documenti PDF)
  - Statistiche (report con confronto)

### Componenti Speciali
- BodyMap SVG interattivo per segnare lesioni
- SchedaMedicazioneMED con campi selezionabili multipli
- SchedaImpiantoPICC 
- SchedaGestionePICC mensile

## Funzionalità Completate
- [x] Login con 5 utenti predefiniti
- [x] Selezione ambulatorio (PTA Centro / Villa delle Ginestre)
- [x] Dashboard con 4 pulsanti
- [x] Agenda con slot 30min, sezioni PICC e MED
- [x] Creazione rapida pazienti (PICC/MED/PICC+MED)
- [x] Cartella clinica con anagrafica
- [x] Mappa lesioni SVG interattiva
- [x] Schede medicazione MED
- [x] Schede impianto PICC
- [x] Schede gestione mensile PICC
- [x] Galleria foto
- [x] Modulistica scaricabile
- [x] Statistiche con confronto periodi
- [x] Villa Ginestre solo PICC (niente MED)

## Prossimi Task
1. **Esportazione PDF/Excel** - Implementare generazione documenti
2. **Stampa schede** - Funzionalità print-friendly
3. **Export Word modificabile** - Per schede compilate
4. **Icone prestazioni** - Aggiungere icone dedicate nelle statistiche
5. **Festività Palermo** - Completare calcolo Pasqua dinamico
6. **Confronto foto** - Slider confronto evoluzione lesioni

## Credenziali
| Username | Password | Accesso |
|----------|----------|---------|
| Domenico | infermiere | PTA Centro + Villa Ginestre |
| Antonella | infermiere | PTA Centro + Villa Ginestre |
| Giovanna | infermiere | Solo PTA Centro |
| Oriana | infermiere | Solo PTA Centro |
| G.Domenico | infermiere | Solo PTA Centro |
