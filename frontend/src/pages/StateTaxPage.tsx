import React, { useState, useEffect } from "react";
import { stateTaxAPI } from "../services/api";
import toast from "react-hot-toast";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import { MapPin, Calculator, TrendingDown, TrendingUp, Info } from "lucide-react";

const FILING_STATUSES = [
  { value: "single", label: "Single" },
  { value: "married_joint", label: "Married Filing Jointly" },
  { value: "married_separate", label: "Married Filing Separately" },
  { value: "head_of_household", label: "Head of Household" },
];

const PIE_COLORS = ["#6366f1", "#22d3ee", "#10b981"];

export default function StateTaxPage() {
  const [states, setStates] = useState<any[]>([]);
  const [comparison, setComparison] = useState<any[]>([]);
  const [result, setResult] = useState<any>(null);
  const [tab, setTab] = useState<"calculator" | "compare" | "combined">("calculator");
  const [loading, setLoading] = useState(false);
  const [compLoading, setCompLoading] = useState(false);

  const [form, setForm] = useState({
    state_code: "CA",
    income: 100000,
    filing_status: "single",
    itemized_deductions: 0,
    tax_year: new Date().getFullYear() - 1,
    additional_income: 0,
  });

  useEffect(() => {
    stateTaxAPI.listStates().then((r) => setStates(r.data));
  }, []);

  const calculate = async () => {
    setLoading(true);
    try {
      const res = await stateTaxAPI.calculate({
        state_code: form.state_code,
        income: form.income,
        filing_status: form.filing_status,
        itemized_deductions: form.itemized_deductions,
      });
      setResult(res.data);
    } catch {
      toast.error("Calculation failed");
    } finally {
      setLoading(false);
    }
  };

  const calculateCombined = async () => {
    setLoading(true);
    try {
      const res = await stateTaxAPI.combined({
        state_code: form.state_code,
        tax_year: form.tax_year,
        filing_status: form.filing_status,
        additional_income: form.additional_income,
        itemized_deductions: form.itemized_deductions,
      });
      setResult(res.data);
    } catch {
      toast.error("Combined calculation failed");
    } finally {
      setLoading(false);
    }
  };

  const loadComparison = async () => {
    setCompLoading(true);
    try {
      const res = await stateTaxAPI.compare(form.income, form.filing_status);
      setComparison(res.data);
    } catch {
      toast.error("Comparison failed");
    } finally {
      setCompLoading(false);
    }
  };

  useEffect(() => {
    if (tab === "compare") loadComparison();
  }, [tab]);

  // Top 10 highest / lowest for bar chart
  const top10High = [...comparison].sort((a, b) => b.effective_rate - a.effective_rate).slice(0, 10);
  const top10Low  = [...comparison].slice(0, 10); // already sorted low→high

  const combinedPieData = result?.combined ? [
    { name: "Federal Tax",    value: result.combined.federal_tax },
    { name: "State Tax",      value: result.combined.state_tax },
    { name: "Net Take-Home",  value: result.income - result.combined.total_tax },
  ] : [];

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>State Tax Calculator</h1>
          <p className="page-subtitle">All 50 states + DC — 2024 tax rates</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="state-tabs">
        {[
          { key: "calculator", label: "State Calculator" },
          { key: "combined",   label: "Federal + State" },
          { key: "compare",    label: "Compare All States" },
        ].map((t) => (
          <button
            key={t.key}
            className={`state-tab ${tab === t.key ? "active" : ""}`}
            onClick={() => setTab(t.key as any)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ── Tab: State Calculator ─────────────────────────────── */}
      {tab === "calculator" && (
        <div className="state-layout">
          <div className="state-form card">
            <h2><Calculator size={16} /> State Tax Calculator</h2>
            <div className="form-field">
              <label>State</label>
              <select value={form.state_code} onChange={(e) => setForm({ ...form, state_code: e.target.value })}>
                {states.map((s) => (
                  <option key={s.code} value={s.code}>
                    {s.name} {!s.has_income_tax ? "(No Income Tax)" : `— top ${s.top_rate?.toFixed(2)}%`}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label>Annual Income ($)</label>
              <input type="number" value={form.income} min={0}
                onChange={(e) => setForm({ ...form, income: Number(e.target.value) })} />
            </div>
            <div className="form-field">
              <label>Filing Status</label>
              <select value={form.filing_status} onChange={(e) => setForm({ ...form, filing_status: e.target.value })}>
                {FILING_STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>
            <div className="form-field">
              <label>Itemized Deductions ($)</label>
              <input type="number" value={form.itemized_deductions} min={0}
                onChange={(e) => setForm({ ...form, itemized_deductions: Number(e.target.value) })} />
            </div>
            <button className="btn-primary full-width" onClick={calculate} disabled={loading}>
              {loading ? "Calculating…" : "Calculate State Tax"}
            </button>
          </div>

          {/* Results */}
          {result && !result.combined && (
            <div className="state-result">
              {!result.has_income_tax ? (
                <div className="card no-tax-card">
                  <div className="no-tax-icon">🎉</div>
                  <h2>{result.state} has NO State Income Tax!</h2>
                  <p>{result.notes || "You owe $0 in state income taxes."}</p>
                </div>
              ) : (
                <div className="card">
                  <div className="state-result-header">
                    <div>
                      <h2>{result.state} Tax Result</h2>
                      <p className="page-subtitle">Filing as {form.filing_status.replace("_", " ")}</p>
                    </div>
                    <div className="big-rate">{result.effective_rate}%<span>effective rate</span></div>
                  </div>

                  <div className="results-grid">
                    <div className="result-item">
                      <span>Gross Income</span><strong>${result.gross_income?.toLocaleString()}</strong>
                    </div>
                    <div className="result-item">
                      <span>Deductions</span><strong>-${result.deduction_amount?.toLocaleString()}</strong>
                    </div>
                    <div className="result-item">
                      <span>Taxable Income</span><strong>${result.taxable_income?.toLocaleString()}</strong>
                    </div>
                    <div className="result-item highlight">
                      <span>State Tax Owed</span><strong>${result.tax_owed?.toLocaleString()}</strong>
                    </div>
                  </div>

                  {/* Bracket Breakdown */}
                  {result.brackets?.length > 0 && (
                    <div className="brackets">
                      <h3>Tax Bracket Breakdown</h3>
                      {result.brackets.map((b: any, i: number) => (
                        <div key={i} className="bracket-row">
                          <span className="bracket-rate">{b.rate}</span>
                          <span className="bracket-range">{b.income_range}</span>
                          <span className="bracket-amount">${b.amount.toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {result.notes && (
                    <div className="state-note">
                      <Info size={14} />{result.notes}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Tab: Federal + State Combined ────────────────────── */}
      {tab === "combined" && (
        <div className="state-layout">
          <div className="state-form card">
            <h2><Calculator size={16} /> Federal + State Combined</h2>
            <div className="form-field">
              <label>State</label>
              <select value={form.state_code} onChange={(e) => setForm({ ...form, state_code: e.target.value })}>
                {states.map((s) => (
                  <option key={s.code} value={s.code}>{s.name}</option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label>Tax Year</label>
              <select value={form.tax_year} onChange={(e) => setForm({ ...form, tax_year: Number(e.target.value) })}>
                {[2024, 2023, 2022].map((y) => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>
            <div className="form-field">
              <label>Additional Income ($) <small>on top of uploaded docs</small></label>
              <input type="number" value={form.additional_income} min={0}
                onChange={(e) => setForm({ ...form, additional_income: Number(e.target.value) })} />
            </div>
            <div className="form-field">
              <label>Filing Status</label>
              <select value={form.filing_status} onChange={(e) => setForm({ ...form, filing_status: e.target.value })}>
                {FILING_STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>
            <button className="btn-primary full-width" onClick={calculateCombined} disabled={loading}>
              {loading ? "Calculating…" : "Calculate Combined Tax"}
            </button>
          </div>

          {result?.combined && (
            <div className="combined-result">
              {/* Summary Cards */}
              <div className="combined-cards">
                <div className="comb-card fed">
                  <p className="comb-label">Federal Tax</p>
                  <p className="comb-val">${result.combined.federal_tax.toLocaleString()}</p>
                  <p className="comb-sub">{result.federal.effective_rate}% effective</p>
                </div>
                <div className="comb-card state">
                  <p className="comb-label">{result.state.state} State Tax</p>
                  <p className="comb-val">${result.combined.state_tax.toLocaleString()}</p>
                  <p className="comb-sub">{result.state.effective_rate}% effective</p>
                </div>
                <div className="comb-card total">
                  <p className="comb-label">Total Tax Burden</p>
                  <p className="comb-val">${result.combined.total_tax.toLocaleString()}</p>
                  <p className="comb-sub">{result.combined.total_effective_rate}% combined rate</p>
                </div>
              </div>

              {/* Pie Chart */}
              <div className="card">
                <h2>Where Your Money Goes</h2>
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie data={combinedPieData} cx="50%" cy="50%" innerRadius={60} outerRadius={95}
                      paddingAngle={3} dataKey="value">
                      {combinedPieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                    </Pie>
                    <Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Federal breakdown */}
              <div className="card">
                <h2>Federal Breakdown</h2>
                <div className="results-grid">
                  {[
                    ["Gross Income",      `$${result.federal.gross_income?.toLocaleString()}`],
                    ["Deduction",         `-$${result.federal.deduction_amount?.toLocaleString()}`],
                    ["Taxable Income",    `$${result.federal.taxable_income?.toLocaleString()}`],
                    ["Tax Owed",          `$${result.federal.tax_owed?.toLocaleString()}`],
                    ["Withheld",          `-$${result.federal.federal_withheld?.toLocaleString()}`],
                    ["Refund / Due",      result.federal.refund > 0 ? `+$${result.federal.refund?.toLocaleString()}` : `-$${result.federal.amount_due?.toLocaleString()}`],
                  ].map(([label, val]) => (
                    <div key={label} className="result-item">
                      <span>{label}</span><strong>{val}</strong>
                    </div>
                  ))}
                </div>
              </div>

              {/* State brackets */}
              {result.state.has_income_tax && result.state.brackets?.length > 0 && (
                <div className="card">
                  <h2>{result.state.state} State Brackets</h2>
                  <div className="brackets">
                    {result.state.brackets.map((b: any, i: number) => (
                      <div key={i} className="bracket-row">
                        <span className="bracket-rate">{b.rate}</span>
                        <span className="bracket-range">{b.income_range}</span>
                        <span className="bracket-amount">${b.amount.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Tab: Compare All States ─────────────────────────── */}
      {tab === "compare" && (
        <div>
          <div className="compare-controls card">
            <div className="compare-form">
              <div className="form-field">
                <label>Income to Compare ($)</label>
                <input type="number" value={form.income} min={0}
                  onChange={(e) => setForm({ ...form, income: Number(e.target.value) })} />
              </div>
              <div className="form-field">
                <label>Filing Status</label>
                <select value={form.filing_status} onChange={(e) => setForm({ ...form, filing_status: e.target.value })}>
                  {FILING_STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
                </select>
              </div>
              <button className="btn-primary" onClick={loadComparison} disabled={compLoading}>
                {compLoading ? "Loading…" : "Compare"}
              </button>
            </div>
          </div>

          {comparison.length > 0 && (
            <>
              {/* Bar charts */}
              <div className="charts-row">
                <div className="card">
                  <h2><TrendingDown size={16} /> 10 Lowest-Tax States</h2>
                  <ResponsiveContainer width="100%" height={260}>
                    <BarChart data={top10Low} layout="vertical" margin={{ left: 80 }}>
                      <XAxis type="number" tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11 }} />
                      <YAxis type="category" dataKey="state" tick={{ fontSize: 11 }} width={80} />
                      <Tooltip formatter={(v: any) => `${Number(v).toFixed(2)}%`} />
                      <Bar dataKey="effective_rate" fill="#10b981" radius={[0,4,4,0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="card">
                  <h2><TrendingUp size={16} /> 10 Highest-Tax States</h2>
                  <ResponsiveContainer width="100%" height={260}>
                    <BarChart data={top10High} layout="vertical" margin={{ left: 80 }}>
                      <XAxis type="number" tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11 }} />
                      <YAxis type="category" dataKey="state" tick={{ fontSize: 11 }} width={80} />
                      <Tooltip formatter={(v: any) => `${Number(v).toFixed(2)}%`} />
                      <Bar dataKey="effective_rate" fill="#ef4444" radius={[0,4,4,0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Full table */}
              <div className="card">
                <h2><MapPin size={16} /> All States — Tax on ${form.income.toLocaleString()}</h2>
                <div className="compare-table-wrap">
                  <table className="compare-table">
                    <thead>
                      <tr>
                        <th>Rank</th>
                        <th>State</th>
                        <th>Effective Rate</th>
                        <th>Tax Owed</th>
                        <th>Take-Home</th>
                      </tr>
                    </thead>
                    <tbody>
                      {comparison.map((s, i) => (
                        <tr key={s.state_code} className={!s.has_income_tax ? "no-tax-row" : ""}>
                          <td className="rank">#{i + 1}</td>
                          <td className="state-name">
                            <strong>{s.state}</strong>
                            <span className="state-code">{s.state_code}</span>
                          </td>
                          <td>
                            {s.has_income_tax ? (
                              <span className="rate-pill">{s.effective_rate}%</span>
                            ) : (
                              <span className="no-tax-pill">No Tax</span>
                            )}
                          </td>
                          <td className="tax-col">${s.tax_owed.toLocaleString()}</td>
                          <td className="takehome-col">
                            ${(form.income - s.tax_owed).toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
