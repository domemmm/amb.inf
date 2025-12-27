from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, date, timedelta
import jwt
import bcrypt
from enum import Enum
import base64
import io
import zipfile
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Settings
JWT_SECRET = os.environ.get('JWT_SECRET', 'ambulatorio-infermieristico-secret-key-2024')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

security = HTTPBearer()

# Create the main app
app = FastAPI(title="Ambulatorio Infermieristico API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============== ENUMS ==============
class PatientType(str, Enum):
    PICC = "PICC"
    MED = "MED"
    PICC_MED = "PICC_MED"

class PatientStatus(str, Enum):
    IN_CURA = "in_cura"
    DIMESSO = "dimesso"
    SOSPESO = "sospeso"

class DischargeReason(str, Enum):
    GUARITO = "guarito"
    ADI = "adi"
    ALTRO = "altro"

class Ambulatorio(str, Enum):
    PTA_CENTRO = "pta_centro"
    VILLA_GINESTRE = "villa_ginestre"

# ============== MODELS ==============
class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    ambulatori: List[str]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PatientCreate(BaseModel):
    nome: str
    cognome: str
    tipo: PatientType
    ambulatorio: Ambulatorio
    data_nascita: Optional[str] = None
    codice_fiscale: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    medico_base: Optional[str] = None
    anamnesi: Optional[str] = None
    terapia_in_atto: Optional[str] = None
    allergie: Optional[str] = None

class PatientUpdate(BaseModel):
    nome: Optional[str] = None
    cognome: Optional[str] = None
    tipo: Optional[PatientType] = None
    data_nascita: Optional[str] = None
    codice_fiscale: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    medico_base: Optional[str] = None
    anamnesi: Optional[str] = None
    terapia_in_atto: Optional[str] = None
    allergie: Optional[str] = None
    status: Optional[PatientStatus] = None
    discharge_reason: Optional[str] = None
    discharge_notes: Optional[str] = None
    suspend_notes: Optional[str] = None
    lesion_markers: Optional[List[Dict[str, Any]]] = None

class Patient(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    cognome: str
    tipo: PatientType
    ambulatorio: Ambulatorio
    status: PatientStatus = PatientStatus.IN_CURA
    data_nascita: Optional[str] = None
    codice_fiscale: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    medico_base: Optional[str] = None
    anamnesi: Optional[str] = None
    terapia_in_atto: Optional[str] = None
    allergie: Optional[str] = None
    lesion_markers: List[Dict[str, Any]] = []
    discharge_reason: Optional[str] = None
    discharge_notes: Optional[str] = None
    suspend_notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Prestazioni
class PrestazionePICC(str, Enum):
    MEDICAZIONE_SEMPLICE = "medicazione_semplice"
    IRRIGAZIONE_CATETERE = "irrigazione_catetere"

class PrestazioneMED(str, Enum):
    MEDICAZIONE_SEMPLICE = "medicazione_semplice"
    FASCIATURA_SEMPLICE = "fasciatura_semplice"
    INIEZIONE_TERAPEUTICA = "iniezione_terapeutica"
    CATETERE_VESCICALE = "catetere_vescicale"

class AppointmentCreate(BaseModel):
    patient_id: str
    ambulatorio: Ambulatorio
    data: str  # YYYY-MM-DD
    ora: str   # HH:MM
    tipo: str  # PICC or MED
    prestazioni: List[str]
    note: Optional[str] = None

class Appointment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    patient_nome: Optional[str] = None
    patient_cognome: Optional[str] = None
    ambulatorio: Ambulatorio
    data: str
    ora: str
    tipo: str
    prestazioni: List[str]
    note: Optional[str] = None
    completed: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Scheda Medicazione MED
class SchedaMedicazioneMEDCreate(BaseModel):
    patient_id: str
    ambulatorio: Ambulatorio
    data_compilazione: str
    fondo: List[str] = []  # granuleggiante, fibrinoso, necrotico, infetto, biofilmato
    margini: List[str] = []  # attivi, piantati, in_estensione, a_scogliera
    cute_perilesionale: List[str] = []  # integra, secca, arrossata, macerata, ipercheratosica
    essudato_quantita: Optional[str] = None  # assente, moderato, abbondante
    essudato_tipo: List[str] = []  # sieroso, ematico, infetto
    medicazione: str = "La lesione è stata trattata seguendo le 4 fasi del Wound Hygiene:\nDetersione con Prontosan\nDebridement e Riattivazione dei margini\nMedicazione: "
    prossimo_cambio: Optional[str] = None
    firma: Optional[str] = None
    foto_ids: List[str] = []

class SchedaMedicazioneMED(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    ambulatorio: Ambulatorio
    data_compilazione: str
    fondo: List[str] = []
    margini: List[str] = []
    cute_perilesionale: List[str] = []
    essudato_quantita: Optional[str] = None
    essudato_tipo: List[str] = []
    medicazione: str
    prossimo_cambio: Optional[str] = None
    firma: Optional[str] = None
    foto_ids: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Scheda Impianto PICC
class SchedaImpiantoPICCCreate(BaseModel):
    patient_id: str
    ambulatorio: Ambulatorio
    data_impianto: str
    tipo_catetere: str
    sede: str
    braccio: Optional[str] = None  # dx, sn
    vena: Optional[str] = None  # basilica, cefalica, brachiale
    exit_site_cm: Optional[str] = None
    ecoguidato: bool = False
    igiene_mani: Optional[str] = None
    precauzioni_barriera: bool = False
    disinfettante: Optional[str] = None
    sutureless_device: bool = False
    medicazione_trasparente: bool = False
    controllo_rx: bool = False
    controllo_ecg: bool = False
    modalita: Optional[str] = None  # emergenza, urgenza, elezione
    motivazione: Optional[str] = None
    operatore: Optional[str] = None
    note: Optional[str] = None
    allegati: List[str] = []

class SchedaImpiantoPICC(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    ambulatorio: Ambulatorio
    data_impianto: str
    tipo_catetere: str
    sede: str
    braccio: Optional[str] = None
    vena: Optional[str] = None
    exit_site_cm: Optional[str] = None
    ecoguidato: bool = False
    igiene_mani: Optional[str] = None
    precauzioni_barriera: bool = False
    disinfettante: Optional[str] = None
    sutureless_device: bool = False
    medicazione_trasparente: bool = False
    controllo_rx: bool = False
    controllo_ecg: bool = False
    modalita: Optional[str] = None
    motivazione: Optional[str] = None
    operatore: Optional[str] = None
    note: Optional[str] = None
    allegati: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Scheda Gestione Mensile PICC
class SchedaGestionePICCCreate(BaseModel):
    patient_id: str
    ambulatorio: Ambulatorio
    mese: str  # YYYY-MM
    giorni: Dict[str, Dict[str, Any]] = {}  # {1: {lavaggio_mani: true, ...}, 2: {...}}
    note: Optional[str] = None

class SchedaGestionePICC(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    ambulatorio: Ambulatorio
    mese: str
    giorni: Dict[str, Dict[str, Any]] = {}
    note: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Photo / Attachment
class PhotoCreate(BaseModel):
    patient_id: str
    ambulatorio: Ambulatorio
    tipo: str  # MED, PICC, MED_SCHEDA
    descrizione: Optional[str] = None
    data: str
    file_type: Optional[str] = "image"  # image, pdf, word, excel
    original_name: Optional[str] = None
    scheda_med_id: Optional[str] = None  # Link to specific scheda MED

class Photo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    ambulatorio: Ambulatorio
    tipo: str
    descrizione: Optional[str] = None
    data: str
    image_data: str  # Base64
    file_type: Optional[str] = "image"  # image, pdf, word, excel
    original_name: Optional[str] = None
    mime_type: Optional[str] = None
    scheda_med_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Document Templates
class DocumentTemplate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    nome: str
    categoria: str  # PICC or MED
    tipo_file: str  # pdf, word
    url: str

# Statistics
class StatisticsQuery(BaseModel):
    ambulatorio: Ambulatorio
    tipo: Optional[str] = None  # PICC, MED or None for all
    anno: int
    mese: Optional[int] = None

# ============== USERS DATA ==============
USERS = {
    "Domenico": {
        "password": "infermiere",
        "ambulatori": ["pta_centro", "villa_ginestre"]
    },
    "Antonella": {
        "password": "infermiere",
        "ambulatori": ["pta_centro", "villa_ginestre"]
    },
    "Giovanna": {
        "password": "infermiere",
        "ambulatori": ["pta_centro"]
    },
    "Oriana": {
        "password": "infermiere",
        "ambulatori": ["pta_centro"]
    },
    "G.Domenico": {
        "password": "infermiere",
        "ambulatori": ["pta_centro"]
    }
}

# Document templates
DOCUMENT_TEMPLATES = [
    # MED Documents
    {"id": "consent_med", "nome": "Consenso Informato MED", "categoria": "MED", "tipo_file": "pdf", "url": "https://customer-assets.emergentagent.com/job_f548c735-b113-437f-82ec-c0afbf122c8d/artifacts/k3jcaxa4_CONSENSO_INFORMATO.pdf"},
    {"id": "scheda_mmg", "nome": "Scheda MMG", "categoria": "MED", "tipo_file": "pdf", "url": "https://customer-assets.emergentagent.com/job_f548c735-b113-437f-82ec-c0afbf122c8d/artifacts/8bonfflf_SCHEDA_MMG.pdf"},
    {"id": "anagrafica_med", "nome": "Anagrafica/Anamnesi MED", "categoria": "MED", "tipo_file": "pdf", "url": "https://customer-assets.emergentagent.com/job_f548c735-b113-437f-82ec-c0afbf122c8d/artifacts/txx60tb0_anagrafica%20med.jpg"},
    {"id": "scheda_medicazione_med", "nome": "Scheda Medicazione MED", "categoria": "MED", "tipo_file": "pdf", "url": "https://customer-assets.emergentagent.com/job_f548c735-b113-437f-82ec-c0afbf122c8d/artifacts/nzkb51vc_medicazione%20med.jpg"},
    # PICC Documents
    {"id": "consent_picc_1", "nome": "Consenso Generico Processi Clinico-Assistenziali", "categoria": "PICC", "tipo_file": "pdf", "url": "https://customer-assets.emergentagent.com/job_medhub-38/artifacts/ysusww7f_CONSENSO%20GENERICO%20AI%20PROCESSI%20CLINICO.ASSISTENZIALI%20ORDINARI%201.pdf"},
    {"id": "consent_picc_2", "nome": "Consenso Informato PICC e Midline", "categoria": "PICC", "tipo_file": "pdf", "url": "https://customer-assets.emergentagent.com/job_medhub-38/artifacts/siz46bgw_CONSENSO%20INFORMATO%20PICC%20E%20MIDLINE.pdf"},
    {"id": "brochure_picc_port", "nome": "Brochure PICC Port", "categoria": "PICC", "tipo_file": "pdf", "url": "https://customer-assets.emergentagent.com/job_medhub-38/artifacts/cein282q_Picc%20Port.pdf"},
    {"id": "brochure_picc", "nome": "Brochure PICC", "categoria": "PICC", "tipo_file": "pdf", "url": "https://customer-assets.emergentagent.com/job_medhub-38/artifacts/kk882djy_Picc.pdf"},
    {"id": "scheda_impianto_picc", "nome": "Scheda Impianto e Gestione AV", "categoria": "PICC", "tipo_file": "pdf", "url": "https://customer-assets.emergentagent.com/job_medhub-38/artifacts/sbw1iws9_Sch%20Impianto%20Gestione%20AV%20NEW.pdf"},
    {"id": "specifiche_impianto_picc", "nome": "Specifiche Impianto", "categoria": "PICC", "tipo_file": "pdf", "url": "https://customer-assets.emergentagent.com/job_medhub-38/artifacts/03keycn2_specifiche%20impianto.pdf"},
]

# Italian holidays for Palermo
def get_holidays(year: int) -> List[str]:
    holidays = [
        f"{year}-01-01",  # Capodanno
        f"{year}-01-06",  # Epifania
        f"{year}-04-25",  # Liberazione
        f"{year}-05-01",  # Festa del Lavoro
        f"{year}-06-02",  # Festa della Repubblica
        f"{year}-07-15",  # Santa Rosalia (Palermo)
        f"{year}-08-15",  # Ferragosto
        f"{year}-11-01",  # Ognissanti
        f"{year}-12-08",  # Immacolata
        f"{year}-12-25",  # Natale
        f"{year}-12-26",  # Santo Stefano
    ]
    # Easter calculation (simplified - would need proper algorithm for accuracy)
    # Adding approximate Easter dates for 2026-2030
    easter_dates = {
        2026: "2026-04-05",
        2027: "2027-03-28",
        2028: "2028-04-16",
        2029: "2029-04-01",
        2030: "2030-04-21",
    }
    if year in easter_dates:
        easter = easter_dates[year]
        holidays.append(easter)
        # Pasquetta (Easter Monday)
        easter_date = datetime.strptime(easter, "%Y-%m-%d")
        pasquetta = easter_date + timedelta(days=1)
        holidays.append(pasquetta.strftime("%Y-%m-%d"))
    return holidays

# ============== AUTH HELPERS ==============
def create_token(username: str, ambulatori: List[str]) -> str:
    payload = {
        "sub": username,
        "ambulatori": ambulatori,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token scaduto")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token non valido")

# ============== AUTH ROUTES ==============
@api_router.post("/auth/login", response_model=TokenResponse)
async def login(data: UserLogin):
    user = USERS.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    
    token = create_token(data.username, user["ambulatori"])
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=data.username.lower().replace(".", "_"),
            username=data.username,
            ambulatori=user["ambulatori"]
        )
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user(payload: dict = Depends(verify_token)):
    username = payload["sub"]
    user = USERS.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    return UserResponse(
        id=username.lower().replace(".", "_"),
        username=username,
        ambulatori=user["ambulatori"]
    )

# ============== PATIENTS ROUTES ==============
@api_router.post("/patients", response_model=Patient, status_code=201)
async def create_patient(data: PatientCreate, payload: dict = Depends(verify_token)):
    # Check ambulatorio access
    if data.ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    # Villa Ginestre only allows PICC
    if data.ambulatorio == Ambulatorio.VILLA_GINESTRE and data.tipo != PatientType.PICC:
        raise HTTPException(status_code=400, detail="Villa delle Ginestre gestisce solo pazienti PICC")
    
    patient = Patient(**data.model_dump())
    doc = patient.model_dump()
    await db.patients.insert_one(doc)
    return patient

@api_router.get("/patients", response_model=List[Patient])
async def get_patients(
    ambulatorio: Ambulatorio,
    status: Optional[PatientStatus] = None,
    tipo: Optional[PatientType] = None,
    search: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    if ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    query = {"ambulatorio": ambulatorio.value}
    if status:
        query["status"] = status.value
    if tipo:
        query["tipo"] = tipo.value
    if search:
        query["$or"] = [
            {"nome": {"$regex": search, "$options": "i"}},
            {"cognome": {"$regex": search, "$options": "i"}}
        ]
    
    patients = await db.patients.find(query, {"_id": 0}).sort("cognome", 1).to_list(1000)
    return patients

@api_router.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str, payload: dict = Depends(verify_token)):
    patient = await db.patients.find_one({"id": patient_id}, {"_id": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Paziente non trovato")
    if patient["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    return patient

@api_router.put("/patients/{patient_id}", response_model=Patient)
async def update_patient(patient_id: str, data: PatientUpdate, payload: dict = Depends(verify_token)):
    patient = await db.patients.find_one({"id": patient_id}, {"_id": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Paziente non trovato")
    if patient["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.patients.update_one({"id": patient_id}, {"$set": update_data})
    updated = await db.patients.find_one({"id": patient_id}, {"_id": 0})
    return updated

@api_router.delete("/patients/{patient_id}")
async def delete_patient(patient_id: str, payload: dict = Depends(verify_token)):
    patient = await db.patients.find_one({"id": patient_id}, {"_id": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Paziente non trovato")
    if patient["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    # Delete patient
    await db.patients.delete_one({"id": patient_id})
    
    # Delete all related records
    await db.schede_impianto_picc.delete_many({"patient_id": patient_id})
    await db.schede_gestione_picc.delete_many({"patient_id": patient_id})
    await db.schede_medicazione_med.delete_many({"patient_id": patient_id})
    await db.appointments.delete_many({"patient_id": patient_id})
    await db.prescrizioni.delete_many({"patient_id": patient_id})
    await db.photos.delete_many({"patient_id": patient_id})
    
    return {"message": "Paziente e tutte le schede correlate eliminati"}

# ============== APPOINTMENTS ROUTES ==============
@api_router.post("/appointments", response_model=Appointment)
async def create_appointment(data: AppointmentCreate, payload: dict = Depends(verify_token)):
    if data.ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    # Get patient info
    patient = await db.patients.find_one({"id": data.patient_id}, {"_id": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Paziente non trovato")
    
    # Check slot availability (max 2 per type per slot)
    existing = await db.appointments.count_documents({
        "ambulatorio": data.ambulatorio.value,
        "data": data.data,
        "ora": data.ora,
        "tipo": data.tipo
    })
    if existing >= 2:
        raise HTTPException(status_code=400, detail="Slot pieno (max 2 pazienti)")
    
    appointment = Appointment(
        **data.model_dump(),
        patient_nome=patient["nome"],
        patient_cognome=patient["cognome"]
    )
    doc = appointment.model_dump()
    await db.appointments.insert_one(doc)
    return appointment

@api_router.get("/appointments", response_model=List[Appointment])
async def get_appointments(
    ambulatorio: Ambulatorio,
    data: Optional[str] = None,
    data_from: Optional[str] = None,
    data_to: Optional[str] = None,
    tipo: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    if ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    query = {"ambulatorio": ambulatorio.value}
    if data:
        query["data"] = data
    elif data_from and data_to:
        query["data"] = {"$gte": data_from, "$lte": data_to}
    if tipo:
        query["tipo"] = tipo
    
    appointments = await db.appointments.find(query, {"_id": 0}).sort([("data", 1), ("ora", 1)]).to_list(1000)
    return appointments

@api_router.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: str, data: dict, payload: dict = Depends(verify_token)):
    appointment = await db.appointments.find_one({"id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appuntamento non trovato")
    if appointment["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    await db.appointments.update_one({"id": appointment_id}, {"$set": data})
    updated = await db.appointments.find_one({"id": appointment_id}, {"_id": 0})
    return updated

@api_router.delete("/appointments/{appointment_id}")
async def delete_appointment(appointment_id: str, payload: dict = Depends(verify_token)):
    appointment = await db.appointments.find_one({"id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appuntamento non trovato")
    if appointment["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    await db.appointments.delete_one({"id": appointment_id})
    return {"message": "Appuntamento eliminato"}

# ============== SCHEDE MEDICAZIONE MED ==============
@api_router.post("/schede-medicazione-med", response_model=SchedaMedicazioneMED)
async def create_scheda_medicazione_med(data: SchedaMedicazioneMEDCreate, payload: dict = Depends(verify_token)):
    if data.ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    scheda = SchedaMedicazioneMED(**data.model_dump())
    doc = scheda.model_dump()
    await db.schede_medicazione_med.insert_one(doc)
    return scheda

@api_router.get("/schede-medicazione-med", response_model=List[SchedaMedicazioneMED])
async def get_schede_medicazione_med(
    patient_id: str,
    ambulatorio: Ambulatorio,
    payload: dict = Depends(verify_token)
):
    if ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    schede = await db.schede_medicazione_med.find(
        {"patient_id": patient_id, "ambulatorio": ambulatorio.value},
        {"_id": 0}
    ).sort("data_compilazione", -1).to_list(1000)
    return schede

@api_router.get("/schede-medicazione-med/{scheda_id}", response_model=SchedaMedicazioneMED)
async def get_scheda_medicazione_med(scheda_id: str, payload: dict = Depends(verify_token)):
    scheda = await db.schede_medicazione_med.find_one({"id": scheda_id}, {"_id": 0})
    if not scheda:
        raise HTTPException(status_code=404, detail="Scheda non trovata")
    if scheda["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    return scheda

@api_router.put("/schede-medicazione-med/{scheda_id}", response_model=SchedaMedicazioneMED)
async def update_scheda_medicazione_med(scheda_id: str, data: dict, payload: dict = Depends(verify_token)):
    scheda = await db.schede_medicazione_med.find_one({"id": scheda_id}, {"_id": 0})
    if not scheda:
        raise HTTPException(status_code=404, detail="Scheda non trovata")
    if scheda["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    await db.schede_medicazione_med.update_one({"id": scheda_id}, {"$set": data})
    updated = await db.schede_medicazione_med.find_one({"id": scheda_id}, {"_id": 0})
    return updated

# ============== SCHEDE IMPIANTO PICC ==============
@api_router.post("/schede-impianto-picc", response_model=SchedaImpiantoPICC)
async def create_scheda_impianto_picc(data: SchedaImpiantoPICCCreate, payload: dict = Depends(verify_token)):
    if data.ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    scheda = SchedaImpiantoPICC(**data.model_dump())
    doc = scheda.model_dump()
    await db.schede_impianto_picc.insert_one(doc)
    return scheda

@api_router.get("/schede-impianto-picc", response_model=List[SchedaImpiantoPICC])
async def get_schede_impianto_picc(
    patient_id: str,
    ambulatorio: Ambulatorio,
    payload: dict = Depends(verify_token)
):
    if ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    schede = await db.schede_impianto_picc.find(
        {"patient_id": patient_id, "ambulatorio": ambulatorio.value},
        {"_id": 0}
    ).sort("data_impianto", -1).to_list(1000)
    return schede

@api_router.put("/schede-impianto-picc/{scheda_id}", response_model=SchedaImpiantoPICC)
async def update_scheda_impianto_picc(scheda_id: str, data: dict, payload: dict = Depends(verify_token)):
    scheda = await db.schede_impianto_picc.find_one({"id": scheda_id}, {"_id": 0})
    if not scheda:
        raise HTTPException(status_code=404, detail="Scheda non trovata")
    if scheda["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    await db.schede_impianto_picc.update_one({"id": scheda_id}, {"$set": data})
    updated = await db.schede_impianto_picc.find_one({"id": scheda_id}, {"_id": 0})
    return updated

# Generate PDF for Scheda Impianto PICC in official format
@api_router.get("/schede-impianto-picc/{scheda_id}/pdf")
async def download_scheda_impianto_pdf(scheda_id: str, payload: dict = Depends(verify_token)):
    """Download scheda impianto PICC as PDF in official format"""
    scheda = await db.schede_impianto_picc.find_one({"id": scheda_id}, {"_id": 0})
    if not scheda:
        raise HTTPException(status_code=404, detail="Scheda non trovata")
    if scheda["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    # Get patient info
    patient = await db.patients.find_one({"id": scheda["patient_id"]}, {"_id": 0})
    
    # Generate PDF
    pdf_bytes = generate_scheda_impianto_pdf(scheda, patient)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=scheda_impianto_{scheda.get('data_impianto', 'nd')}.pdf"}
    )

def generate_scheda_impianto_pdf(scheda: dict, patient: dict) -> bytes:
    """Generate PDF for Scheda Impianto PICC - EXACT format as per official form"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.8*cm, bottomMargin=0.8*cm, leftMargin=1*cm, rightMargin=1*cm)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', fontSize=12, alignment=1, fontName='Helvetica-Bold', spaceAfter=5)
    section_header = ParagraphStyle('SectionHeader', fontSize=10, fontName='Helvetica-Bold', textColor=colors.white, 
                                    backColor=colors.HexColor('#4a5568'), leftIndent=3, rightIndent=3, spaceBefore=8, spaceAfter=4)
    normal_style = ParagraphStyle('Normal', fontSize=8, spaceAfter=2, fontName='Helvetica')
    small_style = ParagraphStyle('Small', fontSize=7, spaceAfter=1, fontName='Helvetica')
    italic_small = ParagraphStyle('ItalicSmall', fontSize=6, fontName='Helvetica-Oblique', textColor=colors.grey)
    
    def cb(checked):
        """Checkbox helper - filled or empty"""
        return "■" if checked else "□"
    
    def get_val(key, default=""):
        """Get value from scheda, return empty string if None"""
        val = scheda.get(key)
        return val if val else default
    
    # === HEADER ===
    story.append(Paragraph("SCHEDA IMPIANTO e GESTIONE ACCESSI VENOSI", title_style))
    story.append(Paragraph("Allegato n. 2", ParagraphStyle('Right', fontSize=8, alignment=2)))
    story.append(Spacer(1, 8))
    
    # Patient Info Box
    patient_name = f"{patient.get('cognome', '')} {patient.get('nome', '')}" if patient else ""
    patient_cf = patient.get('codice_fiscale', '') if patient else ""
    patient_dob = patient.get('data_nascita', '') if patient else ""
    patient_sex = patient.get('sesso', '') if patient else ""
    
    header_data = [
        ["Presidio Ospedaliero/Struttura:", get_val('presidio_impianto'), "Cognome e Nome:", patient_name],
        ["Codice Fiscale:", patient_cf, "Data di nascita:", patient_dob],
        ["Sesso:", f"{cb(patient_sex == 'M')} M   {cb(patient_sex == 'F')} F", "Preso in carico dal:", get_val('data_impianto')],
    ]
    t = Table(header_data, colWidths=[4*cm, 5.5*cm, 3.5*cm, 5.5*cm])
    t.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))
    
    # === SECTION 1: CATETERE GIÀ PRESENTE ===
    story.append(Paragraph("1. SEZIONE CATETERE GIA' PRESENTE", section_header))
    story.append(Paragraph("(Da compilare se catetere già presente al momento della presa in carico)", italic_small))
    story.append(Spacer(1, 4))
    
    tipo = get_val('tipo_catetere')
    tipo_opts = [
        ("cvd_non_tunnellizzato", "CVC non tunnellizzato (breve termine)"),
        ("cvd_tunnellizzato", "CVC tunnellizzato (lungo termine tipo Groshong, Hickman, Broviac)"),
        ("picc", "CVC medio termine (PICC)"),
        ("port", "PORT (lungo termine)"),
        ("midline", "Midline"),
    ]
    
    story.append(Paragraph("<b>Tipo di Catetere:</b>", normal_style))
    for opt_id, opt_label in tipo_opts:
        story.append(Paragraph(f"    {cb(tipo == opt_id)} {opt_label}", small_style))
    
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Struttura/reparto dove il catetere è stato inserito:</b> {get_val('reparto_provenienza')}", small_style))
    story.append(Paragraph(f"<b>Controllo RX Post-Inserimento effettuato:</b>  {cb(get_val('controllo_rx_precedente'))} SI   {cb(not get_val('controllo_rx_precedente'))} NO", small_style))
    
    story.append(Spacer(1, 8))
    
    # === SECTION 2: IMPIANTO CATETERE ===
    story.append(Paragraph("2. SEZIONE IMPIANTO CATETERE", section_header))
    story.append(Paragraph("(Da compilare se catetere viene impiantato nella struttura)", italic_small))
    story.append(Spacer(1, 4))
    
    # TIPO DI CATETERE
    story.append(Paragraph("<b>TIPO DI CATETERE:</b>", normal_style))
    for opt_id, opt_label in tipo_opts:
        story.append(Paragraph(f"    {cb(tipo == opt_id)} {opt_label}", small_style))
    
    story.append(Spacer(1, 4))
    
    # POSIZIONAMENTO CVC
    story.append(Paragraph("<b>POSIZIONAMENTO CVC:</b>", normal_style))
    sede = get_val('sede')
    cvc_pos = [("succlavia_dx", "succlavia dx"), ("succlavia_sn", "succlavia sn"), 
               ("giugulare_dx", "giugulare interna dx"), ("giugulare_sn", "giugulare interna sn")]
    pos_line = "    " + "  ".join([f"{cb(sede == p[0])} {p[1]}" for p in cvc_pos])
    story.append(Paragraph(pos_line, small_style))
    story.append(Paragraph(f"    {cb(sede and sede not in [p[0] for p in cvc_pos])} altro specificare: {sede if sede and sede not in [p[0] for p in cvc_pos] else ''}", small_style))
    
    story.append(Spacer(1, 4))
    
    # POSIZIONAMENTO PICC
    story.append(Paragraph("<b>POSIZIONAMENTO PICC:</b>", normal_style))
    braccio = get_val('braccio')
    story.append(Paragraph(f"    {cb(braccio == 'dx')} braccio dx    {cb(braccio == 'sn')} braccio sn", small_style))
    
    vena = get_val('vena')
    story.append(Paragraph(f"    <b>Vena:</b>  {cb(vena == 'basilica')} Basilica   {cb(vena == 'cefalica')} Cefalica   {cb(vena == 'brachiale')} Vena brachiale", small_style))
    story.append(Paragraph(f"    <b>Exit-site cm:</b> {get_val('exit_site_cm')}", small_style))
    
    tunn = get_val('tunnelizzazione')
    story.append(Paragraph(f"    <b>Tunnelizzazione:</b>  {cb(tunn)} SI   {cb(not tunn)} NO", small_style))
    
    story.append(Spacer(1, 4))
    
    # PROCEDURE DETAILS
    val_sito = get_val('valutazione_sito')
    story.append(Paragraph(f"<b>VALUTAZIONE MIGLIOR SITO DI INSERIMENTO:</b>  {cb(val_sito)} SI   {cb(not val_sito)} NO", normal_style))
    
    eco = get_val('ecoguidato')
    story.append(Paragraph(f"<b>IMPIANTO ECOGUIDATO:</b>  {cb(eco)} SI   {cb(not eco)} NO", normal_style))
    
    igiene = get_val('igiene_mani')
    story.append(Paragraph(f"<b>IGIENE DELLE MANI (lavaggio antisettico o frizione alcolica):</b>  {cb(igiene)} SI   {cb(not igiene)} NO", normal_style))
    
    prec = get_val('precauzioni_barriera')
    story.append(Paragraph(f"<b>UTILIZZO MASSIME PRECAUZIONI DI BARRIERA:</b>  {cb(prec)} SI   {cb(not prec)} NO", normal_style))
    story.append(Paragraph("    (berretto, maschera, camice sterile, guanti sterili, telo sterile)", italic_small))
    
    story.append(Spacer(1, 3))
    
    # DISINFEZIONE
    dis = get_val('disinfettante')
    story.append(Paragraph("<b>DISINFEZIONE DELLA CUTE INTEGRA:</b>", normal_style))
    story.append(Paragraph(f"    {cb(dis == 'clorexidina_2')} CLOREXIDINA IN SOLUZIONE ALCOLICA 2%    {cb(dis == 'iodiopovidone')} IODIOPOVIDONE", small_style))
    
    story.append(Spacer(1, 3))
    
    # ALTRI DETTAGLI
    sut = get_val('sutureless_device')
    story.append(Paragraph(f"<b>IMPIEGO DI 'SUTURELESS DEVICES':</b>  {cb(sut)} SI   {cb(not sut)} NO", normal_style))
    
    med_trasp = get_val('medicazione_trasparente')
    story.append(Paragraph(f"<b>IMPIEGO DI MEDICAZIONE SEMIPERMEABILE TRASPARENTE:</b>  {cb(med_trasp)} SI   {cb(not med_trasp)} NO", normal_style))
    
    med_occl = get_val('medicazione_occlusiva')
    story.append(Paragraph(f"<b>IMPIEGO DI MEDICAZIONE OCCLUSIVA:</b>  {cb(med_occl)} SI   {cb(not med_occl)} NO", normal_style))
    
    rx_post = get_val('controllo_rx')
    story.append(Paragraph(f"<b>CONTROLLO RX POST-INSERIMENTO:</b>  {cb(rx_post)} SI   {cb(not rx_post)} NO", normal_style))
    
    ecg_post = get_val('controllo_ecg')
    story.append(Paragraph(f"<b>CONTROLLO ECG POST-INSERIMENTO:</b>  {cb(ecg_post)} SI   {cb(not ecg_post)} NO", normal_style))
    
    story.append(Spacer(1, 4))
    
    # MODALITÀ
    mod = get_val('modalita')
    story.append(Paragraph(f"<b>MODALITÀ:</b>  {cb(mod == 'emergenza')} EMERGENZA - URGENZA    {cb(mod == 'elezione')} ELEZIONE", normal_style))
    
    story.append(Spacer(1, 4))
    
    # MOTIVAZIONE
    motiv = get_val('motivazione')
    story.append(Paragraph("<b>MOTIVAZIONE DI INSERIMENTO CVC:</b>", normal_style))
    motiv_opts = [("chemioterapia", "chemioterapia"), ("difficolta_vene", "difficoltà nel reperire vene"),
                  ("terapia_prolungata", "terapia prolungata"), ("monitoraggio", "monitoraggio invasivo")]
    motiv_line = "    " + "  ".join([f"{cb(motiv == m[0])} {m[1]}" for m in motiv_opts])
    story.append(Paragraph(motiv_line, small_style))
    story.append(Paragraph(f"    {cb(motiv == 'altro')} altro: {get_val('motivazione_altro')}", small_style))
    
    story.append(Spacer(1, 10))
    
    # === FOOTER ===
    footer_data = [
        ["DATA POSIZIONAMENTO:", get_val('data_impianto')],
        ["OPERATORE:", get_val('operatore')],
        ["FIRMA:", ""],
    ]
    ft = Table(footer_data, colWidths=[4.5*cm, 14*cm])
    ft.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(ft)
    
    # Note se presenti
    if get_val('note'):
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>NOTE:</b> {get_val('note')}", normal_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ============== SCHEDE GESTIONE PICC (MENSILE) ==============
@api_router.post("/schede-gestione-picc", response_model=SchedaGestionePICC)
async def create_scheda_gestione_picc(data: SchedaGestionePICCCreate, payload: dict = Depends(verify_token)):
    if data.ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    # Check if already exists for this month
    existing = await db.schede_gestione_picc.find_one({
        "patient_id": data.patient_id,
        "ambulatorio": data.ambulatorio.value,
        "mese": data.mese
    })
    if existing:
        raise HTTPException(status_code=400, detail="Esiste già una scheda per questo mese")
    
    scheda = SchedaGestionePICC(**data.model_dump())
    doc = scheda.model_dump()
    await db.schede_gestione_picc.insert_one(doc)
    return scheda

@api_router.get("/schede-gestione-picc", response_model=List[SchedaGestionePICC])
async def get_schede_gestione_picc(
    patient_id: str,
    ambulatorio: Ambulatorio,
    mese: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    if ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    query = {"patient_id": patient_id, "ambulatorio": ambulatorio.value}
    if mese:
        query["mese"] = mese
    
    schede = await db.schede_gestione_picc.find(query, {"_id": 0}).sort("mese", -1).to_list(100)
    return schede

@api_router.put("/schede-gestione-picc/{scheda_id}", response_model=SchedaGestionePICC)
async def update_scheda_gestione_picc(scheda_id: str, data: dict, payload: dict = Depends(verify_token)):
    scheda = await db.schede_gestione_picc.find_one({"id": scheda_id}, {"_id": 0})
    if not scheda:
        raise HTTPException(status_code=404, detail="Scheda non trovata")
    if scheda["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.schede_gestione_picc.update_one({"id": scheda_id}, {"$set": data})
    updated = await db.schede_gestione_picc.find_one({"id": scheda_id}, {"_id": 0})
    return updated

# ============== PHOTOS / ATTACHMENTS ==============
@api_router.post("/photos")
async def upload_photo(
    patient_id: str = Form(...),
    ambulatorio: str = Form(...),
    tipo: str = Form(...),
    data: str = Form(...),
    descrizione: Optional[str] = Form(None),
    file_type: Optional[str] = Form("image"),
    original_name: Optional[str] = Form(None),
    scheda_med_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    payload: dict = Depends(verify_token)
):
    if ambulatorio not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    contents = await file.read()
    image_data = base64.b64encode(contents).decode('utf-8')
    
    # Determine file type from content type if not provided
    mime_type = file.content_type
    if not file_type or file_type == "image":
        if mime_type and 'pdf' in mime_type:
            file_type = 'pdf'
        elif mime_type and ('word' in mime_type or 'document' in mime_type):
            file_type = 'word'
        elif mime_type and ('excel' in mime_type or 'spreadsheet' in mime_type):
            file_type = 'excel'
        elif mime_type and mime_type.startswith('image/'):
            file_type = 'image'
    
    photo = Photo(
        patient_id=patient_id,
        ambulatorio=Ambulatorio(ambulatorio),
        tipo=tipo,
        descrizione=descrizione,
        data=data,
        image_data=image_data,
        file_type=file_type,
        original_name=original_name or file.filename,
        mime_type=mime_type,
        scheda_med_id=scheda_med_id if scheda_med_id != "pending" else None
    )
    doc = photo.model_dump()
    await db.photos.insert_one(doc)
    
    return {"id": photo.id, "message": "File caricato"}

@api_router.get("/photos")
async def get_photos(
    patient_id: str,
    ambulatorio: Ambulatorio,
    tipo: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    if ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    query = {"patient_id": patient_id, "ambulatorio": ambulatorio.value}
    if tipo:
        query["tipo"] = tipo
    
    photos = await db.photos.find(query, {"_id": 0}).sort("data", -1).to_list(100)
    return photos

@api_router.get("/photos/{photo_id}")
async def get_photo(photo_id: str, payload: dict = Depends(verify_token)):
    photo = await db.photos.find_one({"id": photo_id}, {"_id": 0})
    if not photo:
        raise HTTPException(status_code=404, detail="Foto non trovata")
    if photo["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    return photo

@api_router.delete("/photos/{photo_id}")
async def delete_photo(photo_id: str, payload: dict = Depends(verify_token)):
    photo = await db.photos.find_one({"id": photo_id}, {"_id": 0})
    if not photo:
        raise HTTPException(status_code=404, detail="Foto non trovata")
    if photo["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    await db.photos.delete_one({"id": photo_id})
    return {"message": "Foto eliminata"}

# ============== DOCUMENTS ==============
@api_router.get("/documents")
async def get_documents(
    ambulatorio: Ambulatorio,
    categoria: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    if ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    docs = DOCUMENT_TEMPLATES.copy()
    
    # Villa Ginestre only sees PICC documents
    if ambulatorio == Ambulatorio.VILLA_GINESTRE:
        docs = [d for d in docs if d["categoria"] == "PICC"]
    
    if categoria:
        docs = [d for d in docs if d["categoria"] == categoria]
    
    return docs

# ============== STATISTICS ==============
@api_router.get("/statistics")
async def get_statistics(
    ambulatorio: Ambulatorio,
    anno: int,
    mese: Optional[int] = None,
    tipo: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    if ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    # Villa Ginestre only shows PICC stats
    if ambulatorio == Ambulatorio.VILLA_GINESTRE and tipo == "MED":
        raise HTTPException(status_code=400, detail="Villa delle Ginestre non ha statistiche MED")
    
    # Build date range
    if mese:
        start_date = f"{anno}-{mese:02d}-01"
        if mese == 12:
            end_date = f"{anno + 1}-01-01"
        else:
            end_date = f"{anno}-{mese + 1:02d}-01"
    else:
        start_date = f"{anno}-01-01"
        end_date = f"{anno + 1}-01-01"
    
    query = {
        "ambulatorio": ambulatorio.value,
        "data": {"$gte": start_date, "$lt": end_date}
    }
    if tipo:
        query["tipo"] = tipo
    elif ambulatorio == Ambulatorio.VILLA_GINESTRE:
        query["tipo"] = "PICC"
    
    appointments = await db.appointments.find(query, {"_id": 0}).to_list(10000)
    
    # Calculate statistics
    total_accessi = len(appointments)
    unique_patients = len(set(a["patient_id"] for a in appointments))
    
    # Prestazioni count
    prestazioni_count = {}
    for app in appointments:
        for prest in app.get("prestazioni", []):
            prestazioni_count[prest] = prestazioni_count.get(prest, 0) + 1
    
    # Monthly breakdown
    monthly_stats = {}
    for app in appointments:
        month = app["data"][:7]  # YYYY-MM
        if month not in monthly_stats:
            monthly_stats[month] = {"accessi": 0, "pazienti": set(), "prestazioni": {}}
        monthly_stats[month]["accessi"] += 1
        monthly_stats[month]["pazienti"].add(app["patient_id"])
        for prest in app.get("prestazioni", []):
            monthly_stats[month]["prestazioni"][prest] = monthly_stats[month]["prestazioni"].get(prest, 0) + 1
    
    # Convert sets to counts
    for month in monthly_stats:
        monthly_stats[month]["pazienti_unici"] = len(monthly_stats[month]["pazienti"])
        del monthly_stats[month]["pazienti"]
    
    return {
        "anno": anno,
        "mese": mese,
        "ambulatorio": ambulatorio.value,
        "tipo": tipo,
        "totale_accessi": total_accessi,
        "pazienti_unici": unique_patients,
        "prestazioni": prestazioni_count,
        "dettaglio_mensile": monthly_stats
    }

@api_router.get("/statistics/compare")
async def compare_statistics(
    ambulatorio: Ambulatorio,
    periodo1_anno: int,
    periodo1_mese: Optional[int] = None,
    periodo2_anno: int = None,
    periodo2_mese: Optional[int] = None,
    tipo: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    if ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    # Get stats for both periods
    stats1 = await get_statistics(ambulatorio, periodo1_anno, periodo1_mese, tipo, payload)
    stats2 = await get_statistics(ambulatorio, periodo2_anno or periodo1_anno, periodo2_mese, tipo, payload)
    
    # Calculate differences
    diff = {
        "accessi": stats2["totale_accessi"] - stats1["totale_accessi"],
        "pazienti_unici": stats2["pazienti_unici"] - stats1["pazienti_unici"],
        "prestazioni": {}
    }
    
    all_prestazioni = set(stats1["prestazioni"].keys()) | set(stats2["prestazioni"].keys())
    for prest in all_prestazioni:
        val1 = stats1["prestazioni"].get(prest, 0)
        val2 = stats2["prestazioni"].get(prest, 0)
        diff["prestazioni"][prest] = val2 - val1
    
    return {
        "periodo1": stats1,
        "periodo2": stats2,
        "differenze": diff
    }

# ============== CALENDAR HELPERS ==============
@api_router.get("/calendar/holidays")
async def get_calendar_holidays(anno: int):
    return get_holidays(anno)

@api_router.get("/calendar/slots")
async def get_time_slots():
    """Returns available time slots"""
    morning_slots = []
    afternoon_slots = []
    
    # Morning: 08:30 - 13:00
    current = datetime.strptime("08:30", "%H:%M")
    end_morning = datetime.strptime("13:00", "%H:%M")
    while current < end_morning:
        morning_slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=30)
    
    # Afternoon: 15:00 - 17:00
    current = datetime.strptime("15:00", "%H:%M")
    end_afternoon = datetime.strptime("17:00", "%H:%M")
    while current < end_afternoon:
        afternoon_slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=30)
    
    return {
        "mattina": morning_slots,
        "pomeriggio": afternoon_slots,
        "tutti": morning_slots + afternoon_slots
    }

# ============== DELETE ENDPOINTS ==============

@api_router.delete("/schede-impianto-picc/{scheda_id}")
async def delete_scheda_impianto(scheda_id: str, payload: dict = Depends(verify_token)):
    scheda = await db.schede_impianto_picc.find_one({"id": scheda_id}, {"_id": 0})
    if not scheda:
        raise HTTPException(status_code=404, detail="Scheda non trovata")
    if scheda["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    await db.schede_impianto_picc.delete_one({"id": scheda_id})
    return {"message": "Scheda impianto eliminata"}

@api_router.delete("/schede-gestione-picc/{scheda_id}")
async def delete_scheda_gestione(scheda_id: str, payload: dict = Depends(verify_token)):
    scheda = await db.schede_gestione_picc.find_one({"id": scheda_id}, {"_id": 0})
    if not scheda:
        raise HTTPException(status_code=404, detail="Scheda non trovata")
    if scheda["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    await db.schede_gestione_picc.delete_one({"id": scheda_id})
    return {"message": "Scheda gestione eliminata"}

@api_router.delete("/schede-medicazione-med/{scheda_id}")
async def delete_scheda_medicazione(scheda_id: str, payload: dict = Depends(verify_token)):
    scheda = await db.schede_medicazione_med.find_one({"id": scheda_id}, {"_id": 0})
    if not scheda:
        raise HTTPException(status_code=404, detail="Scheda non trovata")
    if scheda["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    await db.schede_medicazione_med.delete_one({"id": scheda_id})
    return {"message": "Scheda medicazione eliminata"}

@api_router.put("/schede-impianto-picc/{scheda_id}")
async def update_scheda_impianto(scheda_id: str, data: dict, payload: dict = Depends(verify_token)):
    scheda = await db.schede_impianto_picc.find_one({"id": scheda_id}, {"_id": 0})
    if not scheda:
        raise HTTPException(status_code=404, detail="Scheda non trovata")
    if scheda["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.schede_impianto_picc.update_one({"id": scheda_id}, {"$set": data})
    updated = await db.schede_impianto_picc.find_one({"id": scheda_id}, {"_id": 0})
    return updated

# ============== IMPLANT STATISTICS ==============
@api_router.get("/statistics/implants")
async def get_implant_statistics(
    ambulatorio: Ambulatorio,
    anno: int,
    mese: Optional[int] = None,
    payload: dict = Depends(verify_token)
):
    """Get statistics for implants (PICC, Port, Midline, etc.)"""
    if ambulatorio.value not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    # Build date range query
    if mese:
        start_date = f"{anno}-{mese:02d}-01"
        if mese == 12:
            end_date = f"{anno + 1}-01-01"
        else:
            end_date = f"{anno}-{mese + 1:02d}-01"
    else:
        start_date = f"{anno}-01-01"
        end_date = f"{anno + 1}-01-01"
    
    # Query implants
    query = {
        "ambulatorio": ambulatorio.value,
        "data_impianto": {"$gte": start_date, "$lt": end_date}
    }
    
    schede = await db.schede_impianto_picc.find(query, {"_id": 0}).to_list(1000)
    
    # Get list of existing patient IDs
    existing_patients = await db.patients.distinct("id", {"ambulatorio": ambulatorio.value})
    existing_patient_ids = set(existing_patients)
    
    # Count by type - only for existing patients
    tipo_counts = {}
    monthly_breakdown = {}
    
    for scheda in schede:
        # Skip if patient no longer exists
        patient_id = scheda.get("patient_id")
        if patient_id and patient_id not in existing_patient_ids:
            continue
            
        tipo = scheda.get("tipo_catetere", "altro")
        tipo_counts[tipo] = tipo_counts.get(tipo, 0) + 1
        
        # Monthly breakdown
        data_impianto = scheda.get("data_impianto", "")
        if data_impianto:
            month_key = data_impianto[:7]  # "YYYY-MM"
            if month_key not in monthly_breakdown:
                monthly_breakdown[month_key] = {}
            monthly_breakdown[month_key][tipo] = monthly_breakdown[month_key].get(tipo, 0) + 1
    
    # Labels for types
    tipo_labels = {
        "picc": "PICC",
        "picc_port": "PICC/Port",
        "midline": "Midline",
        "cvd_non_tunnellizzato": "CVC non tunnellizzato",
        "cvd_tunnellizzato": "CVC tunnellizzato",
        "port": "PORT",
    }
    
    return {
        "totale_impianti": len(schede),
        "per_tipo": tipo_counts,
        "tipo_labels": tipo_labels,
        "dettaglio_mensile": monthly_breakdown
    }

# ============== PATIENT FOLDER DOWNLOAD ==============
def generate_patient_pdf(patient: dict, schede_med: list, schede_impianto: list, schede_gestione: list, photos: list) -> bytes:
    """Generate a PDF with patient data - NO allegati, NO foto in scheda MED, only COMPLETE scheda impianto"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=TA_CENTER)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#1e40af'))
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=11, spaceAfter=6)
    
    story = []
    
    # Title
    story.append(Paragraph(f"Cartella Clinica - {patient.get('cognome', '')} {patient.get('nome', '')}", title_style))
    story.append(Spacer(1, 20))
    
    # SEZIONE 1: Dati Anagrafici
    story.append(Paragraph("Dati Anagrafici", heading_style))
    info_data = [
        ["Nome:", patient.get('nome', '-')],
        ["Cognome:", patient.get('cognome', '-')],
        ["Tipo:", patient.get('tipo', '-')],
        ["Codice Fiscale:", patient.get('codice_fiscale', '-')],
        ["Data di Nascita:", patient.get('data_nascita', '-')],
        ["Sesso:", patient.get('sesso', '-')],
        ["Telefono:", patient.get('telefono', '-')],
        ["Email:", patient.get('email', '-')],
        ["Medico di Base:", patient.get('medico_base', '-')],
        ["Stato:", patient.get('status', '-')],
    ]
    table = Table(info_data, colWidths=[4*cm, 12*cm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # SEZIONE 2: Anamnesi
    if patient.get('anamnesi') or patient.get('terapia_in_atto') or patient.get('allergie'):
        story.append(Paragraph("Anamnesi", heading_style))
        if patient.get('anamnesi'):
            story.append(Paragraph(f"<b>Anamnesi:</b> {patient.get('anamnesi', '-')}", normal_style))
        if patient.get('terapia_in_atto'):
            story.append(Paragraph(f"<b>Terapia in Atto:</b> {patient.get('terapia_in_atto', '-')}", normal_style))
        if patient.get('allergie'):
            story.append(Paragraph(f"<b>Allergie:</b> {patient.get('allergie', '-')}", normal_style))
        story.append(Spacer(1, 20))
    
    # SEZIONE 3: Schede Medicazione MED (senza anagrafica, senza foto)
    if schede_med:
        story.append(Paragraph("Schede Medicazione MED", heading_style))
        for idx, scheda in enumerate(schede_med, 1):
            story.append(Paragraph(f"<b>Medicazione #{idx} - Data: {scheda.get('data_compilazione', '-')}</b>", normal_style))
            story.append(Paragraph(f"Fondo: {', '.join(scheda.get('fondo', [])) or '-'}", normal_style))
            story.append(Paragraph(f"Margini: {', '.join(scheda.get('margini', [])) or '-'}", normal_style))
            story.append(Paragraph(f"Cute perilesionale: {', '.join(scheda.get('cute_perilesionale', [])) or '-'}", normal_style))
            story.append(Paragraph(f"Essudato Quantità: {scheda.get('essudato_quantita', '-')}", normal_style))
            story.append(Paragraph(f"Essudato Tipo: {', '.join(scheda.get('essudato_tipo', [])) or '-'}", normal_style))
            if scheda.get('medicazione'):
                story.append(Paragraph(f"Medicazione: {scheda.get('medicazione', '-')}", normal_style))
            if scheda.get('prossimo_cambio'):
                story.append(Paragraph(f"Prossimo Cambio: {scheda.get('prossimo_cambio', '-')}", normal_style))
            if scheda.get('firma'):
                story.append(Paragraph(f"Firma Operatore: {scheda.get('firma', '-')}", normal_style))
            # NOTE: NO foto qui - le foto rimangono solo nell'applicativo
            story.append(Spacer(1, 15))
        story.append(Spacer(1, 10))
    
    # SEZIONE 4: Schede Impianto PICC - SOLO schede COMPLETE (no semplificata)
    # Filtro solo schede complete (priorità a complete)
    schede_complete = [s for s in schede_impianto if s.get('scheda_type') != 'semplificata']
    if schede_complete:
        story.append(Paragraph("Schede Impianto PICC (Complete)", heading_style))
        for idx, scheda in enumerate(schede_complete, 1):
            story.append(Paragraph(f"<b>Impianto #{idx} - Data: {scheda.get('data_impianto', '-')}</b>", normal_style))
            story.append(Paragraph(f"Presidio: {scheda.get('presidio_impianto', '-')}", normal_style))
            story.append(Paragraph(f"Tipo Catetere: {scheda.get('tipo_catetere', '-')}", normal_style))
            story.append(Paragraph(f"Sede: {scheda.get('sede', '-')}", normal_style))
            story.append(Paragraph(f"Braccio: {'Destro' if scheda.get('braccio') == 'dx' else 'Sinistro' if scheda.get('braccio') == 'sn' else '-'}", normal_style))
            story.append(Paragraph(f"Vena: {scheda.get('vena', '-')}", normal_style))
            story.append(Paragraph(f"Exit-site: {scheda.get('exit_site_cm', '-')} cm", normal_style))
            story.append(Paragraph(f"Tunnelizzazione: {'Sì' if scheda.get('tunnelizzazione') else 'No'}", normal_style))
            story.append(Paragraph(f"Ecoguidato: {'Sì' if scheda.get('ecoguidato') else 'No'}", normal_style))
            story.append(Paragraph(f"Precauzioni Barriera: {'Sì' if scheda.get('precauzioni_barriera') else 'No'}", normal_style))
            story.append(Paragraph(f"Disinfezione: {scheda.get('disinfettante', '-')}", normal_style))
            story.append(Paragraph(f"Sutureless Device: {'Sì' if scheda.get('sutureless_device') else 'No'}", normal_style))
            story.append(Paragraph(f"Medicazione Trasparente: {'Sì' if scheda.get('medicazione_trasparente') else 'No'}", normal_style))
            story.append(Paragraph(f"Controllo RX: {'Sì' if scheda.get('controllo_rx') else 'No'}", normal_style))
            story.append(Paragraph(f"Controllo ECG: {'Sì' if scheda.get('controllo_ecg') else 'No'}", normal_style))
            story.append(Paragraph(f"Modalità: {scheda.get('modalita', '-')}", normal_style))
            story.append(Paragraph(f"Motivazione: {scheda.get('motivazione', '-')}", normal_style))
            story.append(Paragraph(f"Operatore: {scheda.get('operatore', '-')}", normal_style))
            if scheda.get('note'):
                story.append(Paragraph(f"Note: {scheda.get('note', '-')}", normal_style))
            story.append(Spacer(1, 15))
        story.append(Spacer(1, 10))
    
    # PICC Gestione Schede (Monthly Management)
    if schede_gestione:
        story.append(Spacer(1, 20))
        story.append(Paragraph("Schede Gestione PICC (Accessi Venosi)", heading_style))
        
        # Define the items to display
        gestione_items = [
            ("data_giorno_mese", "Data (giorno/mese)"),
            ("uso_precauzioni_barriera", "Uso massime precauzioni barriera"),
            ("lavaggio_mani", "Lavaggio mani"),
            ("guanti_non_sterili", "Uso guanti non sterili"),
            ("cambio_guanti_sterili", "Cambio guanti con guanti sterili"),
            ("rimozione_medicazione_sutureless", "Rimozione medicazione e sostituzione sutureless"),
            ("rimozione_medicazione_straordinaria", "Rimozione medicazione ord/straordinaria"),
            ("ispezione_sito", "Ispezione del sito"),
            ("sito_dolente", "Sito dolente"),
            ("edema_arrossamento", "Presenza di edema/arrossamento"),
            ("disinfezione_sito", "Disinfezione del sito"),
            ("exit_site_cm", "Exit-site cm"),
            ("fissaggio_sutureless", "Fissaggio catetere con sutureless device"),
            ("medicazione_trasparente", "Medicazione semipermeabile trasparente"),
            ("lavaggio_fisiologica", "Lavaggio con fisiologica 10cc/20cc"),
            ("disinfezione_clorexidina", "Disinfezione Clorexidina 2%"),
            ("difficolta_aspirazione", "Difficoltà di aspirazione"),
            ("difficolta_iniezione", "Difficoltà iniezione"),
            ("medicazione_clorexidina_prolungato", "Medicazione Clorexidina rilascio prol."),
            ("port_protector", "Utilizzo Port Protector"),
            ("lock_eparina", "Lock eparina per lavaggi"),
            ("sostituzione_set", "Sostituzione set infusione"),
            ("ore_sostituzione_set", "Ore da precedente sostituzione set"),
            ("febbre", "Febbre"),
            ("emocoltura", "Prelievo emocoltura"),
            ("emocoltura_positiva", "Emocoltura positiva per CVC"),
            ("trasferimento", "Trasferimento altra struttura"),
            ("rimozione_cvc", "Rimozione CVC"),
            ("sigla_operatore", "SIGLA OPERATORE"),
        ]
        
        for scheda in schede_gestione:
            story.append(Paragraph(f"<b>Mese: {scheda.get('mese', '-')}</b>", normal_style))
            giorni = scheda.get('giorni', {})
            
            if giorni:
                # Sort dates
                sorted_dates = sorted(giorni.keys())
                num_cols = min(len(sorted_dates), 10)  # Max 10 columns per table for readability
                
                # Split into chunks if more than 10 dates
                for chunk_start in range(0, len(sorted_dates), 10):
                    chunk_dates = sorted_dates[chunk_start:chunk_start + 10]
                    
                    # Build header row
                    header_row = ["Attività"] + [d.split("-")[-1] for d in chunk_dates]  # Show day number
                    
                    # Build data rows
                    table_data = [header_row]
                    for item_id, item_label in gestione_items:
                        row = [item_label]
                        for date_str in chunk_dates:
                            val = giorni.get(date_str, {}).get(item_id, "-")
                            row.append(val if val else "-")
                        table_data.append(row)
                    
                    # Create table
                    col_widths = [5*cm] + [1.2*cm] * len(chunk_dates)
                    table = Table(table_data, colWidths=col_widths)
                    table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 6),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 10))
                
                # Add notes if present
                if scheda.get('note'):
                    story.append(Paragraph(f"<b>Note:</b> {scheda.get('note', '')}", normal_style))
            else:
                story.append(Paragraph("Nessuna medicazione registrata per questo mese.", normal_style))
            
            story.append(Spacer(1, 15))
    
    # NOTE: Allegati section removed from PDF download as per user request
    # Gli allegati NON vengono scaricati con la cartella paziente
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_patient_zip(patient: dict, schede_med: list, schede_impianto: list, schede_gestione: list, photos: list) -> bytes:
    """Generate a ZIP with patient data - NO allegati, only PDF cartella clinica"""
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add PDF summary (NO allegati, NO foto MED)
        pdf_data = generate_patient_pdf(patient, schede_med, schede_impianto, schede_gestione, [])
        zf.writestr(f"cartella_clinica_{patient.get('cognome', 'paziente')}_{patient.get('nome', '')}.pdf", pdf_data)
        
        # Add patient JSON data
        import json
        patient_json = json.dumps(patient, indent=2, ensure_ascii=False)
        zf.writestr("dati_paziente.json", patient_json)
        
        # Add MED schede as JSON (without photos)
        if schede_med:
            med_json = json.dumps(schede_med, indent=2, ensure_ascii=False)
            zf.writestr("schede_medicazione_med.json", med_json)
        
        # Add only COMPLETE PICC impianto schede as JSON (no semplificata)
        schede_complete = [s for s in schede_impianto if s.get('scheda_type') != 'semplificata']
        if schede_complete:
            impianto_json = json.dumps(schede_complete, indent=2, ensure_ascii=False)
            zf.writestr("schede_impianto_picc.json", impianto_json)
        
        # Add PICC gestione schede as JSON
        if schede_gestione:
            gestione_json = json.dumps(schede_gestione, indent=2, ensure_ascii=False)
            zf.writestr("schede_gestione_picc.json", gestione_json)
        
        # NOTE: NO allegati nel ZIP - si scaricano singolarmente
    
    buffer.seek(0)
    return buffer.getvalue()


@api_router.get("/patients/{patient_id}/download/pdf")
async def download_patient_pdf(patient_id: str, payload: dict = Depends(verify_token)):
    """Download patient folder as PDF - NO allegati, NO foto MED"""
    patient = await db.patients.find_one({"id": patient_id}, {"_id": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Paziente non trovato")
    if patient["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    # Fetch all related data (NO photos - allegati si scaricano separatamente)
    schede_med = await db.schede_medicazione_med.find({"patient_id": patient_id}, {"_id": 0}).to_list(1000)
    schede_impianto = await db.schede_impianto_picc.find({"patient_id": patient_id}, {"_id": 0}).to_list(1000)
    schede_gestione = await db.schede_gestione_picc.find({"patient_id": patient_id}, {"_id": 0}).to_list(1000)
    
    # NO photos passed - allegati NOT included in cartella paziente
    pdf_data = generate_patient_pdf(patient, schede_med, schede_impianto, schede_gestione, [])
    
    filename = f"cartella_{patient.get('cognome', 'paziente')}_{patient.get('nome', '')}.pdf"
    
    return StreamingResponse(
        io.BytesIO(pdf_data),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@api_router.get("/patients/{patient_id}/download/zip")
async def download_patient_zip(patient_id: str, payload: dict = Depends(verify_token)):
    """Download patient folder as ZIP - NO allegati (si scaricano singolarmente)"""
    patient = await db.patients.find_one({"id": patient_id}, {"_id": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Paziente non trovato")
    if patient["ambulatorio"] not in payload["ambulatori"]:
        raise HTTPException(status_code=403, detail="Non hai accesso a questo ambulatorio")
    
    # Fetch all related data - NO photos (allegati si scaricano separatamente)
    schede_med = await db.schede_medicazione_med.find({"patient_id": patient_id}, {"_id": 0}).to_list(1000)
    schede_impianto = await db.schede_impianto_picc.find({"patient_id": patient_id}, {"_id": 0}).to_list(1000)
    schede_gestione = await db.schede_gestione_picc.find({"patient_id": patient_id}, {"_id": 0}).to_list(1000)
    
    zip_data = generate_patient_zip(patient, schede_med, schede_impianto, schede_gestione, [])
    
    filename = f"cartella_{patient.get('cognome', 'paziente')}_{patient.get('nome', '')}.zip"
    
    return StreamingResponse(
        io.BytesIO(zip_data),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ============== ROOT ==============
@api_router.get("/")
async def root():
    return {"message": "Ambulatorio Infermieristico API", "version": "1.0.0"}

# ============== PRESCRIZIONI ==============
class PrescrizioneCreate(BaseModel):
    patient_id: str
    ambulatorio: Ambulatorio
    data_inizio: str  # YYYY-MM-DD
    durata_mesi: int = 1  # 1, 2, or 3 months

class Prescrizione(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    ambulatorio: Ambulatorio
    data_inizio: str
    durata_mesi: int
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@api_router.get("/prescrizioni")
async def get_prescrizioni(
    ambulatorio: Ambulatorio,
    current_user: dict = Depends(get_current_user)
):
    """Get all prescriptions for an ambulatorio"""
    cursor = db.prescrizioni.find({"ambulatorio": ambulatorio})
    prescrizioni = await cursor.to_list(length=1000)
    result = []
    for p in prescrizioni:
        item = {
            "id": p.get("id", str(p.get("_id", ""))),
            "patient_id": p.get("patient_id"),
            "ambulatorio": p.get("ambulatorio"),
            "data_inizio": p.get("data_inizio"),
            "durata_mesi": p.get("durata_mesi"),
            "created_at": p.get("created_at"),
            "updated_at": p.get("updated_at")
        }
        result.append(item)
    return result

@api_router.post("/prescrizioni")
async def create_or_update_prescrizione(
    data: PrescrizioneCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create or update a prescription for a patient"""
    # Check if prescription already exists for this patient
    existing = await db.prescrizioni.find_one({
        "patient_id": data.patient_id,
        "ambulatorio": data.ambulatorio
    })
    
    if existing:
        # Update existing
        await db.prescrizioni.update_one(
            {"_id": existing["_id"]},
            {
                "$set": {
                    "data_inizio": data.data_inizio,
                    "durata_mesi": data.durata_mesi,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        return {"message": "Prescrizione aggiornata", "id": existing.get("id")}
    else:
        # Create new
        prescrizione = Prescrizione(
            patient_id=data.patient_id,
            ambulatorio=data.ambulatorio,
            data_inizio=data.data_inizio,
            durata_mesi=data.durata_mesi
        )
        await db.prescrizioni.insert_one(prescrizione.model_dump())
        return {"message": "Prescrizione creata", "id": prescrizione.id}

@api_router.delete("/prescrizioni/{patient_id}")
async def delete_prescrizione(
    patient_id: str,
    ambulatorio: Ambulatorio,
    current_user: dict = Depends(get_current_user)
):
    """Delete a prescription for a patient"""
    result = await db.prescrizioni.delete_one({
        "patient_id": patient_id,
        "ambulatorio": ambulatorio
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Prescrizione non trovata")
    return {"message": "Prescrizione eliminata"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
