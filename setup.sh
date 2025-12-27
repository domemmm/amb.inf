#!/bin/bash

# ==============================================
# AMBULATORIO INFERMIERISTICO - SCRIPT DI SETUP
# ==============================================
# Questo script configura e avvia l'applicazione
# ==============================================

echo "🏥 Ambulatorio Infermieristico - Setup Script"
echo "=============================================="

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funzione per stampare step
print_step() {
    echo -e "\n${YELLOW}📌 $1${NC}"
}

# Funzione per stampare successo
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Funzione per stampare errore
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Verificare prerequisiti
print_step "Verifico prerequisiti..."

# Verifica Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python installato: $PYTHON_VERSION"
else
    print_error "Python3 non trovato. Installarlo prima di continuare."
    exit 1
fi

# Verifica Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js installato: $NODE_VERSION"
else
    print_error "Node.js non trovato. Installarlo prima di continuare."
    exit 1
fi

# Verifica Yarn
if command -v yarn &> /dev/null; then
    YARN_VERSION=$(yarn --version)
    print_success "Yarn installato: $YARN_VERSION"
else
    print_error "Yarn non trovato. Installarlo: npm install -g yarn"
    exit 1
fi

# Verifica MongoDB
if command -v mongod &> /dev/null; then
    print_success "MongoDB installato"
else
    print_error "MongoDB non trovato. Installarlo prima di continuare."
    exit 1
fi

# 2. Setup Backend
print_step "Setup Backend..."
cd backend

# Creare virtual environment (opzionale)
if [ ! -d "venv" ]; then
    echo "Creazione virtual environment..."
    python3 -m venv venv
fi

# Attivare virtual environment
source venv/bin/activate 2>/dev/null || true

# Installare dipendenze
echo "Installazione dipendenze Python..."
pip install -r requirements.txt --quiet

print_success "Backend configurato!"

cd ..

# 3. Setup Frontend
print_step "Setup Frontend..."
cd frontend

# Installare dipendenze
echo "Installazione dipendenze Node.js..."
yarn install --silent

print_success "Frontend configurato!"

cd ..

# 4. Verificare file .env
print_step "Verifico configurazione..."

if [ ! -f "backend/.env" ]; then
    echo "Creazione backend/.env..."
    cat > backend/.env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="ambulatorio_infermieristico"
CORS_ORIGINS="*"
JWT_SECRET="ambulatorio-infermieristico-secret-key-2024"
EOF
fi

if [ ! -f "frontend/.env" ]; then
    echo "Creazione frontend/.env..."
    cat > frontend/.env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
EOF
fi

print_success "Configurazione completata!"

# 5. Istruzioni finali
echo ""
echo "=============================================="
echo -e "${GREEN}🎉 SETUP COMPLETATO!${NC}"
echo "=============================================="
echo ""
echo "Per avviare l'applicazione:"
echo ""
echo "📌 TERMINALE 1 - Backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # (opzionale)"
echo "   uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
echo ""
echo "📌 TERMINALE 2 - Frontend:"
echo "   cd frontend"
echo "   yarn start"
echo ""
echo "📌 L'applicazione sarà disponibile su:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8001"
echo "   API Docs: http://localhost:8001/docs"
echo ""
echo "📌 Credenziali di accesso:"
echo "   Username: Domenico (o Antonella, Giovanna, Oriana, G.Domenico)"
echo "   Password: infermiere"
echo ""
echo "=============================================="
