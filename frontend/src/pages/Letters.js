import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { useNavigate } from "react-router-dom";
import { Plus, Edit2, Trash2, Download, Eye, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { toast } from "sonner";

const Letters = () => {
  const navigate = useNavigate();
  const [letters, setLetters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [previewLetter, setPreviewLetter] = useState(null);
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);

  useEffect(() => {
    fetchLetters();
  }, []);

  const fetchLetters = async () => {
    try {
      const response = await axios.get(`${API}/letters`);
      setLetters(response.data);
    } catch (error) {
      console.error("Error fetching letters:", error);
      toast.error("Failed to fetch letters");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this letter?")) return;

    try {
      await axios.delete(`${API}/letters/${id}`);
      toast.success("Letter deleted successfully");
      fetchLetters();
    } catch (error) {
      console.error("Error deleting letter:", error);
      toast.error("Failed to delete letter");
    }
  };

  const handleDownload = async (id, letterNumber) => {
    try {
      const response = await axios.get(`${API}/letters/${id}/pdf`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `letter_${letterNumber.replace('/', '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success("Letter downloaded successfully");
    } catch (error) {
      console.error("Error downloading letter:", error);
      toast.error("Failed to download letter");
    }
  };

  const handlePreview = async (letter) => {
    try {
      const response = await axios.get(`${API}/letters/${letter.id}`);
      
      // Get company data
      let companyData = null;
      try {
        const companyResponse = await axios.get(`${API}/companies/${letter.company_id}`);
        companyData = companyResponse.data;
      } catch (companyError) {
        console.warn("Company not found, using letter data only");
        companyData = {
          name: "Company Information Not Available",
          address: "",
          phone: "",
          email: "",
          motto: ""
        };
      }
      
      setPreviewLetter({ ...response.data, company: companyData });
      setPreviewDialogOpen(true);
    } catch (error) {
      console.error("Error loading preview:", error);
      toast.error("Failed to load preview. Please try again.");
    }
  };

  const getLetterTypeLabel = (type) => {
    const types = {
      general: "Surat Umum",
      cooperation: "Surat Penawaran Kerja Sama",
      request: "Surat Permohonan"
    };
    return types[type] || type;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-600">Loading...</div>
      </div>
    );
  }

  return (
    <div data-testid="letters-page">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Surat Menyurat</h1>
          <p className="text-slate-600">Kelola surat resmi perusahaan</p>
        </div>
        <Button
          onClick={() => navigate('/letters/create')}
          data-testid="create-letter-btn"
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Plus size={20} className="mr-2" />
          Buat Surat Baru
        </Button>
      </div>

      {letters.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Mail size={64} className="text-slate-300 mb-4" />
            <h3 className="text-xl font-semibold text-slate-600 mb-2">Belum Ada Surat</h3>
            <p className="text-slate-500 mb-6">Mulai dengan membuat surat pertama Anda</p>
            <Button
              onClick={() => navigate('/letters/create')}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Plus size={20} className="mr-2" />
              Buat Surat Baru
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          {letters.map((letter) => (
            <Card key={letter.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="border-b">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-xl mb-2">{letter.subject}</CardTitle>
                    <div className="flex flex-wrap gap-4 text-sm text-slate-600">
                      <span>No: <strong>{letter.letter_number}</strong></span>
                      <span>Tanggal: {letter.date}</span>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                        {getLetterTypeLabel(letter.letter_type)}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handlePreview(letter)}
                      data-testid={`preview-letter-${letter.id}`}
                      className="text-blue-600 hover:text-blue-700"
                    >
                      <Eye size={18} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDownload(letter.id, letter.letter_number)}
                      data-testid={`download-letter-${letter.id}`}
                      className="text-green-600 hover:text-green-700"
                    >
                      <Download size={18} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/letters/edit/${letter.id}`)}
                      data-testid={`edit-letter-${letter.id}`}
                      className="text-slate-600 hover:text-slate-700"
                    >
                      <Edit2 size={18} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(letter.id)}
                      data-testid={`delete-letter-${letter.id}`}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 size={18} />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-slate-500">Penerima:</span>
                    <p className="font-medium">{letter.recipient_name}</p>
                    {letter.recipient_position && (
                      <p className="text-slate-600">{letter.recipient_position}</p>
                    )}
                  </div>
                  <div>
                    <span className="text-slate-500">Penandatangan:</span>
                    {letter.signatories && letter.signatories.length > 0 ? (
                      <div>
                        {letter.signatories.map((sig, idx) => (
                          <p key={idx} className="font-medium">
                            {sig.name} - {sig.position}
                          </p>
                        ))}
                      </div>
                    ) : (
                      <p className="text-slate-400">-</p>
                    )}
                  </div>
                </div>
                {letter.content && (
                  <div className="mt-4">
                    <p className="text-slate-700 line-clamp-2">{letter.content}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Preview Dialog */}
      <Dialog open={previewDialogOpen} onOpenChange={setPreviewDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Preview Surat</DialogTitle>
          </DialogHeader>
          {previewLetter && (
            <div className="preview-container bg-white p-8 rounded-lg border">
              {/* Company Header with Logo */}
              <div className="text-center mb-6 border-b-2 border-slate-800 pb-4">
                <div className="flex items-center justify-center gap-4 mb-2">
                  {previewLetter.company?.logo && (
                    <img
                      src={previewLetter.company.logo}
                      alt="Company Logo"
                      className="w-16 h-16 object-contain"
                    />
                  )}
                  <div>
                    <h1 className="text-2xl font-bold text-slate-800">{previewLetter.company?.name}</h1>
                    {previewLetter.company?.motto && (
                      <p className="text-sm text-slate-600 italic">{previewLetter.company.motto}</p>
                    )}
                  </div>
                </div>
                <p className="text-sm text-slate-600">{previewLetter.company?.address}</p>
                <p className="text-sm text-slate-600">
                  Tel: {previewLetter.company?.phone} | Email: {previewLetter.company?.email}
                </p>
                {previewLetter.company?.website && (
                  <p className="text-sm text-slate-600">Website: {previewLetter.company.website}</p>
                )}
              </div>

              {/* Letter Info */}
              <div className="mb-6">
                <div className="text-sm space-y-1">
                  <p><span className="font-semibold">Nomor:</span> {previewLetter.letter_number}</p>
                  <p><span className="font-semibold">Tanggal:</span> {previewLetter.date}</p>
                  {previewLetter.attachments_count > 0 && (
                    <p><span className="font-semibold">Lampiran:</span> {previewLetter.attachments_count} berkas</p>
                  )}
                  <p><span className="font-semibold">Perihal:</span> <strong>{previewLetter.subject}</strong></p>
                </div>
              </div>

              {/* Recipient */}
              <div className="mb-6">
                <p className="mb-2">Kepada Yth,</p>
                <p className="font-bold">{previewLetter.recipient_name}</p>
                {previewLetter.recipient_position && (
                  <p className="text-slate-700">{previewLetter.recipient_position}</p>
                )}
                {previewLetter.recipient_address && (
                  <p className="text-slate-700 whitespace-pre-wrap">{previewLetter.recipient_address}</p>
                )}
              </div>

              {/* Greeting */}
              <div className="mb-4">
                <p>Dengan hormat,</p>
              </div>

              {/* Content */}
              <div className="mb-6 text-justify space-y-3">
                {previewLetter.content?.split('\n').map((para, idx) => (
                  para.trim() && <p key={idx}>{para.trim()}</p>
                ))}
              </div>

              {/* Closing */}
              <div className="mb-8">
                {previewLetter.letter_type === 'general' && (
                  <p>Demikian surat ini kami sampaikan. Atas perhatian dan kerjasamanya, kami ucapkan terima kasih.</p>
                )}
                {previewLetter.letter_type === 'cooperation' && (
                  <p>Demikian surat penawaran kerjasama ini kami sampaikan. Besar harapan kami dapat menjalin kerjasama yang baik dengan perusahaan Bapak/Ibu.</p>
                )}
                {previewLetter.letter_type === 'request' && (
                  <p>Demikian permohonan ini kami sampaikan, atas perhatian dan perkenannya kami ucapkan terima kasih.</p>
                )}
              </div>

              {/* Signatories */}
              {previewLetter.signatories && previewLetter.signatories.length > 0 && (
                <div className="mb-6">
                  <div className="flex justify-around gap-4">
                    {previewLetter.signatories.map((sig, idx) => (
                      <div key={idx} className="text-center min-w-[200px]">
                        <p className="mb-2">{sig.position}</p>
                        {sig.signature_image ? (
                          <img
                            src={sig.signature_image}
                            alt={`Signature ${idx + 1}`}
                            className="h-16 mx-auto object-contain my-4"
                          />
                        ) : (
                          <div className="h-16 my-4"></div>
                        )}
                        <div className="border-t border-slate-800 pt-2">
                          <p className="font-bold">{sig.name}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* CC List */}
              {previewLetter.cc_list && (
                <div className="border-t pt-4 mt-6">
                  <p className="font-semibold mb-2">Tembusan:</p>
                  <div className="text-sm text-slate-700 space-y-1">
                    {previewLetter.cc_list.split('\n').map((cc, idx) => (
                      cc.trim() && <p key={idx}>- {cc.trim()}</p>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex justify-end gap-3 mt-6 pt-6 border-t">
                <Button
                  variant="outline"
                  onClick={() => setPreviewDialogOpen(false)}
                  data-testid="close-preview-btn"
                >
                  Close
                </Button>
                <Button
                  onClick={() => handleDownload(previewLetter.id, previewLetter.letter_number)}
                  className="bg-blue-600 hover:bg-blue-700"
                  data-testid="download-from-preview-btn"
                >
                  <Download size={18} className="mr-2" />
                  Download PDF
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Letters;