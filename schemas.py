from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class DoctorCreate(BaseModel):
    name: str
    specialization: str

class DoctorUpdate(BaseModel):
    name: str

class PatientCreate(BaseModel):
    name: str
    phone: str

class PatientUpdate(BaseModel):
    name: str

class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_id: int
    appointment_date: datetime