import { useState, useRef } from "react";
import { apiClient } from "@/App";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { ScrollArea } from "@/components/ui/scroll-area";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Plus, FileText, Edit2, Trash2, Save, Printer, Download, FileDown } from "lucide-react";
import { toast } from "sonner";
import { format } from "date-fns";
import { it } from "date-fns/locale";

const TIPO_CATETERE_OPTIONS = [
  { id: "picc", label: "PICC" },
  { id: "picc_port", label: "PICC/Port" },
  { id: "midline", label: "Midline" },
  { id: "cvd_non_tunnellizzato", label: "CVC non tunnellizzato" },
  { id: "cvd_tunnellizzato", label: "CVC tunnellizzato" },
  { id: "port", label: "PORT" },
];

const VENA_OPTIONS = [
  { id: "basilica", label: "Basilica" },
  { id: "cefalica", label: "Cefalica" },
  { id: "brachiale", label: "Brachiale" },
];

const MODALITA_OPTIONS = [
  { id: "emergenza", label: "Emergenza" },
  { id: "urgenza", label: "Urgenza" },
  { id: "elezione", label: "Elezione" },
];

const MOTIVAZIONE_OPTIONS = [
  { id: "chemioterapia", label: "Chemioterapia" },
  { id: "difficolta_vene", label: "Difficoltà nel reperire vene" },
  { id: "terapia_prolungata", label: "Terapia prolungata" },
  { id: "monitoraggio", label: "Monitoraggio invasivo" },
  { id: "altro", label: "Altro" },
];

