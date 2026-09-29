import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, String, Float, Integer, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL=os.getenv("DATABASE_URL","sqlite:///./sentinel.db")
engine=create_engine(DATABASE_URL,pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)
class Base(DeclarativeBase): pass
class Supplier(Base):
    __tablename__="suppliers"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[str]=mapped_column(String(200),unique=True,index=True)
    category:Mapped[str]=mapped_column(String(40),default="non-critical")
    on_time_rate:Mapped[float]=mapped_column(Float,default=1.0)
    order_accuracy:Mapped[float]=mapped_column(Float,default=1.0)
    quality_issues:Mapped[int]=mapped_column(Integer,default=0)
class Material(Base):
    __tablename__="materials"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[str]=mapped_column(String(200),unique=True,index=True)
    unit:Mapped[str]=mapped_column(String(30),default="pcs")
    on_hand:Mapped[float]=mapped_column(Float,default=0)
    in_transit:Mapped[float]=mapped_column(Float,default=0)
    reserved:Mapped[float]=mapped_column(Float,default=0)
    daily_consumption:Mapped[float]=mapped_column(Float,default=0)
class PurchaseOrder(Base):
    __tablename__="purchase_orders"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    po_number:Mapped[str]=mapped_column(String(100),unique=True,index=True)
    supplier_id:Mapped[int]=mapped_column(Integer)
    material_id:Mapped[int]=mapped_column(Integer)
    quantity:Mapped[float]=mapped_column(Float)
    unit_price:Mapped[float]=mapped_column(Float,default=0)
    promised_date:Mapped[datetime]=mapped_column(DateTime)
    actual_date:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
    status:Mapped[str]=mapped_column(String(30),default="open")
class Document(Base):
    __tablename__="documents"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    filename:Mapped[str]=mapped_column(String(255))
    document_type:Mapped[str]=mapped_column(String(50),default="unknown")
    confidence:Mapped[float]=mapped_column(Float,default=0)
    extracted_json:Mapped[str]=mapped_column(Text,default="{}")
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Alert(Base):
    __tablename__="alerts"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    po_id:Mapped[int|None]=mapped_column(Integer,nullable=True)
    severity:Mapped[str]=mapped_column(String(30))
    title:Mapped[str]=mapped_column(String(255))
    message:Mapped[str]=mapped_column(Text)
    evidence_json:Mapped[str]=mapped_column(Text,default="{}")
    recommendation:Mapped[str]=mapped_column(Text)
    status:Mapped[str]=mapped_column(String(30),default="pending")
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Decision(Base):
    __tablename__="decisions"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    alert_id:Mapped[int]=mapped_column(Integer)
    action:Mapped[str]=mapped_column(String(30))
    comment:Mapped[str]=mapped_column(Text,default="")
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
def init_db():
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    try:
        if db.query(Supplier).count()==0:
            s1=Supplier(name="ABC Metals Pvt Ltd",category="bottleneck",on_time_rate=.72,order_accuracy=.94,quality_issues=2)
            s2=Supplier(name="Precision Components",category="strategic",on_time_rate=.91,order_accuracy=.98,quality_issues=0)
            db.add_all([s1,s2]); db.flush()
            m1=Material(name="Steel Sheet 2mm",unit="kg",on_hand=450,in_transit=300,reserved=100,daily_consumption=120)
            m2=Material(name="Bearing 6204",unit="pcs",on_hand=35,in_transit=100,reserved=10,daily_consumption=8)
            db.add_all([m1,m2]); db.flush()
            db.add_all([PurchaseOrder(po_number="PO-1001",supplier_id=s1.id,material_id=m1.id,quantity=300,unit_price=82,promised_date=datetime.utcnow()+timedelta(days=2),status="open"),PurchaseOrder(po_number="PO-1002",supplier_id=s2.id,material_id=m2.id,quantity=100,unit_price=145,promised_date=datetime.utcnow()+timedelta(days=6),status="open")])
            db.commit()
    finally: db.close()
