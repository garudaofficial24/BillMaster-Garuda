import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { useNavigate, useParams } from "react-router-dom";
import { Plus, Trash2, ArrowLeft, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";

const EditLetter = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [companies, setCompanies] = useState([]);
  const [formData, setFormData] = useState({
    letter_number: "",
    company_id: "",
    date: new Date().toISOString().split('T')[0],
    subject: "",
    letter_type: "general",
    recipient_name: "",
    recipient_position: "",
    recipient_address: "",
    content: "",
    attachments_count: 0,
    cc_list: "",
  });
  const [signatories, setSignatories] = useState([{
    name: "",
    position: "",
    signature_image: null,
  }]);
  const [activities, setActivities] = useState([{
    no: 1,
    kegiatan: "",
    jumlah: "",
    satuan: "",
    hasil: "",
    keterangan: ""
  }]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCompanies();
    if (id) {
      fetchLetter();
    }
  }, [id]);

  const fetchCompanies = async () => {
    try {
      const response = await axios.get(`${API}/companies`);
      setCompanies(response.data);
    } catch (error) {
      console.error("Error fetching companies:", error);
    }
  };

  const fetchLetter = async () => {
    try {
      const response = await axios.get(`${API}/letters/${id}`);
      const letter = response.data;
      
      setFormData({
        letter_number: letter.letter_number,
        company_id: letter.company_id,
        date: letter.date,
        subject: letter.subject,
        letter_type: letter.letter_type,
        recipient_name: letter.recipient_name,
        recipient_position: letter.recipient_position || "",
        recipient_address: letter.recipient_address || "",
        content: letter.content,
        attachments_count: letter.attachments_count || 0,
        cc_list: letter.cc_list || "",
      });
      
      if (letter.signatories && letter.signatories.length > 0) {
        setSignatories(letter.signatories);
      }
      
      if (letter.activities && letter.activities.length > 0) {
        setActivities(letter.activities);
      }
      
      setLoading(false);
    } catch (error) {
      console.error("Error fetching letter:", error);
      toast.error("Failed to fetch letter");
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSignatoryChange = (index, field, value) => {
    const newSignatories = [...signatories];
    newSignatories[index][field] = value;
    setSignatories(newSignatories);
  };

  const handleSignatureUpload = async (index, file) => {
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast.error("Please upload an image file");
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      toast.error("File size must be less than 2MB");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/upload-signature`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const newSignatories = [...signatories];
      newSignatories[index].signature_image = response.data.signature;
      setSignatories(newSignatories);
      
      toast.success("Signature uploaded successfully");
    } catch (error) {
      console.error("Error uploading signature:", error);
      toast.error("Failed to upload signature");
    } finally {
      setUploading(false);
    }
  };

  const removeSignature = (index) => {
    const newSignatories = [...signatories];
    newSignatories[index].signature_image = null;
    setSignatories(newSignatories);
  };

  const addSignatory = () => {
    setSignatories([...signatories, {
      name: "",
      position: "",
      signature_image: null,
    }]);
  };

  const removeSignatory = (index) => {
    if (signatories.length > 1) {
      const newSignatories = signatories.filter((_, i) => i !== index);
      setSignatories(newSignatories);
    }
  };

  const handleActivityChange = (index, field, value) => {
    const newActivities = [...activities];
    newActivities[index][field] = value;
    setActivities(newActivities);
  };

  const addActivity = () => {
    const newNo = activities.length + 1;
    setActivities([...activities, {
      no: newNo,
      kegiatan: "",
      jumlah: "",
      satuan: "",
      hasil: "",
      keterangan: ""
    }]);
  };

  const removeActivity = (index) => {
    if (activities.length > 1) {
      const newActivities = activities.filter((_, i) => i !== index);
      // Renumber activities
      const renumbered = newActivities.map((act, idx) => ({
        ...act,
        no: idx + 1
      }));
      setActivities(renumbered);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.letter_number || !formData.company_id || !formData.subject || !formData.recipient_name || !formData.content) {
      toast.error("Please fill in all required fields");
      return;
    }

    const validSignatories = signatories.filter(sig => sig.name && sig.position);
    if (validSignatories.length === 0) {
      toast.error("Please add at least one signatory");
      return;
    }

    const submitData = {
      ...formData,
      attachments_count: parseInt(formData.attachments_count) || 0,
      activities: activities.filter(act => act.kegiatan.trim() !== ""),
      signatories: validSignatories,
    };

    try {
      await axios.put(`${API}/letters/${id}`, submitData);
      toast.success("Letter updated successfully");
      navigate('/letters');
    } catch (error) {
      console.error("Error updating letter:", error);
      toast.error("Failed to update letter");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-600">Loading...</div>
      </div>
    );
  }

  return (
    <div data-testid="edit-letter-page">
      <div className="mb-6">
        <Button
          variant="ghost"
          onClick={() => navigate('/letters')}
          data-testid="back-btn"
          className="mb-4"
        >
          <ArrowLeft size={20} className="mr-2" />
          Kembali ke Daftar Surat
        </Button>
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Edit Surat</h1>
        <p className="text-slate-600">Perbarui informasi surat</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Informasi Surat</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="letter_number">Nomor Surat *</Label>
                    <Input
                      id="letter_number"
                      name="letter_number"
                      data-testid="letter-number-input"
                      value={formData.letter_number}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="company_id">Perusahaan *</Label>
                    <select
                      id="company_id"
                      name="company_id"
                      data-testid="company-select"
                      value={formData.company_id}
                      onChange={handleInputChange}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                      required
                    >
                      <option value="">Pilih Perusahaan</option>
                      {companies.map((company) => (
                        <option key={company.id} value={company.id}>
                          {company.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="date">Tanggal *</Label>
                    <Input
                      id="date"
                      name="date"
                      type="date"
                      data-testid="letter-date-input"
                      value={formData.date}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="letter_type">Jenis Surat *</Label>
                    <select
                      id="letter_type"
                      name="letter_type"
                      data-testid="letter-type-select"
                      value={formData.letter_type}
                      onChange={handleInputChange}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    >
                      <option value="general">Surat Umum</option>
                      <option value="cooperation">Surat Penawaran Kerja Sama</option>
                      <option value="request">Surat Permohonan</option>
                    </select>
                  </div>
                </div>
                <div>
                  <Label htmlFor="subject">Perihal/Subjek *</Label>
                  <Input
                    id="subject"
                    name="subject"
                    data-testid="subject-input"
                    value={formData.subject}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="attachments_count">Jumlah Lampiran</Label>
                  <Input
                    id="attachments_count"
                    name="attachments_count"
                    type="number"
                    min="0"
                    data-testid="attachments-input"
                    value={formData.attachments_count}
                    onChange={handleInputChange}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Penerima Surat</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="recipient_name">Nama Penerima *</Label>
                  <Input
                    id="recipient_name"
                    name="recipient_name"
                    data-testid="recipient-name-input"
                    value={formData.recipient_name}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="recipient_position">Jabatan</Label>
                  <Input
                    id="recipient_position"
                    name="recipient_position"
                    data-testid="recipient-position-input"
                    value={formData.recipient_position}
                    onChange={handleInputChange}
                  />
                </div>
                <div>
                  <Label htmlFor="recipient_address">Alamat</Label>
                  <Textarea
                    id="recipient_address"
                    name="recipient_address"
                    data-testid="recipient-address-input"
                    value={formData.recipient_address}
                    onChange={handleInputChange}
                    rows={2}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Isi Surat</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="content">Isi Surat *</Label>
                  <Textarea
                    id="content"
                    name="content"
                    data-testid="content-input"
                    value={formData.content}
                    onChange={handleInputChange}
                    rows={10}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="cc_list">Tembusan (CC)</Label>
                  <Textarea
                    id="cc_list"
                    name="cc_list"
                    data-testid="cc-input"
                    value={formData.cc_list}
                    onChange={handleInputChange}
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Signatories Sidebar */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Penandatangan</CardTitle>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={addSignatory}
                    data-testid="add-signatory-btn"
                  >
                    <Plus size={16} className="mr-1" />
                    Tambah
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {signatories.map((signatory, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-3">
                    <div className="flex justify-between items-start">
                      <h4 className="font-medium text-sm">Penandatangan {index + 1}</h4>
                      {signatories.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeSignatory(index)}
                          className="text-red-600 hover:text-red-700 h-6 w-6 p-0"
                        >
                          <Trash2 size={14} />
                        </Button>
                      )}
                    </div>
                    <div>
                      <Label>Nama *</Label>
                      <Input
                        data-testid={`signatory-name-${index}`}
                        value={signatory.name}
                        onChange={(e) => handleSignatoryChange(index, 'name', e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <Label>Jabatan *</Label>
                      <Input
                        data-testid={`signatory-position-${index}`}
                        value={signatory.position}
                        onChange={(e) => handleSignatoryChange(index, 'position', e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <Label>Tanda Tangan (Opsional)</Label>
                      {signatory.signature_image ? (
                        <div className="relative border rounded p-2">
                          <img 
                            src={signatory.signature_image} 
                            alt="Signature" 
                            className="h-20 w-full object-contain"
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeSignature(index)}
                            className="absolute top-1 right-1 h-6 w-6 p-0 bg-red-100 hover:bg-red-200"
                          >
                            <X size={14} />
                          </Button>
                        </div>
                      ) : (
                        <Input
                          type="file"
                          accept="image/*"
                          onChange={(e) => handleSignatureUpload(index, e.target.files[0])}
                          disabled={uploading}
                          className="text-sm"
                        />
                      )}
                    </div>
                  </div>
                ))}
                <Button
                  type="submit"
                  data-testid="submit-letter-btn"
                  className="w-full bg-blue-600 hover:bg-blue-700 mt-4"
                  disabled={uploading}
                >
                  Update Surat
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </form>
    </div>
  );
};

export default EditLetter;
