import { useState } from "react";
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
import { Plus, FileText, Edit2, Trash2, Save } from "lucide-react";
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
    data_impianto: format(new Date(), "yyyy-MM-dd"),
    tipo_catetere: "",
    sede: "",
    braccio: "",
    vena: "",
    exit_site_cm: "",
    ecoguidato: false,
    igiene_mani: "",
    precauzioni_barriera: false,
    disinfettante: "",
    sutureless_device: false,
    medicazione_trasparente: false,
    controllo_rx: false,
    controllo_ecg: false,
    modalita: "",
    motivazione: "",
    operatore: "",
    note: "",
  });

  const handleCreate = async () => {
    if (!formData.tipo_catetere || !formData.sede) {
      toast.error("Compila i campi obbligatori");
      return;
    }

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
        tipo_catetere: selectedScheda.tipo_catetere,
        sede: selectedScheda.sede,
        braccio: selectedScheda.braccio,
        vena: selectedScheda.vena,
        exit_site_cm: selectedScheda.exit_site_cm,
        ecoguidato: selectedScheda.ecoguidato,
        igiene_mani: selectedScheda.igiene_mani,
        precauzioni_barriera: selectedScheda.precauzioni_barriera,
        disinfettante: selectedScheda.disinfettante,
        sutureless_device: selectedScheda.sutureless_device,
        medicazione_trasparente: selectedScheda.medicazione_trasparente,
        controllo_rx: selectedScheda.controllo_rx,
        controllo_ecg: selectedScheda.controllo_ecg,
        modalita: selectedScheda.modalita,
        motivazione: selectedScheda.motivazione,
        operatore: selectedScheda.operatore,
        note: selectedScheda.note,
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
      data_impianto: format(new Date(), "yyyy-MM-dd"),
      tipo_catetere: "",
      sede: "",
      braccio: "",
      vena: "",
      exit_site_cm: "",
      ecoguidato: false,
      igiene_mani: "",
      precauzioni_barriera: false,
      disinfettante: "",
      sutureless_device: false,
      medicazione_trasparente: false,
      controllo_rx: false,
      controllo_ecg: false,
      modalita: "",
      motivazione: "",
      operatore: "",
      note: "",
    });
  };

  const updateField = (field, value, isEditMode = false) => {
    if (isEditMode) {
      setSelectedScheda(prev => ({ ...prev, [field]: value }));
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }
  };

  // Render form fields
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
              Compila i dati dell'impianto
            </DialogDescription>
          </DialogHeader>

          <ScrollArea className="max-h-[60vh] pr-4">
            {renderFormFields(formData, false)}
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
              </DialogTitle>
              <div className="flex gap-2">
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
                {isEditing ? (
                  renderFormFields(selectedScheda, true)
                ) : (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-muted-foreground">Tipo Dispositivo</Label>
                        <p className="font-medium">{TIPO_CATETERE_OPTIONS.find((t) => t.id === selectedScheda.tipo_catetere)?.label || selectedScheda.tipo_catetere}</p>
                      </div>
                      <div>
                        <Label className="text-muted-foreground">Sede</Label>
                        <p>{selectedScheda.sede || "-"}</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <Label className="text-muted-foreground">Braccio</Label>
                        <p>{selectedScheda.braccio === "dx" ? "Destro" : selectedScheda.braccio === "sn" ? "Sinistro" : "-"}</p>
                      </div>
                      <div>
                        <Label className="text-muted-foreground">Vena</Label>
                        <p>{VENA_OPTIONS.find((v) => v.id === selectedScheda.vena)?.label || "-"}</p>
                      </div>
                      <div>
                        <Label className="text-muted-foreground">Exit-site</Label>
                        <p>{selectedScheda.exit_site_cm ? `${selectedScheda.exit_site_cm} cm` : "-"}</p>
                      </div>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Caratteristiche</Label>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {selectedScheda.ecoguidato && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Ecoguidato</span>}
                        {selectedScheda.precauzioni_barriera && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Precauzioni barriera</span>}
                        {selectedScheda.sutureless_device && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Sutureless device</span>}
                        {selectedScheda.medicazione_trasparente && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Medicazione trasparente</span>}
                        {selectedScheda.controllo_rx && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Controllo RX</span>}
                        {selectedScheda.controllo_ecg && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Controllo ECG</span>}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-muted-foreground">Modalità</Label>
                        <p>{MODALITA_OPTIONS.find((m) => m.id === selectedScheda.modalita)?.label || "-"}</p>
                      </div>
                      <div>
                        <Label className="text-muted-foreground">Motivazione</Label>
                        <p>{MOTIVAZIONE_OPTIONS.find((m) => m.id === selectedScheda.motivazione)?.label || "-"}</p>
                      </div>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Operatore</Label>
                      <p>{selectedScheda.operatore || "-"}</p>
                    </div>
                    {selectedScheda.note && (
                      <div>
                        <Label className="text-muted-foreground">Note</Label>
                        <p className="whitespace-pre-wrap">{selectedScheda.note}</p>
                      </div>
                    )}
                  </div>
                )}
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
