-- Raithu-Sethu Supabase schema — run once in Supabase Dashboard → SQL Editor.
-- Fresh project setup (no Supabase access to old DB, per review prep).
-- RLS is disabled for the college demo so the FastAPI anon key can read/write;
-- enable + tighten policies before any production use.

-- ── users ──────────────────────────────────────────────
create table if not exists users (
  id text primary key,
  name text not null,
  email text unique not null,
  password_hash text not null,
  phone text not null,
  location text,
  farm_size float,
  company_name text,
  role text not null check (role in ('farmer','buyer','admin')),
  is_verified boolean not null default false,
  created_at timestamptz not null default now()
);

-- ── crops ──────────────────────────────────────────────
create table if not exists crops (
  id text primary key,
  farmer_id text not null references users(id) on delete cascade,
  name text not null,
  category text not null,
  quantity float not null,
  unit text not null,
  price_per_unit float not null,
  description text,
  location text not null,
  harvest_date timestamptz,
  expiry_date timestamptz,
  status text not null default 'active',
  images jsonb not null default '[]',
  created_at timestamptz not null default now()
);

-- ── purchase_requests (buyer → farmer) ──────────────────
create table if not exists purchase_requests (
  id text primary key,
  crop_id text not null references crops(id) on delete cascade,
  crop_name text,
  buyer_id text not null references users(id) on delete cascade,
  farmer_id text not null references users(id) on delete cascade,
  quantity float not null,
  message text,
  proposed_price float,
  status text not null default 'pending',
  created_at timestamptz not null default now()
);

-- ── buyer_requirements ─────────────────────────────────
create table if not exists buyer_requirements (
  id text primary key,
  buyer_id text not null references users(id) on delete cascade,
  crop_name text not null,
  category text not null,
  quantity float not null,
  unit text not null,
  max_price float not null,
  location text,
  required_by timestamptz,
  description text,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

-- ── requirement_responses ──────────────────────────────
create table if not exists requirement_responses (
  id text primary key,
  requirement_id text not null references buyer_requirements(id) on delete cascade,
  farmer_id text not null references users(id) on delete cascade,
  crop_id text not null references crops(id) on delete cascade,
  offered_price float not null,
  message text,
  created_at timestamptz not null default now()
);

-- ── requirement_matches (auto-matcher log) ─────────────
create table if not exists requirement_matches (
  id text primary key default gen_random_uuid()::text,
  requirement_id text not null references buyer_requirements(id) on delete cascade,
  crop_id text not null references crops(id) on delete cascade,
  farmer_id text not null references users(id) on delete cascade,
  created_at timestamptz not null default now(),
  unique (requirement_id, crop_id)
);

-- ── bookings ───────────────────────────────────────────
create table if not exists bookings (
  id text primary key,
  crop_id text not null references crops(id) on delete cascade,
  buyer_id text not null references users(id) on delete cascade,
  farmer_id text not null references users(id) on delete cascade,
  quantity float not null,
  total_price float not null,
  delivery_address text not null,
  delivery_date timestamptz not null,
  payment_method text not null default 'cod',
  status text not null default 'confirmed',
  created_at timestamptz not null default now()
);

-- ── conversations / messages ───────────────────────────
create table if not exists conversations (
  id text primary key,
  participant_one_id text not null references users(id) on delete cascade,
  participant_two_id text not null references users(id) on delete cascade,
  participant_one_name text,
  participant_two_name text,
  last_message text,
  updated_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

create table if not exists messages (
  id text primary key,
  conversation_id text not null references conversations(id) on delete cascade,
  sender_id text not null references users(id) on delete cascade,
  content text not null,
  is_read boolean not null default false,
  created_at timestamptz not null default now()
);

-- ── notifications ──────────────────────────────────────
create table if not exists notifications (
  id text primary key,
  user_id text not null references users(id) on delete cascade,
  title text not null,
  message text not null,
  type text not null,
  reference_id text,
  is_read boolean not null default false,
  created_at timestamptz not null default now()
);

-- ── flash_sales ────────────────────────────────────────
create table if not exists flash_sales (
  id text primary key,
  crop_id text not null references crops(id) on delete cascade,
  discount_percentage float not null,
  start_time timestamptz not null,
  end_time timestamptz not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

-- ── helpful indexes ────────────────────────────────────
create index if not exists idx_crops_farmer on crops(farmer_id);
create index if not exists idx_crops_status on crops(status);
create index if not exists idx_requests_farmer on purchase_requests(farmer_id);
create index if not exists idx_requests_buyer on purchase_requests(buyer_id);
create index if not exists idx_bookings_buyer on bookings(buyer_id);
create index if not exists idx_bookings_farmer on bookings(farmer_id);
create index if not exists idx_notif_user on notifications(user_id);

-- ── demo-friendly RLS (disable; tighten for prod) ──────
alter table users disable row level security;
alter table crops disable row level security;
alter table purchase_requests disable row level security;
alter table buyer_requirements disable row level security;
alter table requirement_responses disable row level security;
alter table requirement_matches disable row level security;
alter table bookings disable row level security;
alter table conversations disable row level security;
alter table messages disable row level security;
alter table notifications disable row level security;
alter table flash_sales disable row level security;
