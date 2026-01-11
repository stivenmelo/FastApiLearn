from fastapi import APIRouter, HTTPException, status,Query
from models import Customer, CustomerCreate, CustomerPlan, CustomerUpdate, Plan, StatusEnum
from db import SessionDep
from sqlmodel import select 

router = APIRouter(tags = ['customers'])


@router.post('/customers',response_model = Customer, tags = ['customers'])
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer) 
    return customer

@router.get('/customers/{customer_id}',response_model = Customer, tags = ['customers'])
async def read_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Customer doesn't exist")
    return customer_db

@router.delete('/customers/{customer_id}', tags = ['customers'])
async def delete_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, detail = "Customer doesn't exist"
            )
    
    session.delete(customer_db)
    session.commit()
    return {"detail": "Ok"}

@router.patch('/customers/{customer_id}',response_model = Customer, status_code = status.HTTP_201_CREATED, tags = ['customers'])
async def update_customer(customer_id: int, customer_data: CustomerUpdate , session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Customer doesn't exist")
    
    customer_data_dict = customer_data.model_dump(exclude_unset = True)
    customer_db.sqlmodel_update(customer_data_dict)
    session.add(customer_db)
    session.commit()
    session.refresh(customer_db)
    return customer_db

@router.get('/customers',response_model = list[Customer], tags = ['customers'])
async def list_customer(session: SessionDep):
    return session.exec(select(Customer)).all()
     

@router.get('/customers/{id}',response_model = Customer | None, tags = ['customers'])
async def customer_whit_id(id:int, session: SessionDep):
    results =  session.exec(select(Customer).where(Customer.id == id))
    for customer in results:
        return customer
    raise HTTPException(status_code=404, detail="Customer not found")


@router.post('/customers/{customer_id}/plans/{plan_id}',response_model = CustomerPlan, tags = ['customers'])
async def suscribe_customer_to_plan(customer_id: int ,plan_id: int ,session: SessionDep, plan_status: StatusEnum = Query()):
    customer_db = session.get(Customer, customer_id)
    pland_db = session.get(Plan, plan_id)
    
    
    if not customer_db or not pland_db:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "The customer or plan doesn't exist")
    
    customer_pland_db = CustomerPlan(plan_id = pland_db.id, customer_id = customer_db.id, status = plan_status)
    session.add(customer_pland_db)
    session.commit()
    session.refresh(customer_pland_db)
    return customer_pland_db


@router.get('/customers/{customer_id}/plans/',response_model = list[Plan], tags = ['customers'])
async def customer_plans(customer_id: int ,session: SessionDep, plan_status: StatusEnum = Query()):
    customer_db =  session.get(Customer, customer_id)
    
    if not customer_db:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "The customer doesn't exist")
    query = select(CustomerPlan).where(CustomerPlan.customer_id == customer_id).where(CustomerPlan.status == plan_status)
    customer_plans_result = session.exec(query).all()
    
    plans_ids: list[int] = [customer_plan.plan_id for customer_plan in customer_plans_result] 
    query_plans = select(Plan).where(Plan.id.in_(plans_ids))
    plans = session.exec(query_plans).all()
    
    return plans
    