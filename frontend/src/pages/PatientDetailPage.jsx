import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAmbulatorio, apiClient, API } from "@/App";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  ArrowLeft,
  User,
  FileText,
  Camera,
  Save,
  UserMinus,
  UserX,
  UserPlus,
  Plus,
  Trash2,
  Copy,
  Download,
  FileDown,
  FileArchive,
} from "lucide-react";
import { toast } from "sonner";
import { format } from "date-fns";
import { it } from "date-fns/locale";
import BodyMap from "@/components/BodyMap";
import SchedaMedicazioneMED from "@/components/SchedaMedicazioneMED";
import SchedaImpiantoPICC from "@/components/SchedaImpiantoPICC";
import SchedaGestionePICC from "@/components/SchedaGestionePICC";

// Simple custom select component without portal issues
const SimpleSelect = ({ value, onChange, options, placeholder }) => {
  const [isOpen, setIsOpen] = useState(false);
  const selectRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (selectRef.current && !selectRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const selectedOption = options.find(opt => opt.value === value);

  return (
    <div ref={selectRef} className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
      >
        <span className={selectedOption ? "" : "text-muted-foreground"}>
          {selectedOption?.label || placeholder}
        </span>
        <ChevronDown className={`h-4 w-4 opacity-50 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover text-popover-foreground shadow-md max-h-60 overflow-auto">
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              className={`w-full px-3 py-2 text-left text-sm hover:bg-accent hover:text-accent-foreground ${
                value === option.value ? 'bg-accent/50' : ''
              }`}
              onClick={() => {
                onChange(option.value);
                setIsOpen(false);
              }}
            >
              {option.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default function PatientDetailPage() {
  const { patientId } = useParams();
  const navigate = useNavigate();
  const { ambulatorio } = useAmbulatorio();
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState("anagrafica");
  const [statusDialogOpen, setStatusDialogOpen] = useState(false);
  const [statusAction, setStatusAction] = useState(null);
  const [statusReason, setStatusReason] = useState("");
  const [statusNotes, setStatusNotes] = useState("");

  // Medical records state
  const [schedeMED, setSchedeMED] = useState([]);
  const [schedeImpiantoPICC, setSchedeImpiantoPICC] = useState([]);
  const [schedeGestionePICC, setSchedeGestionePICC] = useState([]);
  const [photos, setPhotos] = useState([]);

  const fetchPatient = useCallback(async () => {
    try {
      const response = await apiClient.get(`/patients/${patientId}`);
      setPatient(response.data);
    } catch (error) {
      toast.error("Errore nel caricamento del paziente");
      navigate("/pazienti");
    } finally {
      setLoading(false);
    }
  }, [patientId, navigate]);

  // Download patient folder as PDF
  const handleDownloadPDF = async () => {
    try {
      toast.info("Generazione PDF in corso...");
      const response = await apiClient.get(`/patients/${patientId}/download/pdf`, {
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `cartella_${patient?.cognome}_${patient?.nome}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success("PDF scaricato con successo!");
    } catch (error) {
      toast.error("Errore nel download del PDF");
      console.error(error);
    }
  };

  // Download patient folder as ZIP
  const handleDownloadZIP = async () => {
    try {
      toast.info("Generazione ZIP in corso...");
      const response = await apiClient.get(`/patients/${patientId}/download/zip`, {
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: 'application/zip' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `cartella_${patient?.cognome}_${patient?.nome}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success("ZIP scaricato con successo!");
    } catch (error) {
      toast.error("Errore nel download dello ZIP");
      console.error(error);
    }
  };

  const fetchMedicalRecords = useCallback(async () => {
    if (!patient) return;

    try {
      const requests = [];

      // MED records
      if (patient.tipo === "MED" || patient.tipo === "PICC_MED") {
        requests.push(
          apiClient.get("/schede-medicazione-med", {
            params: { patient_id: patientId, ambulatorio },
          })
        );
      } else {
        requests.push(Promise.resolve({ data: [] }));
      }

      // PICC records
      if (patient.tipo === "PICC" || patient.tipo === "PICC_MED") {
        requests.push(
          apiClient.get("/schede-impianto-picc", {
            params: { patient_id: patientId, ambulatorio },
          }),
          apiClient.get("/schede-gestione-picc", {
            params: { patient_id: patientId, ambulatorio },
          })
        );
      } else {
        requests.push(Promise.resolve({ data: [] }), Promise.resolve({ data: [] }));
      }

      // Photos
      requests.push(
        apiClient.get("/photos", {
          params: { patient_id: patientId, ambulatorio },
        })
      );

      const [medRes, impiantoRes, gestioneRes, photosRes] = await Promise.all(requests);

      setSchedeMED(medRes.data);
      setSchedeImpiantoPICC(impiantoRes.data);
      setSchedeGestionePICC(gestioneRes.data);
      setPhotos(photosRes.data);
    } catch (error) {
      console.error("Error fetching medical records:", error);
    }
  }, [patient, patientId, ambulatorio]);

  useEffect(() => {
    fetchPatient();
  }, [fetchPatient]);

  useEffect(() => {
    if (patient) {
      fetchMedicalRecords();
    }
  }, [patient, fetchMedicalRecords]);

  const handleSavePatient = async () => {
    setSaving(true);
    try {
      await apiClient.put(`/patients/${patientId}`, patient);
      toast.success("Paziente aggiornato");
    } catch (error) {
      toast.error("Errore nel salvataggio");
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async () => {
    // Validation only for dimesso and sospeso
    if (statusAction === "dimesso" && !statusReason) {
      toast.error("Seleziona una motivazione");
      return;
    }
    if ((statusAction === "dimesso" && statusReason === "altro" && !statusNotes) ||
        (statusAction === "sospeso" && !statusNotes)) {
      toast.error("Inserisci una nota");
      return;
    }

    try {
      const updateData = {
        status: statusAction,
      };

      if (statusAction === "dimesso") {
        updateData.discharge_reason = statusReason;
        updateData.discharge_notes = statusNotes;
      } else if (statusAction === "sospeso") {
        updateData.suspend_notes = statusNotes;
      }
      // For in_cura, we just update status - history is preserved

      await apiClient.put(`/patients/${patientId}`, updateData);
      
      const messages = {
        in_cura: "Paziente ripreso in cura",
        dimesso: "Paziente dimesso",
        sospeso: "Paziente sospeso",
      };
      toast.success(messages[statusAction]);
      setStatusDialogOpen(false);
      
      if (statusAction !== "in_cura") {
        navigate("/pazienti");
      } else {
        fetchPatient(); // Refresh patient data
      }
    } catch (error) {
      toast.error("Errore nel cambio stato");
    }
  };

  const handleLesionMarkerAdd = (marker) => {
    const newMarkers = [...(patient.lesion_markers || []), marker];
    setPatient({ ...patient, lesion_markers: newMarkers });
  };

  const handleLesionMarkerRemove = (index) => {
    const newMarkers = patient.lesion_markers.filter((_, i) => i !== index);
    setPatient({ ...patient, lesion_markers: newMarkers });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!patient) return null;

  const isMED = patient.tipo === "MED" || patient.tipo === "PICC_MED";
  const isPICC = patient.tipo === "PICC" || patient.tipo === "PICC_MED";

  return (
    <div className="animate-fade-in" data-testid="patient-detail-page">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate("/pazienti")}
          data-testid="back-btn"
        >
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">
              {patient.cognome} {patient.nome}
            </h1>
            <Badge
              className={
                patient.tipo === "PICC"
                  ? "bg-emerald-100 text-emerald-700"
                  : patient.tipo === "MED"
                  ? "bg-blue-100 text-blue-700"
                  : "bg-purple-100 text-purple-700"
              }
            >
              {patient.tipo === "PICC_MED" ? "PICC + MED" : patient.tipo}
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">Cartella Clinica</p>
        </div>

        <div className="flex gap-2 flex-wrap">
          {/* Download Buttons */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" data-testid="download-folder-btn">
                <Download className="w-4 h-4 mr-2" />
                Scarica Cartella
                <ChevronDown className="w-4 h-4 ml-2" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleDownloadPDF} data-testid="download-pdf-btn">
                <FileDown className="w-4 h-4 mr-2 text-red-500" />
                Scarica PDF
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleDownloadZIP} data-testid="download-zip-btn">
                <FileArchive className="w-4 h-4 mr-2 text-amber-500" />
                Scarica ZIP (con foto)
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          
          {/* Show "Riprendi in Cura" for dimesso/sospeso patients */}
          {(patient.status === "dimesso" || patient.status === "sospeso") && (
            <Button
              variant="default"
              className="bg-green-600 hover:bg-green-700"
              onClick={() => {
                setStatusAction("in_cura");
                setStatusReason("");
                setStatusNotes("");
                setStatusDialogOpen(true);
              }}
              data-testid="reactivate-patient-btn"
            >
              <UserPlus className="w-4 h-4 mr-2" />
              Riprendi in Cura
            </Button>
          )}
          {patient.status === "in_cura" && (
            <>
              <Button
                variant="outline"
                onClick={() => {
                  setStatusAction("sospeso");
                  setStatusReason("");
                  setStatusNotes("");
                  setStatusDialogOpen(true);
                }}
                data-testid="suspend-patient-btn"
              >
                <UserX className="w-4 h-4 mr-2" />
                Sospendi
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setStatusAction("dimesso");
                  setStatusReason("");
                  setStatusNotes("");
                  setStatusDialogOpen(true);
                }}
                data-testid="discharge-patient-btn"
              >
                <UserMinus className="w-4 h-4 mr-2" />
                Dimetti
              </Button>
            </>
          )}
          {patient.status !== "in_cura" && (
            <Button
              variant="outline"
              onClick={() => {
                setStatusAction("sospeso");
                if (patient.status === "sospeso") {
                  setStatusAction("dimesso");
                }
                setStatusReason("");
                setStatusNotes("");
                setStatusDialogOpen(true);
              }}
              data-testid="change-status-btn"
            >
              {patient.status === "sospeso" ? (
                <>
                  <UserMinus className="w-4 h-4 mr-2" />
                  Dimetti
                </>
              ) : (
                <>
                  <UserX className="w-4 h-4 mr-2" />
                  Sospendi
                </>
              )}
            </Button>
          )}
          <Button onClick={handleSavePatient} disabled={saving} data-testid="save-patient-btn">
            <Save className="w-4 h-4 mr-2" />
            {saving ? "Salvataggio..." : "Salva"}
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="anagrafica" className="gap-2">
            <User className="w-4 h-4" />
            Anagrafica
          </TabsTrigger>
          {isMED && (
            <TabsTrigger value="medicazione-med" className="gap-2">
              <FileText className="w-4 h-4" />
              Medicazione MED
            </TabsTrigger>
          )}
          {isPICC && (
            <>
              <TabsTrigger value="impianto-picc" className="gap-2">
                <FileText className="w-4 h-4" />
                Impianto PICC
              </TabsTrigger>
              <TabsTrigger value="gestione-picc" className="gap-2">
                <FileText className="w-4 h-4" />
                Gestione PICC
              </TabsTrigger>
            </>
          )}
          <TabsTrigger value="foto" className="gap-2">
            <Camera className="w-4 h-4" />
            Foto
          </TabsTrigger>
        </TabsList>

        {/* Anagrafica Tab */}
        <TabsContent value="anagrafica">
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Personal Data */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Dati Anagrafici</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Cognome</Label>
                    <Input
                      value={patient.cognome}
                      onChange={(e) =>
                        setPatient({ ...patient, cognome: e.target.value })
                      }
                      data-testid="patient-cognome"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Nome</Label>
                    <Input
                      value={patient.nome}
                      onChange={(e) =>
                        setPatient({ ...patient, nome: e.target.value })
                      }
                      data-testid="patient-nome"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Data di Nascita</Label>
                    <Input
                      type="date"
                      value={patient.data_nascita || ""}
                      onChange={(e) =>
                        setPatient({ ...patient, data_nascita: e.target.value })
                      }
                      data-testid="patient-data-nascita"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Codice Fiscale</Label>
                    <Input
                      value={patient.codice_fiscale || ""}
                      onChange={(e) =>
                        setPatient({ ...patient, codice_fiscale: e.target.value.toUpperCase() })
                      }
                      data-testid="patient-cf"
                      maxLength={16}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Telefono</Label>
                    <Input
                      value={patient.telefono || ""}
                      onChange={(e) =>
                        setPatient({ ...patient, telefono: e.target.value })
                      }
                      data-testid="patient-telefono"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input
                      type="email"
                      value={patient.email || ""}
                      onChange={(e) =>
                        setPatient({ ...patient, email: e.target.value })
                      }
                      data-testid="patient-email"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Medico di Base</Label>
                  <Input
                    value={patient.medico_base || ""}
                    onChange={(e) =>
                      setPatient({ ...patient, medico_base: e.target.value })
                    }
                    data-testid="patient-medico"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Medical History */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Anamnesi</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Anamnesi</Label>
                  <Textarea
                    value={patient.anamnesi || ""}
                    onChange={(e) =>
                      setPatient({ ...patient, anamnesi: e.target.value })
                    }
                    rows={3}
                    data-testid="patient-anamnesi"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Terapia in Atto</Label>
                  <Textarea
                    value={patient.terapia_in_atto || ""}
                    onChange={(e) =>
                      setPatient({ ...patient, terapia_in_atto: e.target.value })
                    }
                    rows={2}
                    data-testid="patient-terapia"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Allergie</Label>
                  <Textarea
                    value={patient.allergie || ""}
                    onChange={(e) =>
                      setPatient({ ...patient, allergie: e.target.value })
                    }
                    rows={2}
                    data-testid="patient-allergie"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Body Map for MED patients */}
            {isMED && (
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-lg">Mappa Lesioni</CardTitle>
                  <CardDescription>
                    Clicca sulla sagoma per segnare la posizione delle lesioni
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <BodyMap
                    markers={patient.lesion_markers || []}
                    onAddMarker={handleLesionMarkerAdd}
                    onRemoveMarker={handleLesionMarkerRemove}
                  />
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Medicazione MED Tab */}
        {isMED && (
          <TabsContent value="medicazione-med">
            <SchedaMedicazioneMED
              patientId={patientId}
              ambulatorio={ambulatorio}
              schede={schedeMED}
              onRefresh={fetchMedicalRecords}
              patientInfo={patient}
            />
          </TabsContent>
        )}

        {/* Impianto PICC Tab */}
        {isPICC && (
          <TabsContent value="impianto-picc">
            <SchedaImpiantoPICC
              patientId={patientId}
              ambulatorio={ambulatorio}
              schede={schedeImpiantoPICC}
              onRefresh={fetchMedicalRecords}
            />
          </TabsContent>
        )}

        {/* Gestione PICC Tab */}
        {isPICC && (
          <TabsContent value="gestione-picc">
            <SchedaGestionePICC
              patientId={patientId}
              ambulatorio={ambulatorio}
              schede={schedeGestionePICC}
              onRefresh={fetchMedicalRecords}
              patientInfo={patient}
            />
          </TabsContent>
        )}

        {/* Photos Tab */}
        <TabsContent value="foto">
          <PhotoGallery
            patientId={patientId}
            ambulatorio={ambulatorio}
            patientTipo={patient.tipo}
            photos={photos}
            onRefresh={fetchMedicalRecords}
          />
        </TabsContent>
      </Tabs>

      {/* Status Change Dialog */}
      <Dialog open={statusDialogOpen} onOpenChange={setStatusDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {statusAction === "in_cura" && "Riprendi Paziente in Cura"}
              {statusAction === "dimesso" && "Dimetti Paziente"}
              {statusAction === "sospeso" && "Sospendi Paziente"}
            </DialogTitle>
            <DialogDescription>
              {statusAction === "in_cura"
                ? "Il paziente verrà riportato in stato 'In Cura'. Lo storico sarà conservato."
                : statusAction === "dimesso"
                ? "Seleziona la motivazione della dimissione"
                : "Inserisci una nota per la sospensione temporanea"}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {statusAction === "in_cura" && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-800">
                  Confermando, il paziente tornerà visibile nella lista &quot;In Cura&quot; e sarà possibile gestire nuovamente appuntamenti e schede.
                </p>
              </div>
            )}

            {statusAction === "dimesso" && (
              <div className="space-y-2">
                <Label>Motivazione *</Label>
                <Select value={statusReason} onValueChange={setStatusReason}>
                  <SelectTrigger>
                    <SelectValue placeholder="Seleziona motivazione" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="guarito">Guarito</SelectItem>
                    <SelectItem value="adi">ADI</SelectItem>
                    <SelectItem value="altro">Altro</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}

            {statusAction !== "in_cura" && (
              <div className="space-y-2">
                <Label>
                  Note {statusAction === "sospeso" || statusReason === "altro" ? "*" : ""}
                </Label>
                <Textarea
                  value={statusNotes}
                  onChange={(e) => setStatusNotes(e.target.value)}
                  placeholder={
                    statusAction === "sospeso"
                      ? "Es: Ricovero ospedaliero"
                      : "Inserisci note aggiuntive..."
                  }
                  rows={3}
                />
              </div>
            )}

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setStatusDialogOpen(false)}>
                Annulla
              </Button>
              <Button 
                onClick={handleStatusChange}
                className={statusAction === "in_cura" ? "bg-green-600 hover:bg-green-700" : ""}
              >
                Conferma
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Photo Gallery Component
function PhotoGallery({ patientId, ambulatorio, patientTipo, photos, onRefresh }) {
  const [uploading, setUploading] = useState(false);
  const [selectedPhoto, setSelectedPhoto] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("patient_id", patientId);
    formData.append("ambulatorio", ambulatorio);
    formData.append("tipo", patientTipo === "MED" ? "MED" : "PICC");
    formData.append("data", format(new Date(), "yyyy-MM-dd"));

    setUploading(true);
    try {
      await apiClient.post("/photos", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success("Foto caricata");
      onRefresh();
    } catch (error) {
      toast.error("Errore nel caricamento");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (photoId) => {
    try {
      await apiClient.delete(`/photos/${photoId}`);
      toast.success("Foto eliminata");
      onRefresh();
    } catch (error) {
      toast.error("Errore nell'eliminazione");
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold">Galleria Foto</h2>
        <label>
          <input
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleUpload}
            disabled={uploading}
          />
          <Button asChild disabled={uploading}>
            <span>
              <Camera className="w-4 h-4 mr-2" />
              {uploading ? "Caricamento..." : "Carica Foto"}
            </span>
          </Button>
        </label>
      </div>

      {photos.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Camera className="w-12 h-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">Nessuna foto presente</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {photos.map((photo) => (
            <Card
              key={photo.id}
              className="overflow-hidden cursor-pointer group"
              onClick={() => setSelectedPhoto(photo)}
            >
              <div className="aspect-square relative">
                <img
                  src={`data:image/jpeg;base64,${photo.image_data}`}
                  alt={photo.descrizione || "Foto paziente"}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <Button
                    variant="destructive"
                    size="icon"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(photo.id);
                    }}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <CardContent className="p-2">
                <p className="text-xs text-muted-foreground">
                  {format(new Date(photo.data), "d MMM yyyy", { locale: it })}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Photo Detail Dialog */}
      <Dialog open={!!selectedPhoto} onOpenChange={() => setSelectedPhoto(null)}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>
              Foto del {selectedPhoto && format(new Date(selectedPhoto.data), "d MMMM yyyy", { locale: it })}
            </DialogTitle>
          </DialogHeader>
          {selectedPhoto && (
            <img
              src={`data:image/jpeg;base64,${selectedPhoto.image_data}`}
              alt="Foto ingrandita"
              className="w-full rounded-lg"
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
