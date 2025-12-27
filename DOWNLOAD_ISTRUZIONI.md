# 📥 Come Scaricare il Codice - Ambulatorio Infermieristico

## Metodo 1: Download dalla Piattaforma Emergent (Consigliato)

### Passo 1: Accedere all'opzione Download
1. Nella chat di Emergent, cerca il menu delle opzioni (solitamente un'icona ⋮ o ⚙️)
2. Clicca su **"Download Code"** o **"Scarica Codice"**

### Passo 2: Salvare il file
- Verrà scaricato un file `.zip` contenente l'intero progetto
- Estrarre lo ZIP nella cartella desiderata

---

## Metodo 2: Salvare su GitHub

### Passo 1: Collegare GitHub
1. Nella chat di Emergent, cerca il pulsante **"Save to GitHub"**
2. Autorizza l'accesso al tuo account GitHub
3. Seleziona il repository di destinazione o creane uno nuovo

### Passo 2: Clonare il Repository
```bash
git clone https://github.com/TUO_USERNAME/TUO_REPOSITORY.git
cd TUO_REPOSITORY
```

---

## Contenuto del Download

Una volta scaricato, avrai questa struttura:

```
ambulatorio-infermieristico/
├── backend/
│   ├── server.py              # 🔧 Server API principale
│   ├── requirements.txt       # 📦 Dipendenze Python
│   ├── .env.example          # ⚙️ Template configurazione
│   └── .env                  # ⚙️ Configurazione attuale
│
├── frontend/
│   ├── src/                  # 💻 Codice sorgente React
│   ├── public/               # 📁 File statici
│   ├── package.json          # 📦 Dipendenze Node.js
│   ├── .env.example         # ⚙️ Template configurazione
│   └── .env                 # ⚙️ Configurazione attuale
│
├── README_COMPLETO.md        # 📖 Documentazione dettagliata
├── DOWNLOAD_ISTRUZIONI.md    # 📥 Questo file
└── setup.sh                  # 🚀 Script di setup automatico
```

---

## Dopo il Download: Primi Passi

### 1. Verificare Prerequisiti
- Node.js v18+
- Python 3.11+
- MongoDB 6.0+
- Yarn

### 2. Configurare l'Ambiente
```bash
# Copiare i file di configurazione
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Modificare i file .env secondo le tue necessità
```

### 3. Installare Dipendenze
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
yarn install
```

### 4. Avviare l'Applicazione
```bash
# Terminale 1 - Backend
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminale 2 - Frontend
cd frontend
yarn start
```

---

## Credenziali di Accesso

| Username | Password |
|----------|----------|
| Domenico | infermiere |
| Antonella | infermiere |
| Giovanna | infermiere |
| Oriana | infermiere |
| G.Domenico | infermiere |

---

## Nota Importante

⚠️ **Per la produzione, ricordati di:**
1. Cambiare `JWT_SECRET` con una chiave sicura
2. Configurare correttamente `CORS_ORIGINS`
3. Usare un database MongoDB in cloud (Atlas) o su server dedicato
4. Configurare HTTPS
5. Cambiare le password degli utenti

---

**Hai bisogno di aiuto?** Consulta il file `README_COMPLETO.md` per la documentazione dettagliata.
