from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
import hashlib

from . import models, schemas
from .database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY = "secret"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def convert_hash(password:str):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()[:72]

def hash_password(password: str):
    return pwd_context.hash(convert_hash(password))

def verify_password(plain, hashed):
    return pwd_context.verify(convert_hash(plain), hashed)

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = models.User(
        username=user.username,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Inga form_data use pannirukom, athanala Swagger UI Authorize button work aagum
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )  
    access_token = create_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/doctors", tags=["Doctor"])
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    new_doc = models.Doctor(**doctor.model_dump())
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

@router.get("/doctors", tags=["Doctor"])
def get_doctors(specialization: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Doctor)
    if specialization:
        query = query.filter(models.Doctor.specialization == specialization)
    return query.all()

@router.put("/doctors/{doctor_id}", tags=["Doctor"])
def update_doctor(doctor_id: int, doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    doc = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    for key, value in doctor.model_dump().items():
        setattr(doc, key, value)

    db.commit()
    return {"doctor": "updated Successfully"}

@router.delete("/doctors/{doctor_id}", tags=["Doctor"])
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    db.delete(doc)
    db.commit()
    return {"message": "Doctor deleted"}

@router.post("/patients", tags=["Patients"])
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    new_patient = models.Patient(**patient.model_dump())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@router.get("/patients", tags=["Patients"])
def get_patients(search: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Patient)
    if search:
        query = query.filter(models.Patient.name.contains(search))
    return query.all()

@router.put("/patients/{patient_id}", tags=["Patients"])
def update_patient(patient_id: int, patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    pat = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not pat:
        raise HTTPException(status_code=404, detail="Patient not found")

    for key, value in patient.model_dump().items():
        setattr(pat, key, value)

    db.commit()
    return {"message": "patients_updated"}

@router.delete("/patients/{patient_id}", tags=["Patients"])
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    pat = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not pat:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(pat)
    db.commit() 
    return {"message": "Patient deleted"}

@router.post("/appointments", tags=["Appointment"])
def create_appointment(app: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    new_app = models.Appointment(**app.model_dump())
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

@router.get("/appointments", tags=["Appointment"])
def get_appointments(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return db.query(models.Appointment).all()

@router.get("/appointments/doctor/{doctor_id}", tags=["Appointment"])
def get_by_doctor(doctor_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return db.query(models.Appointment).filter(models.Appointment.doctor_id == doctor_id).all()

@router.get("/appointments/patient/{patient_id}", tags=["Appointment"])
def get_by_patient(patient_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all()

@router.delete("/appointments/{appointment_id}", tags=["Appointment"])
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    app = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(app)
    db.commit()
    return {"message": "Appointment cancelled"}