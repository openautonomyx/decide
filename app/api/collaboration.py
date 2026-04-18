"""
Product, Project, Group API Router
Collaboration containers - three distinct entity types
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from app.db.session import get_db
from app.models.collaboration import Product as ProductModel, Project as ProjectModel, GroupEntity as GroupEntityModel
from app.schemas.collaboration import (
    ProductCreate, ProductUpdate, Product, ProductList,
    ProjectCreate, ProjectUpdate, Project, ProjectList,
    GroupCreate, GroupUpdate, Group, GroupList,
)

router = APIRouter(prefix="/collaboration", tags=["collaboration"])

# Products
@router.get("/products", response_model=ProductList)
def list_products(tenant_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(ProductModel)
    if tenant_id:
        query = query.filter(ProductModel.tenant_id == tenant_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return ProductList(total=total, items=items)


@router.post("/products", response_model=Product, status_code=201)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    product = ProductModel(id=str(uuid4()), **product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.patch("/products/{product_id}", response_model=Product)
def update_product(product_id: str, product_in: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in product_in.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


# Projects
@router.get("/projects", response_model=ProjectList)
def list_projects(tenant_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(ProjectModel)
    if tenant_id:
        query = query.filter(ProjectModel.tenant_id == tenant_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return ProjectList(total=total, items=items)


@router.post("/projects", response_model=Project, status_code=201)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    project = ProjectModel(id=str(uuid4()), **project_in.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects/{project_id}", response_model=Project)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# Groups
@router.get("/groups", response_model=GroupList)
def list_groups(tenant_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(GroupEntityModel)
    if tenant_id:
        query = query.filter(GroupEntityModel.tenant_id == tenant_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return GroupList(total=total, items=items)


@router.post("/groups", response_model=Group, status_code=201)
def create_group(group_in: GroupCreate, db: Session = Depends(get_db)):
    group = GroupEntityModel(id=str(uuid4()), **group_in.model_dump())
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.get("/groups/{group_id}", response_model=Group)
def get_group(group_id: str, db: Session = Depends(get_db)):
    group = db.query(GroupEntityModel).filter(GroupEntityModel.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group