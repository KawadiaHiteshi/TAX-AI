import React, { useEffect, useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { documentsAPI } from "../services/api";
import toast from "react-hot-toast";
import { Upload, FileText, Trash2, CheckCircle, Clock, AlertCircle, RefreshCw } from "lucide-react";

const STATUS_MAP: Record<string, { icon: React.ReactNode; label: string; cls: string }> = {
  processing: { icon: <Clock size={14} />, label: "Processing…", cls: "warning" },
  done: { icon: <CheckCircle size={14} />, label: "Extracted", cls: "success" },
  error: { icon: <AlertCircle size={14} />, label: "Error", cls: "error" },
};

export default function DocumentsPage() {
  const [docs, setDocs] = useState<any[]>([]);
  const [taxYear, setTaxYear] = useState(new Date().getFullYear() - 1);
  const [uploading, setUploading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedDoc, setExpandedDoc] = useState<number | null>(null);

  const load = async () => {
    const res = await documentsAPI.list();
    setDocs(res.data);
  };

  useEffect(() => { load(); }, []);

  // Auto-refresh processing docs
  useEffect(() => {
    const hasProcessing = docs.some((d) => d.status === "processing");
    if (!hasProcessing) return;
    const t = setTimeout(load, 3000);
    return () => clearTimeout(t);
  }, [docs]);

  const onDrop = useCallback(async (accepted: File[]) => {
    setUploading(true);
    const results = await Promise.allSettled(
      accepted.map((f) => documentsAPI.upload(f, taxYear))
    );
    const succeeded = results.filter((r) => r.status === "fulfilled").length;
    const failed = results.length - succeeded;
    if (succeeded) toast.success(`${succeeded} document(s) uploaded — AI is extracting data…`);
    if (failed) toast.error(`${failed} upload(s) failed`);
    setUploading(false);
    load();
  }, [taxYear]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "image/jpeg": [".jpg", ".jpeg"], "image/png": [".png"] },
    maxSize: 20 * 1024 * 1024,
  });

  const handleDelete = async (id: number) => {
    if (!window.confirm("Delete this document?")) return;
    await documentsAPI.delete(id);
    toast.success("Document deleted");
    setDocs((prev) => prev.filter((d) => d.id !== id));
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Documents</h1>
          <p className="page-subtitle">Upload your W-2s, 1099s, and other tax documents</p>
        </div>
        <div className="header-actions">
          <select
            className="year-select"
            value={taxYear}
            onChange={(e) => setTaxYear(Number(e.target.value))}
          >
            {[2024, 2023, 2022, 2021].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
          <button className="btn-secondary" onClick={handleRefresh} disabled={refreshing}>
            <RefreshCw size={15} className={refreshing ? "spinning" : ""} />
            Refresh
          </button>
        </div>
      </div>

      {/* Drop Zone */}
      <div {...getRootProps()} className={`dropzone ${isDragActive ? "active" : ""} ${uploading ? "uploading" : ""}`}>
        <input {...getInputProps()} />
        <Upload size={36} className="drop-icon" />
        <p className="drop-title">
          {uploading ? "Uploading…" : isDragActive ? "Drop files here!" : "Drag & drop your tax documents"}
        </p>
        <p className="drop-subtitle">Supports PDF, JPG, PNG — W-2, 1099, 1098, receipts</p>
        {!uploading && <button className="btn-primary" onClick={(e) => e.stopPropagation()}>Choose Files</button>}
      </div>

      {/* Document List */}
      {docs.length > 0 && (
        <div className="section">
          <h2>Uploaded Documents ({docs.length})</h2>
          <div className="docs-list">
            {docs.map((doc) => {
              const s = STATUS_MAP[doc.status] || STATUS_MAP.error;
              const isExpanded = expandedDoc === doc.id;
              const fields = doc.extracted_data?.tax_fields;

              return (
                <div key={doc.id} className="doc-card">
                  <div className="doc-header" onClick={() => setExpandedDoc(isExpanded ? null : doc.id)}>
                    <div className="doc-icon"><FileText size={20} /></div>
                    <div className="doc-info">
                      <p className="doc-name">{doc.filename}</p>
                      <p className="doc-meta">{doc.doc_type} · {doc.tax_year}</p>
                    </div>
                    <span className={`status-badge ${s.cls}`}>{s.icon} {s.label}</span>
                    <button
                      className="delete-btn"
                      onClick={(e) => { e.stopPropagation(); handleDelete(doc.id); }}
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>

                  {/* Extracted Fields */}
                  {isExpanded && doc.status === "done" && fields && (
                    <div className="doc-fields">
                      <p className="fields-title">Extracted Data</p>
                      <div className="fields-grid">
                        {Object.entries(fields).filter(([, v]) => v).map(([k, v]) => (
                          <div key={k} className="field-item">
                            <span className="field-key">{k.replace(/_/g, " ")}</span>
                            <span className="field-value">{String(v)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {isExpanded && doc.status === "processing" && (
                    <div className="doc-fields processing">
                      <Clock size={16} /> AI is extracting data from this document…
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {docs.length === 0 && !uploading && (
        <div className="empty-state">
          <FileText size={48} />
          <p>No documents yet. Upload your first tax document above.</p>
        </div>
      )}
    </div>
  );
}
