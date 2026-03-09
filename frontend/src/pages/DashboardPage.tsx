import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { documentsAPI, taxAPI } from "../services/api";
import { FileText, Calculator, CreditCard, TrendingUp, ChevronRight, CheckCircle, Clock, AlertCircle } from "lucide-react";

const STATUS_ICON: Record<string, React.ReactNode> = {
  filed: <CheckCircle size={14} className="status-icon success" />,
  paid: <CheckCircle size={14} className="status-icon success" />,
  review: <Clock size={14} className="status-icon warning" />,
  draft: <AlertCircle size={14} className="status-icon neutral" />,
  approved: <CheckCircle size={14} className="status-icon info" />,
};

export default function DashboardPage() {
  const { user } = useAuth();
  const [docs, setDocs] = useState<any[]>([]);
  const [returns, setReturns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([documentsAPI.list(), taxAPI.listReturns()])
      .then(([d, r]) => { setDocs(d.data); setReturns(r.data); })
      .finally(() => setLoading(false));
  }, []);

  const latestReturn = returns[0];

  const steps = [
    { label: "Upload Documents", done: docs.length > 0, to: "/documents", icon: FileText },
    { label: "Calculate Taxes", done: returns.length > 0, to: "/tax-return", icon: Calculator },
    { label: "Review & Approve", done: latestReturn?.status === "approved" || latestReturn?.status === "paid", to: "/tax-return", icon: CheckCircle },
    { label: "Pay & File", done: latestReturn?.status === "paid", to: "/payment", icon: CreditCard },
  ];

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Welcome back, {user?.full_name?.split(" ")[0]} 👋</h1>
          <p className="page-subtitle">Here's your tax filing progress for 2024</p>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon blue"><FileText size={22} /></div>
          <div>
            <p className="stat-value">{docs.length}</p>
            <p className="stat-label">Documents Uploaded</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon green"><TrendingUp size={22} /></div>
          <div>
            <p className="stat-value">${latestReturn?.total_income?.toLocaleString() ?? "—"}</p>
            <p className="stat-label">Total Income</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon orange"><Calculator size={22} /></div>
          <div>
            <p className="stat-value">
              {latestReturn ? `$${latestReturn.tax_owed?.toLocaleString()}` : "—"}
            </p>
            <p className="stat-label">Tax Owed</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon purple"><CreditCard size={22} /></div>
          <div>
            <p className="stat-value">
              {latestReturn?.refund_amount > 0
                ? `$${latestReturn.refund_amount?.toLocaleString()}`
                : "—"}
            </p>
            <p className="stat-label">Expected Refund</p>
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="section">
        <h2>Filing Progress</h2>
        <div className="steps-list">
          {steps.map((step, i) => (
            <Link key={i} to={step.to} className={`step-item ${step.done ? "done" : ""}`}>
              <div className={`step-number ${step.done ? "done" : ""}`}>
                {step.done ? <CheckCircle size={16} /> : i + 1}
              </div>
              <div className="step-info">
                <step.icon size={15} />
                <span>{step.label}</span>
              </div>
              <ChevronRight size={16} className="step-arrow" />
            </Link>
          ))}
        </div>
      </div>

      {/* Latest Return */}
      {latestReturn && (
        <div className="section">
          <h2>Latest Tax Return</h2>
          <div className="return-card">
            <div className="return-header">
              <span className="tax-year">{latestReturn.tax_year} Return</span>
              <span className={`status-badge ${latestReturn.status}`}>
                {STATUS_ICON[latestReturn.status]}
                {latestReturn.status}
              </span>
            </div>
            <p className="ai-summary">{latestReturn.ai_summary}</p>
            <Link to="/tax-return" className="btn-link">View Details <ChevronRight size={14} /></Link>
          </div>
        </div>
      )}
    </div>
  );
}
