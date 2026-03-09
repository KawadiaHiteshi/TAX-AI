import React, { useState, useEffect, useRef } from "react";
import { taxAPI } from "../services/api";
import toast from "react-hot-toast";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { Calculator, Send, CheckCircle, Bot, User } from "lucide-react";

const FILING_STATUSES = [
  { value: "single", label: "Single" },
  { value: "married_joint", label: "Married Filing Jointly" },
  { value: "married_separate", label: "Married Filing Separately" },
  { value: "head_of_household", label: "Head of Household" },
];

const COLORS = ["#6366f1", "#22d3ee", "#f59e0b", "#10b981"];

export default function TaxReturnPage() {
  const [form, setForm] = useState({
    tax_year: new Date().getFullYear() - 1,
    filing_status: "single",
    additional_income: 0,
    itemized_deductions: 0,
  });
  const [result, setResult] = useState<any>(null);
  const [returns, setReturns] = useState<any[]>([]);
  const [calculating, setCalculating] = useState(false);
  const [approving, setApproving] = useState(false);
  const [chat, setChat] = useState<{ role: "user" | "ai"; text: string }[]>([]);
  const [chatMsg, setChatMsg] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    taxAPI.listReturns().then((r) => setReturns(r.data));
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  const calculate = async () => {
    setCalculating(true);
    try {
      const res = await taxAPI.calculate(form);
      setResult(res.data);
      toast.success("Tax calculation complete!");
      taxAPI.listReturns().then((r) => setReturns(r.data));
    } catch {
      toast.error("Calculation failed. Check your documents are processed.");
    } finally {
      setCalculating(false);
    }
  };

  const approve = async () => {
    if (!result?.tax_return_id) return;
    setApproving(true);
    try {
      await taxAPI.approve(result.tax_return_id);
      toast.success("Return approved! Proceed to payment.");
      taxAPI.listReturns().then((r) => setReturns(r.data));
    } finally {
      setApproving(false);
    }
  };

  const sendChat = async () => {
    if (!chatMsg.trim()) return;
    const msg = chatMsg.trim();
    setChatMsg("");
    setChat((c) => [...c, { role: "user", text: msg }]);
    setChatLoading(true);
    try {
      const res = await taxAPI.chat(msg, result?.tax_return_id);
      setChat((c) => [...c, { role: "ai", text: res.data.reply }]);
    } catch {
      setChat((c) => [...c, { role: "ai", text: "Sorry, I couldn't reach the AI. Try again." }]);
    } finally {
      setChatLoading(false);
    }
  };

  const calc = result?.calculation;
  const pieData = calc ? [
    { name: "Tax Owed", value: calc.tax_owed },
    { name: "Withheld", value: calc.federal_withheld },
    { name: "Deductions", value: calc.deduction_amount },
    { name: "Remaining Income", value: calc.taxable_income - calc.tax_owed },
  ] : [];

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Tax Return</h1>
          <p className="page-subtitle">Calculate your taxes and get AI-powered insights</p>
        </div>
      </div>

      <div className="tax-layout">
        {/* Left: Form + Results */}
        <div className="tax-main">
          {/* Calculator Form */}
          <div className="card">
            <h2><Calculator size={18} /> Calculate My Taxes</h2>
            <div className="form-grid">
              <div className="form-field">
                <label>Tax Year</label>
                <select value={form.tax_year} onChange={(e) => setForm({ ...form, tax_year: Number(e.target.value) })}>
                  {[2024, 2023, 2022].map((y) => <option key={y} value={y}>{y}</option>)}
                </select>
              </div>
              <div className="form-field">
                <label>Filing Status</label>
                <select value={form.filing_status} onChange={(e) => setForm({ ...form, filing_status: e.target.value })}>
                  {FILING_STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
                </select>
              </div>
              <div className="form-field">
                <label>Additional Income ($)</label>
                <input type="number" value={form.additional_income} min={0}
                  onChange={(e) => setForm({ ...form, additional_income: Number(e.target.value) })} />
              </div>
              <div className="form-field">
                <label>Itemized Deductions ($)</label>
                <input type="number" value={form.itemized_deductions} min={0}
                  onChange={(e) => setForm({ ...form, itemized_deductions: Number(e.target.value) })} />
              </div>
            </div>
            <button className="btn-primary full-width" onClick={calculate} disabled={calculating}>
              {calculating ? "Calculating…" : "Calculate My Taxes"}
            </button>
          </div>

          {/* Results */}
          {calc && (
            <div className="card results-card">
              <div className="results-header">
                <h2>Your 2024 Tax Summary</h2>
                <span className={`amount-badge ${calc.refund > 0 ? "refund" : "owed"}`}>
                  {calc.refund > 0
                    ? `Refund: $${calc.refund.toLocaleString()}`
                    : `Owed: $${calc.amount_due.toLocaleString()}`}
                </span>
              </div>

              <div className="results-grid">
                <div className="result-item">
                  <span>Gross Income</span><strong>${calc.gross_income.toLocaleString()}</strong>
                </div>
                <div className="result-item">
                  <span>{calc.deduction_type === "standard" ? "Standard" : "Itemized"} Deduction</span>
                  <strong>-${calc.deduction_amount.toLocaleString()}</strong>
                </div>
                <div className="result-item">
                  <span>Taxable Income</span><strong>${calc.taxable_income.toLocaleString()}</strong>
                </div>
                <div className="result-item highlight">
                  <span>Tax Owed</span><strong>${calc.tax_owed.toLocaleString()}</strong>
                </div>
                <div className="result-item">
                  <span>Already Withheld</span><strong>-${calc.federal_withheld.toLocaleString()}</strong>
                </div>
                <div className="result-item highlight">
                  <span>Effective Rate</span><strong>{calc.effective_rate}%</strong>
                </div>
              </div>

              {/* Bracket Breakdown */}
              <div className="brackets">
                <h3>Tax Bracket Breakdown</h3>
                {calc.brackets.map((b: any, i: number) => (
                  <div key={i} className="bracket-row">
                    <span className="bracket-rate">{b.rate}</span>
                    <span className="bracket-range">{b.income_range}</span>
                    <span className="bracket-amount">${b.amount.toLocaleString()}</span>
                  </div>
                ))}
              </div>

              {/* Pie Chart */}
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={3} dataKey="value">
                      {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="chart-legend">
                  {pieData.map((d, i) => (
                    <div key={i} className="legend-item">
                      <span className="legend-dot" style={{ background: COLORS[i] }} />
                      <span>{d.name}</span>
                    </div>
                  ))}
                </div>
              </div>

              {result?.ai_summary && (
                <div className="ai-summary-box">
                  <Bot size={16} /><p>{result.ai_summary}</p>
                </div>
              )}

              <button className="btn-success full-width" onClick={approve} disabled={approving}>
                <CheckCircle size={16} />
                {approving ? "Approving…" : "Approve & Proceed to Payment"}
              </button>
            </div>
          )}
        </div>

        {/* Right: AI Chat */}
        <div className="chat-panel">
          <div className="chat-header">
            <Bot size={18} />
            <h2>AI Tax Assistant</h2>
          </div>
          <div className="chat-messages">
            {chat.length === 0 && (
              <div className="chat-empty">
                <Bot size={32} />
                <p>Ask me anything about your taxes!</p>
                <div className="chat-suggestions">
                  {["What deductions can I claim?", "Am I in a high tax bracket?", "What's the standard deduction?"].map((q) => (
                    <button key={q} className="suggestion-chip" onClick={() => setChatMsg(q)}>{q}</button>
                  ))}
                </div>
              </div>
            )}
            {chat.map((m, i) => (
              <div key={i} className={`chat-bubble ${m.role}`}>
                <div className="bubble-icon">
                  {m.role === "ai" ? <Bot size={14} /> : <User size={14} />}
                </div>
                <p>{m.text}</p>
              </div>
            ))}
            {chatLoading && (
              <div className="chat-bubble ai">
                <div className="bubble-icon"><Bot size={14} /></div>
                <p className="typing">···</p>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          <div className="chat-input">
            <input
              value={chatMsg}
              onChange={(e) => setChatMsg(e.target.value)}
              placeholder="Ask about your taxes…"
              onKeyDown={(e) => e.key === "Enter" && sendChat()}
            />
            <button onClick={sendChat} disabled={chatLoading || !chatMsg.trim()}>
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
