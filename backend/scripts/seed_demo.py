"""Seed demo users + sample crops for the minor-project review.
Run after supabase/schema.sql:  python scripts/seed_demo.py
Needs backend/.env with SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY.
ponytail: stdlib+supabase only, idempotent deletes-by-email first.
"""
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import bcrypt  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from supabase import create_client  # noqa: E402

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
assert URL and KEY, "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in backend/.env"

sb = create_client(URL, KEY)
now = datetime.now(timezone.utc)
DEMO = [
    {"name": "Demo Farmer", "email": "farmer.demo@raithusethu.in", "password": "Farmer@123",
     "phone": "9876543210", "role": "farmer", "location": "Mysuru, Karnataka",
     "farm_size": 5.0, "is_verified": True},
    {"name": "Demo Buyer", "email": "buyer.demo@raithusethu.in", "password": "Buyer@123",
     "phone": "9876543211", "role": "buyer", "company_name": "FreshMart Foods",
     "is_verified": True},
    {"name": "Demo Admin", "email": "admin.demo@raithusethu.in", "password": "Admin@123",
     "phone": "9876543212", "role": "admin", "is_verified": True},
]

ids = {}
for u in DEMO:
    pw = u.pop("password")
    sb.table("users").delete().eq("email", u["email"]).execute()
    row = {"id": str(uuid.uuid4()),
           "password_hash": bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode(),
           "created_at": now.isoformat(), **u}
    sb.table("users").insert(row).execute()
    ids[u["role"]] = row["id"]
    print(f'{u["role"]:7} {u["email"]} / {pw}')

crops = [
    {"name": "Sona Masoori Paddy", "category": "Grains & Cereals", "quantity": 500,
     "unit": "quintal", "price_per_unit": 2200, "location": "Mysuru, Karnataka",
     "description": "Freshly harvested Sona Masoori, demo listing."},
    {"name": "Tomato", "category": "Vegetables", "quantity": 200,
     "unit": "kg", "price_per_unit": 28, "location": "Mysuru, Karnataka",
     "description": "Farm-fresh tomatoes, demo listing."},
    {"name": "Turmeric Fingers", "category": "Spices", "quantity": 100,
     "unit": "kg", "price_per_unit": 180, "location": "Mysuru, Karnataka",
     "description": "High-curcumin turmeric, demo listing."},
]
for c in crops:
    sb.table("crops").insert({
        "id": str(uuid.uuid4()), "farmer_id": ids["farmer"],
        "harvest_date": now.isoformat(),
        "expiry_date": (now + timedelta(days=30)).isoformat(),
        "status": "active", "images": [],
        "created_at": now.isoformat(), **c}).execute()
print(f"Seeded {len(crops)} crops for the demo farmer.")
print("Done. Log in on the frontend with the emails/passwords above.")
