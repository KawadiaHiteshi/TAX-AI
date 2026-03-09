# 🤖 TaxAI — AI-Powered Tax Filing App

A full-stack web application that uses AI and Google Document AI to automatically extract data from tax documents, calculate taxes, and process payments.

---

## 🏗️ Architecture

```
taxai/
├── backend/                   # FastAPI (Python)
│   ├── main.py                # App entry point + CORS
│   ├── models/
│   │   ├── models.py          # SQLAlchemy DB models
│   │   └── database.py        # Async DB connection
│   ├── routers/
│   │   ├── auth.py            # JWT login/register
│   │   ├── documents.py       # Upload + Google Document AI
│   │   ├── tax.py             # Tax calculation + AI chat
│   │   └── payment.py         # Stripe payment processing
│   ├── services/
│   │   ├── document_ai.py     # Google Document AI integration
│   │   ├── tax_engine.py      # 2024 US tax bracket calculator
│   │   └── ai_assistant.py    # OpenAI GPT-4o tax chat
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/                  # React + TypeScript
    └── src/
        ├── pages/
        │   ├── LoginPage.tsx
        │   ├── DashboardPage.tsx
        │   ├── DocumentsPage.tsx
        │   ├── TaxReturnPage.tsx
        │   └── PaymentPage.tsx
        ├── services/api.ts    # Axios API layer
        └── context/AuthContext.tsx
```

---

## 🚀 Quick Start

### 1. Clone & Setup Backend

```bash
cd taxai/backend
chmod +x start.sh
./start.sh
```

### 2. Configure Environment Variables

Edit `backend/.env` with your API keys:

```env
GOOGLE_PROJECT_ID=your-gcp-project
GOOGLE_LOCATION=us
GOOGLE_PROCESSOR_ID=your-processor-id
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json

SECRET_KEY=your-random-secret-key
OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_test_...
```

### 3. Start Frontend

```bash
cd taxai/frontend
npm install
npm start
```

App runs at: **http://localhost:3000**
API docs at: **http://localhost:8000/docs**

---

## ☁️ Setting Up Google Document AI

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable the **Document AI API**
4. Go to Document AI → Create Processor
   - Choose **"Form Parser"** for general tax docs
   - Or **"W-2 Parser"** / **"1099 Parser"** for specific forms
5. Copy the **Processor ID** to your `.env`
6. Create a Service Account with Document AI permissions
7. Download the JSON key → save as `backend/service-account.json`

---

## 💳 Setting Up Stripe

1. Create account at [stripe.com](https://stripe.com)
2. Get test API keys from Dashboard → Developers
3. Add to `.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```
4. In production: replace the mock card input in `PaymentPage.tsx` with `<CardElement>` from `@stripe/react-stripe-js`

---

## 📋 Features

| Feature | Status | Details |
|---------|--------|---------|
| JWT Auth | ✅ | Register/login with bcrypt passwords |
| Document Upload | ✅ | PDF, JPG, PNG up to 20MB |
| Google Document AI OCR | ✅ | Auto-extracts W-2, 1099, 1098 fields |
| Tax Calculation | ✅ | 2024 US federal brackets, all filing statuses |
| AI Tax Chat | ✅ | GPT-4o with your tax context |
| Stripe Payments | ✅ | Create payment intent + confirm |
| Tax Return History | ✅ | View all past returns |
| Dark Mode UI | ✅ | Polished dark theme |
| Background Processing | ✅ | Document AI runs async |

---

## 🔐 Security Notes

- Passwords hashed with bcrypt
- JWT tokens expire after 60 minutes  
- Only last 4 digits of SSN stored
- All uploads stored server-side (add S3 for production)
- Never log or expose full tax data in responses

---

## 🛣️ Production Roadmap

- [ ] Replace SQLite with PostgreSQL
- [ ] Add AWS S3 for document storage
- [ ] Integrate Stripe Webhooks for reliable payment confirmation
- [ ] Add IRS MeF e-filing integration (requires IRS authorization)
- [ ] Add state tax calculations
- [ ] Add email notifications
- [ ] Add 2FA / MFA
- [ ] SOC 2 compliance audit

---

## 📚 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT token |
| POST | `/api/documents/upload` | Upload tax document |
| GET | `/api/documents/` | List user documents |
| POST | `/api/tax/calculate` | Calculate taxes from documents |
| POST | `/api/tax/chat` | Chat with AI assistant |
| POST | `/api/tax/approve/{id}` | Approve tax return |
| POST | `/api/payment/create-intent` | Create Stripe payment intent |
| POST | `/api/payment/confirm` | Confirm payment |
