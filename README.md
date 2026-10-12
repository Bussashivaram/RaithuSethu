# Raithu-Sethu — farmer-to-buyer marketplace (review-ready)

Full stack: **React 19 + Vite + Tailwind 4** (`front-end/`) + **FastAPI + Socket.IO + Supabase Postgres** (`backend/`).

## 1. Fresh Supabase setup (15 min, you need this — old DB keys are not accessible)

1. Go to [supabase.com](https://supabase.com) → New project → copy **Project URL**, **anon public key**, **service_role key** (Project Settings → API).
2. Dashboard → **SQL Editor** → paste + run `supabase/schema.sql` (creates all 11 tables, demo-friendly RLS off).
3. `cd backend` → copy `.env.example` to `.env`, fill in your three keys + a random `JWT_SECRET_KEY`.
4. Seed demo logins: `pip install -r requirements.txt && python scripts/seed_demo.py`

| Role | Email | Password |
|---|---|---|
| Farmer | farmer.demo@raithusethu.in | Farmer@123 |
| Buyer | buyer.demo@raithusethu.in | Buyer@123 |
| Admin | admin.demo@raithusethu.in | Admin@123 |

## 2. Run locally

```bash
# backend (http://localhost:8000, docs at /docs, health at /health)
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# frontend (http://localhost:5173) — new terminal
cd front-end
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

Vite proxies `/api`, `/uploads`, `/socket.io` to localhost:8000, so chat + images work locally with zero CORS setup.

## 3. Deploy (Render + Vercel)

**Backend → Render:** New → Web Service → point at repo, `rootDir: backend`, Docker (`render.yaml` at repo root already configures this, health check `/health`). Set env vars: `SUPABASE_URL`, `SUPABASE_KEY` (anon), `SUPABASE_SERVICE_ROLE_KEY`, `JWT_SECRET_KEY`, `FRONTEND_URL=https://<your-app>.vercel.app`. Note the `https://<render-name>.onrender.com` URL.

**Frontend → Vercel:** Import repo, `rootDirectory: front-end` (build `npm run build`, output `dist` per `vercel.json`). Set env `VITE_API_URL=https://<render-name>.onrender.com` (no trailing slash). Redeploy after setting env.

**Uploads note:** crop images/voice notes live on the backend's local disk (`backend/uploads/`). They survive the review demo; for long-term prod move to Supabase Storage (endpoint shape stays `/uploads/...` via `resolveMediaUrl`).

## 4. Review demo flow (5 min)

1. Open `/buyer/marketplace` (public, no login) → search/filter a crop → open details.
2. Login as **buyer** → Request crop → post a Requirement → open Chat.
3. Login as **farmer** (second browser/incognito) → accept request under Requests → respond to the Requirement → create a Flash Sale.
4. Buyer → Book crop → farmer marks booking Complete under Bookings.
5. **Admin** → `/admin` dashboard + Farmers/Buyers verify + Analytics. Notifications bell + realtime chat are the wow-factor closers.

Architecture one-liner for examiners: React SPA → REST (`/api/*`, JWT `Bearer rs_token`) + Socket.IO (`/socket.io`, same JWT) → FastAPI → Supabase Postgres; APScheduler hourly job expires crops/sales and auto-creates flash sales for crops expiring in 24h.
