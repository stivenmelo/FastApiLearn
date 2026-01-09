from fastapi import APIRouter
from models import Plan 
from db import SessionDep
from sqlmodel import select

router = APIRouter(tags = ['plans'])

@router.post("/plans")
def create_plan(plan_data: Plan, session: SessionDep):
    plan_db = Plan.model_validate(plan_data.model_dump())
    session.add(plan_db)
    session.commit()
    session.refresh(plan_db)
    return plan_db


@router.get('/plans')
async def list_plans(session: SessionDep ):
    query = select(Plan)
    plans =  session.exec(query).all()
    return plans
