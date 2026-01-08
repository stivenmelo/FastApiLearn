from fastapi import APIRouter, HTTPException, status

from models import Customer, CustomerCreate, CustomerUpdate
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
