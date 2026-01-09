from fastapi import FastAPI, HTTPException, status
from datetime import datetime
import zoneinfo
from models import Transaction, Invioce
from db import create_all_tables
from .routers import customers, transactions, plans

app = FastAPI(lifespan = create_all_tables)
app.include_router(customers.router)
app.include_router(transactions.router)
app.include_router(plans.router)

@app.get('/')
async def root():
    return {"message": "Hola, Stiven!"}

country_timezones = {
    "CO": "America/Bogota",
    "MX": "America/Mexico_City",
    "AR": "America/Argentina/Buenos_Aires",
    "BR": "America/Sao_Paulo",
    "PE": "America/Lima",
}


@app.get('/time/{iso_code}')
async def time(iso_code: str):
    iso = iso_code.upper()
    timezone_str = country_timezones.get(iso)
    tz = zoneinfo.ZoneInfo(timezone_str)
    return {"time": datetime.now(tz)}


@app.post('/invioces')
async def create_invioces(invioce_data: Invioce):
    return invioce_data