export const SchedaImpiantoPICC = ({ patientId, ambulatorio, schede, onRefresh }) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedScheda, setSelectedScheda] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    scheda_type: "semplificata",
    data_impianto: format(new Date(), "yyyy-MM-dd"),
    presidio_impianto: "",
    tipo_catetere: "",
    braccio: "",
    vena: "",
    tunnelizzazione: false,
    tunnelizzazione_note: "", // Max 6 caratteri
    exit_site_cm: "",
    operatore: "",
  });

  const handleCreate = async () => {
    setSaving(true);
    try {
      await apiClient.post("/schede-impianto-picc", {
        patient_id: patientId,
        ambulatorio,
        ...formData,
      });
      toast.success("Scheda impianto creata");
      setDialogOpen(false);
      resetForm();
      onRefresh();
    } catch (error) {
      toast.error("Errore nella creazione");
    } finally {
      setSaving(false);
    }
  };

  const handleUpdate = async () => {
    if (!selectedScheda) return;
    
    setSaving(true);
    try {
      await apiClient.put(`/schede-impianto-picc/${selectedScheda.id}`, {
        data_impianto: selectedScheda.data_impianto,
        presidio_impianto: selectedScheda.presidio_impianto,
        tipo_catetere: selectedScheda.tipo_catetere,
        braccio: selectedScheda.braccio,
        vena: selectedScheda.vena,
        exit_site_cm: selectedScheda.exit_site_cm,
        tunnelizzazione: selectedScheda.tunnelizzazione,
        tunnelizzazione_note: selectedScheda.tunnelizzazione_note,
        operatore: selectedScheda.operatore,
      });
      toast.success("Scheda aggiornata");
      setIsEditing(false);
      onRefresh();
    } catch (error) {
      toast.error("Errore nell'aggiornamento");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedScheda) return;
    
    try {
      await apiClient.delete(`/schede-impianto-picc/${selectedScheda.id}`);
      toast.success("Scheda eliminata");
      setDeleteDialogOpen(false);
      setEditDialogOpen(false);
      onRefresh();
    } catch (error) {
      toast.error("Errore nell'eliminazione");
    }
  };

  const handleOpenView = (scheda) => {
    setSelectedScheda({ ...scheda });
    setIsEditing(false);
    setEditDialogOpen(true);
  };

  const resetForm = () => {
    setFormData({
      scheda_type: "semplificata",
      data_impianto: format(new Date(), "yyyy-MM-dd"),
      presidio_impianto: "",
      tipo_catetere: "",
      braccio: "",
      vena: "",
      tunnelizzazione: false,
      tunnelizzazione_note: "",
      exit_site_cm: "",
      operatore: "",
    });
  };

  // Handle print/download PDF
  const handlePrintScheda = () => {
    if (!selectedScheda) return;
    
    // Create printable content
    const printContent = document.getElementById('scheda-print-content');
    if (printContent) {
      const printWindow = window.open('', '_blank');
      printWindow.document.write(`
        <html>
          <head>
            <title>Scheda Impianto - ${selectedScheda.data_impianto}</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 20px; }
              h1 { color: #166534; font-size: 18px; margin-bottom: 10px; }
              h2 { font-size: 14px; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 20px; }
              .field { margin: 8px 0; }
              .field-label { font-weight: bold; color: #555; }
              .field-value { margin-left: 10px; }
              .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
              .checkbox { display: inline-block; width: 12px; height: 12px; border: 1px solid #000; margin-right: 5px; }
              .checked { background: #166534; }
              @media print { body { margin: 0; } }
            </style>
          </head>
          <body>
            ${printContent.innerHTML}
          </body>
        </html>
      `);
      printWindow.document.close();
      printWindow.print();
    }
  };

  const handleDownloadPDF = async () => {
    if (!selectedScheda) return;
    
    // Only allow download for complete scheda type
    if (selectedScheda.scheda_type === "semplificata") {
      toast.error("La scheda semplificata non è scaricabile");
      return;
    }
    
    try {
      toast.info("Generazione PDF in corso...");
      const response = await apiClient.get(`/schede-impianto-picc/${selectedScheda.id}/pdf`, {
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `scheda_impianto_${selectedScheda.data_impianto}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success("PDF scaricato!");
    } catch (error) {
      toast.error("Errore nel download del PDF");
    }
  };

  const updateField = (field, value, isEditMode = false) => {
    if (isEditMode) {
      setSelectedScheda(prev => ({ ...prev, [field]: value }));
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }
  };

  // Render SIMPLIFIED form fields
  const renderSimplifiedForm = (data, isEditMode = false) => (
    <div className="space-y-6">
      <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg">
        <p className="text-sm text-emerald-700 font-medium">Versione Semplificata</p>
        <p className="text-xs text-emerald-600">Campi essenziali per registrazione rapida</p>
      </div>
      
      {/* Basic Info */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label>Data Impianto *</Label>
          <Input
            type="date"
            value={data.data_impianto || ""}
            onChange={(e) => updateField("data_impianto", e.target.value, isEditMode)}
          />
        </div>
        <div className="space-y-2">
          <Label>Presidio di Impianto</Label>
          <Input
            value={data.presidio_impianto || ""}
            onChange={(e) => updateField("presidio_impianto", e.target.value, isEditMode)}
            placeholder="Es: Ospedale San Giovanni"
          />
        </div>
      </div>

      {/* Tipo Impianto */}
      <div className="space-y-2">
        <Label>Tipo di Impianto *</Label>
        <Select
          value={data.tipo_catetere || ""}
          onValueChange={(value) => updateField("tipo_catetere", value, isEditMode)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Seleziona tipo" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="picc">PICC</SelectItem>
            <SelectItem value="picc_port">PICC Port</SelectItem>
            <SelectItem value="midline">Midline</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Positioning */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label>Braccio *</Label>
          <Select
            value={data.braccio || ""}
            onValueChange={(value) => updateField("braccio", value, isEditMode)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Seleziona" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="dx">Destro</SelectItem>
              <SelectItem value="sn">Sinistro</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label>Vena *</Label>
          <Select
            value={data.vena || ""}
            onValueChange={(value) => updateField("vena", value, isEditMode)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Seleziona" />
            </SelectTrigger>
            <SelectContent>
              {VENA_OPTIONS.map((opt) => (
                <SelectItem key={opt.id} value={opt.id}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Tunnelizzazione */}
      <div className="space-y-3">
        <div className="flex items-center space-x-3 p-3 border rounded-lg">
          <Checkbox
            id={`tunnelizzazione-${isEditMode ? 'edit' : 'new'}`}
            checked={data.tunnelizzazione || false}
            onCheckedChange={(checked) => updateField("tunnelizzazione", !!checked, isEditMode)}
          />
          <Label htmlFor={`tunnelizzazione-${isEditMode ? 'edit' : 'new'}`} className="font-medium">
            Tunnelizzazione
          </Label>
        </div>
        {/* Campo note che appare solo quando tunnelizzazione è selezionato */}
        {data.tunnelizzazione && (
          <div className="ml-6 space-y-1">
            <Label className="text-sm">Note (max 6 caratteri)</Label>
            <Input
              value={data.tunnelizzazione_note || ""}
              onChange={(e) => {
                // Limita a 6 caratteri
                const value = e.target.value.slice(0, 6);
                updateField("tunnelizzazione_note", value, isEditMode);
              }}
              placeholder="Note"
              maxLength={6}
              className="w-24"
            />
          </div>
        )}
      </div>

      {/* Exit-site */}
      <div className="space-y-2">
        <Label>Exit-site (cm)</Label>
        <Input
          value={data.exit_site_cm || ""}
          onChange={(e) => updateField("exit_site_cm", e.target.value, isEditMode)}
          placeholder="Distanza in cm dall'inserzione"
        />
      </div>

      {/* Operatore */}
      <div className="space-y-2">
        <Label>Operatore</Label>
        <Input
          value={data.operatore || ""}
          onChange={(e) => updateField("operatore", e.target.value, isEditMode)}
          placeholder="Nome operatore"
        />
      </div>
    </div>
  );

  // Render form fields (COMPLETE VERSION)
  const renderFormFields = (data, isEditMode = false) => (
    <div className="space-y-6">
      {/* Basic Info */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label>Data Impianto *</Label>
          <Input
            type="date"
            value={data.data_impianto || ""}
            onChange={(e) => updateField("data_impianto", e.target.value, isEditMode)}
          />
        </div>
        <div className="space-y-2">
          <Label>Tipo di Dispositivo *</Label>
          <Select
            value={data.tipo_catetere || ""}
            onValueChange={(value) => updateField("tipo_catetere", value, isEditMode)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Seleziona tipo" />
            </SelectTrigger>
            <SelectContent>
              {TIPO_CATETERE_OPTIONS.map((opt) => (
                <SelectItem key={opt.id} value={opt.id}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Positioning */}
      <div className="form-section">
        <div className="form-section-title">Posizionamento</div>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-2">
            <Label>Braccio</Label>
            <Select
              value={data.braccio || ""}
              onValueChange={(value) => updateField("braccio", value, isEditMode)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleziona" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="dx">Destro</SelectItem>
                <SelectItem value="sn">Sinistro</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Vena</Label>
            <Select
              value={data.vena || ""}
              onValueChange={(value) => updateField("vena", value, isEditMode)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleziona" />
              </SelectTrigger>
              <SelectContent>
                {VENA_OPTIONS.map((opt) => (
                  <SelectItem key={opt.id} value={opt.id}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Exit-site (cm)</Label>
            <Input
              value={data.exit_site_cm || ""}
              onChange={(e) => updateField("exit_site_cm", e.target.value, isEditMode)}
              placeholder="es: 35"
            />
          </div>
        </div>

        <div className="space-y-2 mt-4">
          <Label>Sede *</Label>
          <Input
            value={data.sede || ""}
            onChange={(e) => updateField("sede", e.target.value, isEditMode)}
            placeholder="Descrizione sede di inserimento"
          />
        </div>
      </div>

      {/* Procedure Details */}
      <div className="form-section">
        <div className="form-section-title">Dettagli Procedura</div>
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <Checkbox
              id={`ecoguidato-${isEditMode ? 'edit' : 'new'}`}
              checked={data.ecoguidato || false}
              onCheckedChange={(checked) => updateField("ecoguidato", !!checked, isEditMode)}
            />
            <Label htmlFor={`ecoguidato-${isEditMode ? 'edit' : 'new'}`}>Impianto ecoguidato</Label>
          </div>

          <div className="space-y-2">
            <Label>Igiene delle mani</Label>
            <Select
              value={data.igiene_mani || ""}
              onValueChange={(value) => updateField("igiene_mani", value, isEditMode)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleziona" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="lavaggio_antisettico">Lavaggio antisettico</SelectItem>
                <SelectItem value="frizione_alcolica">Frizione alcolica</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id={`precauzioni-${isEditMode ? 'edit' : 'new'}`}
              checked={data.precauzioni_barriera || false}
              onCheckedChange={(checked) => updateField("precauzioni_barriera", !!checked, isEditMode)}
            />
            <Label htmlFor={`precauzioni-${isEditMode ? 'edit' : 'new'}`}>
              Massime precauzioni di barriera
            </Label>
          </div>

          <div className="space-y-2">
            <Label>Disinfezione cute</Label>
            <Select
              value={data.disinfettante || ""}
              onValueChange={(value) => updateField("disinfettante", value, isEditMode)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleziona" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="clorexidina_2">Clorexidina 2% alcolica</SelectItem>
                <SelectItem value="iodiopovidone">Iodiopovidone</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center space-x-2">
              <Checkbox
                id={`sutureless-${isEditMode ? 'edit' : 'new'}`}
                checked={data.sutureless_device || false}
                onCheckedChange={(checked) => updateField("sutureless_device", !!checked, isEditMode)}
              />
              <Label htmlFor={`sutureless-${isEditMode ? 'edit' : 'new'}`}>Sutureless device</Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id={`medicazione-${isEditMode ? 'edit' : 'new'}`}
                checked={data.medicazione_trasparente || false}
                onCheckedChange={(checked) => updateField("medicazione_trasparente", !!checked, isEditMode)}
              />
              <Label htmlFor={`medicazione-${isEditMode ? 'edit' : 'new'}`}>Medicazione trasparente</Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id={`rx-${isEditMode ? 'edit' : 'new'}`}
                checked={data.controllo_rx || false}
                onCheckedChange={(checked) => updateField("controllo_rx", !!checked, isEditMode)}
              />
              <Label htmlFor={`rx-${isEditMode ? 'edit' : 'new'}`}>Controllo RX</Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id={`ecg-${isEditMode ? 'edit' : 'new'}`}
                checked={data.controllo_ecg || false}
                onCheckedChange={(checked) => updateField("controllo_ecg", !!checked, isEditMode)}
              />
              <Label htmlFor={`ecg-${isEditMode ? 'edit' : 'new'}`}>Controllo ECG</Label>
            </div>
          </div>
        </div>
      </div>

      {/* Clinical Info */}
      <div className="form-section">
        <div className="form-section-title">Informazioni Cliniche</div>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label>Modalità</Label>
            <Select
              value={data.modalita || ""}
              onValueChange={(value) => updateField("modalita", value, isEditMode)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleziona" />
              </SelectTrigger>
              <SelectContent>
                {MODALITA_OPTIONS.map((opt) => (
                  <SelectItem key={opt.id} value={opt.id}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Motivazione</Label>
            <Select
              value={data.motivazione || ""}
              onValueChange={(value) => updateField("motivazione", value, isEditMode)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Seleziona" />
              </SelectTrigger>
              <SelectContent>
                {MOTIVAZIONE_OPTIONS.map((opt) => (
                  <SelectItem key={opt.id} value={opt.id}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="space-y-2 mt-4">
          <Label>Operatore</Label>
          <Input
            value={data.operatore || ""}
            onChange={(e) => updateField("operatore", e.target.value, isEditMode)}
            placeholder="Nome operatore"
          />
        </div>

        <div className="space-y-2 mt-4">
          <Label>Note</Label>
          <Textarea
            value={data.note || ""}
            onChange={(e) => updateField("note", e.target.value, isEditMode)}
            rows={3}
          />
        </div>
      </div>
    </div>
  );

  // Render SIMPLIFIED VIEW (read-only)
  const renderSimplifiedView = (data) => (
    <div className="space-y-4">
      <h1 className="text-lg font-bold text-emerald-700">Scheda Impianto PICC</h1>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label className="text-muted-foreground">Data Impianto</Label>
          <p className="font-medium">{format(new Date(data.data_impianto), "d MMMM yyyy", { locale: it })}</p>
        </div>
        <div>
          <Label className="text-muted-foreground">Presidio di Impianto</Label>
          <p>{data.presidio_impianto || "-"}</p>
        </div>
      </div>
      
      <div>
        <Label className="text-muted-foreground">Tipo di Impianto</Label>
        <p className="font-medium text-lg">{TIPO_CATETERE_OPTIONS.find((t) => t.id === data.tipo_catetere)?.label || data.tipo_catetere || "-"}</p>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label className="text-muted-foreground">Braccio</Label>
          <p>{data.braccio === "dx" ? "Destro" : data.braccio === "sn" ? "Sinistro" : "-"}</p>
        </div>
        <div>
          <Label className="text-muted-foreground">Vena</Label>
          <p>{VENA_OPTIONS.find((v) => v.id === data.vena)?.label || "-"}</p>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label className="text-muted-foreground">Tunnelizzazione</Label>
          <p className={data.tunnelizzazione ? "text-green-600 font-medium" : ""}>
            {data.tunnelizzazione ? `Sì${data.tunnelizzazione_note ? ` (${data.tunnelizzazione_note})` : ''}` : "No"}
          </p>
        </div>
        <div>
          <Label className="text-muted-foreground">Exit-site</Label>
          <p>{data.exit_site_cm ? `${data.exit_site_cm} cm` : "-"}</p>
        </div>
      </div>
      
      <div>
        <Label className="text-muted-foreground">Operatore</Label>
        <p>{data.operatore || "-"}</p>
      </div>
    </div>
  );

  // Render COMPLETE VIEW (read-only)
  const renderCompleteView = (data) => (
    <div className="space-y-4">
      <h1 className="text-lg font-bold text-emerald-700">Scheda Impianto PICC - Completa</h1>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label className="text-muted-foreground">Tipo Dispositivo</Label>
          <p className="font-medium">{TIPO_CATETERE_OPTIONS.find((t) => t.id === data.tipo_catetere)?.label || data.tipo_catetere}</p>
        </div>
        <div>
          <Label className="text-muted-foreground">Sede</Label>
          <p>{data.sede || "-"}</p>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <Label className="text-muted-foreground">Braccio</Label>
          <p>{data.braccio === "dx" ? "Destro" : data.braccio === "sn" ? "Sinistro" : "-"}</p>
        </div>
        <div>
          <Label className="text-muted-foreground">Vena</Label>
          <p>{VENA_OPTIONS.find((v) => v.id === data.vena)?.label || "-"}</p>
        </div>
        <div>
          <Label className="text-muted-foreground">Exit-site</Label>
          <p>{data.exit_site_cm ? `${data.exit_site_cm} cm` : "-"}</p>
        </div>
      </div>
      <div>
        <Label className="text-muted-foreground">Caratteristiche</Label>
        <div className="flex flex-wrap gap-2 mt-1">
          {data.tunnelizzazione && <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded">Tunnelizzato</span>}
          {data.ecoguidato && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Ecoguidato</span>}
          {data.precauzioni_barriera && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Precauzioni barriera</span>}
          {data.sutureless_device && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Sutureless device</span>}
          {data.medicazione_trasparente && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Medicazione trasparente</span>}
          {data.controllo_rx && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Controllo RX</span>}
          {data.controllo_ecg && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Controllo ECG</span>}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label className="text-muted-foreground">Modalità</Label>
          <p>{MODALITA_OPTIONS.find((m) => m.id === data.modalita)?.label || "-"}</p>
        </div>
        <div>
          <Label className="text-muted-foreground">Motivazione</Label>
          <p>{MOTIVAZIONE_OPTIONS.find((m) => m.id === data.motivazione)?.label || "-"}</p>
        </div>
      </div>
      <div>
        <Label className="text-muted-foreground">Operatore</Label>
        <p>{data.operatore || "-"}</p>
      </div>
      {data.note && (
        <div>
          <Label className="text-muted-foreground">Note</Label>
          <p className="whitespace-pre-wrap">{data.note}</p>
        </div>
      )}
    </div>
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold">Schede Impianto PICC</h2>
        <Button onClick={() => setDialogOpen(true)} data-testid="new-scheda-impianto-btn">
          <Plus className="w-4 h-4 mr-2" />
          Nuova Scheda
        </Button>
      </div>

      {schede.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="w-12 h-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">Nessuna scheda impianto presente</p>
            <Button
              variant="link"
              onClick={() => setDialogOpen(true)}
              className="mt-2"
            >
              Crea la prima scheda
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3">
          {schede.map((scheda) => (
            <Card
              key={scheda.id}
              className="cursor-pointer hover:border-primary/50 transition-colors"
              onClick={() => handleOpenView(scheda)}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">
                    Impianto del {format(new Date(scheda.data_impianto), "d MMMM yyyy", { locale: it })}
                  </CardTitle>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleOpenView(scheda);
                      }}
                    >
                      <Edit2 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-destructive hover:text-destructive"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedScheda(scheda);
                        setDeleteDialogOpen(true);
                      }}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {TIPO_CATETERE_OPTIONS.find((t) => t.id === scheda.tipo_catetere)?.label || scheda.tipo_catetere}
                  {scheda.sede && ` - ${scheda.sede}`}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh]">
          <DialogHeader>
            <DialogTitle>Nuova Scheda Impianto</DialogTitle>
            <DialogDescription>
              Scegli il tipo di scheda e compila i dati
            </DialogDescription>
          </DialogHeader>

          {/* Scheda Type Selection */}
          <div className="border-b pb-4 mb-4">
            <Label className="mb-3 block">Tipo di Scheda</Label>
            <RadioGroup 
              value={schedaType} 
              onValueChange={(value) => {
                setSchedaType(value);
                setFormData(prev => ({ ...prev, scheda_type: value }));
              }}
              className="flex gap-4"
            >
              <div className="flex items-center space-x-2 p-3 border rounded-lg cursor-pointer hover:border-primary">
                <RadioGroupItem value="semplificata" id="tipo-semplificata" />
                <Label htmlFor="tipo-semplificata" className="cursor-pointer">
                  <span className="font-medium">Semplificata</span>
                  <p className="text-xs text-muted-foreground">Campi essenziali</p>
                </Label>
              </div>
              <div className="flex items-center space-x-2 p-3 border rounded-lg cursor-pointer hover:border-primary">
                <RadioGroupItem value="completa" id="tipo-completa" />
                <Label htmlFor="tipo-completa" className="cursor-pointer">
                  <span className="font-medium">Completa</span>
                  <p className="text-xs text-muted-foreground">Tutti i dettagli</p>
                </Label>
              </div>
            </RadioGroup>
          </div>

          <ScrollArea className="max-h-[50vh] pr-4">
            {schedaType === "semplificata" 
              ? renderSimplifiedForm(formData, false)
              : renderFormFields(formData, false)
            }
          </ScrollArea>

          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Annulla
            </Button>
            <Button onClick={handleCreate} disabled={saving} data-testid="save-scheda-impianto-btn">
              {saving ? "Salvataggio..." : "Salva Scheda"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* View/Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh]">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <DialogTitle>
                Scheda del {selectedScheda && format(new Date(selectedScheda.data_impianto), "d MMMM yyyy", { locale: it })}
                {selectedScheda?.scheda_type === "semplificata" && (
                  <span className="ml-2 text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded">Semplificata</span>
                )}
              </DialogTitle>
              <div className="flex gap-2">
                {/* Only show PDF/Stampa for COMPLETE scheda */}
                {selectedScheda?.scheda_type !== "semplificata" && (
                  <>
                    <Button variant="outline" size="sm" onClick={handlePrintScheda}>
                      <Printer className="w-4 h-4 mr-2" />
                      Stampa
                    </Button>
                    <Button variant="outline" size="sm" onClick={handleDownloadPDF}>
                      <FileDown className="w-4 h-4 mr-2" />
                      PDF
                    </Button>
                  </>
                )}
                {!isEditing && (
                  <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
                    <Edit2 className="w-4 h-4 mr-2" />
                    Modifica
                  </Button>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  className="text-destructive"
                  onClick={() => setDeleteDialogOpen(true)}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Elimina
                </Button>
              </div>
            </div>
          </DialogHeader>

          {selectedScheda && (
            <>
              <ScrollArea className="max-h-[60vh] pr-4">
                {/* Printable content wrapper */}
                <div id="scheda-print-content">
                  {isEditing ? (
                    selectedScheda.scheda_type === "semplificata" 
                      ? renderSimplifiedForm(selectedScheda, true)
                      : renderFormFields(selectedScheda, true)
                  ) : (
                    selectedScheda.scheda_type === "semplificata" 
                      ? renderSimplifiedView(selectedScheda)
                      : renderCompleteView(selectedScheda)
                  )}
                </div>
              </ScrollArea>

              {isEditing && (
                <div className="flex justify-end gap-2 pt-4 border-t">
                  <Button variant="outline" onClick={() => setIsEditing(false)}>
                    Annulla
                  </Button>
                  <Button onClick={handleUpdate} disabled={saving}>
                    <Save className="w-4 h-4 mr-2" />
                    {saving ? "Salvataggio..." : "Salva Modifiche"}
                  </Button>
                </div>
              )}
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Eliminare questa scheda?</AlertDialogTitle>
            <AlertDialogDescription>
              Questa azione non può essere annullata. La scheda impianto verrà eliminata definitivamente.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Annulla</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Elimina
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default SchedaImpiantoPICC;
