import React, { useState, useEffect } from "react";
import { taxAPI, paymentAPI } from "../services/api";
import toast from "react-hot-toast";
import { CreditCard, CheckCircle, DollarSign, FileCheck, Shield } from "lucide-react";

export default function PaymentPage() {
  const [returns, setReturns] = useState<any[]>([]);
  const [payments, setPayments] = useState<any[]>([]);
  const [processing, setProcessing] = useState(false);
  const [paid, setPaid] = useState(false);

  useEffect(() => {
    Promise.all([taxAPI.listReturns(), paymentAPI.history()]).then(([r, p]) => {
      setReturns(r.data);
      setPayments(p.data);
    });
  }, []);

  const approvedReturn = returns.find(
    (r) => r.status === "approved" || r.status === "paid"
  );
  const isAlreadyPaid = approvedReturn?.status === "paid";

  const handlePay = async () => {
    if (!approvedReturn) return;
    setProcessing(true);
    try {
      // In production: use Stripe.js to collect card and get payment_method_id
      // Here we simulate a successful payment flow
      const intent = await paymentAPI.createIntent(approvedReturn.id);
      // Normally you'd confirm with Stripe.js — here we call confirm directly
      await paymentAPI.confirm(approvedReturn.id, "pm_simulated");
      setPaid(true);
      toast.success("🎉 Payment successful! Your taxes have been filed.");
      const r = await taxAPI.listReturns();
      setReturns(r.data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Payment failed");
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Payment & Filing</h1>
          <p className="page-subtitle">Review and pay your tax balance</p>
        </div>
      </div>

      {!approvedReturn ? (
        <div className="empty-state">
          <FileCheck size={48} />
          <p>No approved tax return yet.</p>
          <p>Go to <strong>Tax Return</strong> to calculate and approve your return first.</p>
        </div>
      ) : (
        <div className="payment-layout">
          {/* Summary Card */}
          <div className="payment-summary">
            <div className="card">
              <h2><DollarSign size={18} /> Payment Summary</h2>
              <div className="summary-rows">
                <div className="summary-row">
                  <span>Tax Year</span>
                  <strong>{approvedReturn.tax_year}</strong>
                </div>
                <div className="summary-row">
                  <span>Filing Status</span>
                  <strong>{approvedReturn.filing_status.replace("_", " ")}</strong>
                </div>
                <div className="summary-row">
                  <span>Total Income</span>
                  <strong>${approvedReturn.total_income?.toLocaleString()}</strong>
                </div>
                <div className="summary-row">
                  <span>Total Deductions</span>
                  <strong>-${approvedReturn.total_deductions?.toLocaleString()}</strong>
                </div>
                <div className="summary-row total">
                  <span>Tax Owed</span>
                  <strong className="big-num">${approvedReturn.tax_owed?.toLocaleString()}</strong>
                </div>
                {approvedReturn.refund_amount > 0 && (
                  <div className="summary-row refund">
                    <span>Expected Refund</span>
                    <strong className="refund-amount">+${approvedReturn.refund_amount?.toLocaleString()}</strong>
                  </div>
                )}
              </div>
            </div>

            <div className="security-notice">
              <Shield size={16} />
              <p>Payments are secured by Stripe. Your card details never touch our servers.</p>
            </div>
          </div>

          {/* Payment Action */}
          <div className="payment-action">
            {(isAlreadyPaid || paid) ? (
              <div className="card success-card">
                <div className="success-icon"><CheckCircle size={56} /></div>
                <h2>Taxes Filed & Paid!</h2>
                <p>Your {approvedReturn.tax_year} federal tax return has been submitted and payment processed.</p>
                <div className="filed-details">
                  <p>Confirmation #: <strong>TAXAI-{approvedReturn.id}-{approvedReturn.tax_year}</strong></p>
                  <p>Amount Paid: <strong>${approvedReturn.tax_owed?.toLocaleString()}</strong></p>
                </div>
              </div>
            ) : approvedReturn.refund_amount > 0 ? (
              <div className="card refund-card">
                <div className="refund-icon"><CheckCircle size={56} /></div>
                <h2>You're Getting a Refund!</h2>
                <p>No payment needed. You'll receive <strong>${approvedReturn.refund_amount?.toLocaleString()}</strong> back from the IRS.</p>
                <button className="btn-success full-width" onClick={handlePay} disabled={processing}>
                  {processing ? "Filing…" : "Submit Return for Refund"}
                </button>
              </div>
            ) : (
              <div className="card pay-card">
                <h2><CreditCard size={18} /> Pay Your Balance</h2>
                <p className="pay-amount">${approvedReturn.tax_owed?.toLocaleString()}</p>
                <p className="pay-due">Due by April 15, {approvedReturn.tax_year + 1}</p>

                {/* In production this would be Stripe Elements */}
                <div className="stripe-placeholder">
                  <div className="mock-card-input">
                    <CreditCard size={16} />
                    <span>4242 4242 4242 4242</span>
                    <span className="mock-expiry">12/27</span>
                    <span className="mock-cvc">123</span>
                  </div>
                  <p className="stripe-note">
                    🔒 In production, replace with <code>&lt;CardElement&gt;</code> from @stripe/react-stripe-js
                  </p>
                </div>

                <button className="btn-pay full-width" onClick={handlePay} disabled={processing}>
                  {processing ? "Processing…" : `Pay $${approvedReturn.tax_owed?.toLocaleString()}`}
                </button>
              </div>
            )}

            {/* Payment History */}
            {payments.length > 0 && (
              <div className="card">
                <h2>Payment History</h2>
                {payments.map((p) => (
                  <div key={p.id} className="payment-row">
                    <div>
                      <p>Tax Return #{p.tax_return_id}</p>
                      <p className="payment-date">{new Date(p.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="payment-right">
                      <strong>${p.amount?.toLocaleString()}</strong>
                      <span className={`status-badge ${p.status === "succeeded" ? "success" : "warning"}`}>
                        {p.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
