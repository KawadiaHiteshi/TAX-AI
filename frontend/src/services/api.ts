import axios from "axios";

const api = axios.create({ baseURL: "/api" });

// Attach token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("taxai_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Auth ────────────────────────────────────────────────────────
export const authAPI = {
  register: (data: { email: string; full_name: string; password: string }) =>
    api.post("/auth/register", data),
  login: (email: string, password: string) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    return api.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
  me: () => api.get("/auth/me"),
};

// ── Documents ───────────────────────────────────────────────────
export const documentsAPI = {
  upload: (file: File, taxYear: number) => {
    const form = new FormData();
    form.append("file", file);
    return api.post(`/documents/upload?tax_year=${taxYear}`, form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  list: () => api.get("/documents/"),
  get: (id: number) => api.get(`/documents/${id}`),
  delete: (id: number) => api.delete(`/documents/${id}`),
};

// ── Tax ─────────────────────────────────────────────────────────
export const taxAPI = {
  calculate: (data: {
    tax_year: number;
    filing_status: string;
    additional_income?: number;
    itemized_deductions?: number;
  }) => api.post("/tax/calculate", data),
  listReturns: () => api.get("/tax/returns"),
  approve: (returnId: number) => api.post(`/tax/approve/${returnId}`),
  chat: (message: string, taxReturnId?: number) =>
    api.post("/tax/chat", { message, tax_return_id: taxReturnId }),
};

// ── State Tax ────────────────────────────────────────────────────
export const stateTaxAPI = {
  listStates: () => api.get("/state-tax/states"),
  calculate: (data: { state_code: string; income: number; filing_status?: string; itemized_deductions?: number }) =>
    api.post("/state-tax/calculate", data),
  combined: (data: { state_code: string; tax_year?: number; filing_status?: string; additional_income?: number; itemized_deductions?: number }) =>
    api.post("/state-tax/combined", data),
  compare: (income: number, filing_status: string) =>
    api.get(`/state-tax/compare?income=${income}&filing_status=${filing_status}`),
};

// ── Payment ─────────────────────────────────────────────────────
export const paymentAPI = {
  createIntent: (taxReturnId: number) =>
    api.post(`/payment/create-intent?tax_return_id=${taxReturnId}`),
  confirm: (taxReturnId: number, paymentMethodId: string) =>
    api.post("/payment/confirm", {
      tax_return_id: taxReturnId,
      payment_method_id: paymentMethodId,
    }),
  history: () => api.get("/payment/history"),
};

export default api;
