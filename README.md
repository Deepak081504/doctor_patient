# Doctor-Patient API (FastAPI)

This is a simple backend project built using FastAPI to manage doctors, patients, and appointments with authentication.

## Features

* User Registration & Login (JWT)
* Doctor CRUD (Create, Read, Update, Delete)
* Patient CRUD
* Appointment Booking
* Protected APIs using token

## Tech Stack

* FastAPI
* SQLAlchemy
* SQLite
* JWT Authentication
* Uvicorn

## API Endpoints

### Auth

* POST /register
* POST /login

### Doctors

* POST /doctors
* GET /doctors
* PUT /doctors/{id}
* DELETE /doctors/{id}

### Patients

* POST /patients
* GET /patients
* PUT /patients/{id}
* DELETE /patients/{id}

### Appointments

* POST /appointments
* GET /appointments
* GET /appointments/doctor/{id}
* GET /appointments/patient/{id}
* DELETE /appointments/{id}
