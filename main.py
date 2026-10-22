import os
import pymysql
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time

app = FastAPI(
    title="API Completa de LoUDI",
    description="API REST con todas las tablas y relaciones de la base de datos LoUDI",
    version="2.0"
)

# Conexión a MySQL en la nube (Aiven)
def get_db_connection():
    return pymysql.connect(
        host="mysql-35731f3f-utsjr-f320.aivencloud.com",
        user="avnadmin",
        password="AVNS_zKLS3uWvvQUa_vSih1o",  # Contraseña configurada para tu instancia de Aiven
        database="LoUDi",
        port=27731,
        cursorclass=pymysql.cursors.DictCursor,
        ssl={"ssl_mode": "REQUIRED"}
    )

# ==========================================
# MODELOS PYDANTIC (Validación de entrada)
# ==========================================

class AdministradorCreate(BaseModel):
    id_Administrador: int
    Nombre_Administrador: str
    Apellido_Administrador: str
    Correo_Administrador: str
    Contraseña_Administrador: str

class HorarioCreate(BaseModel):
    idHorario: int
    Turno: str
    HoraEntrada: time
    HoraSalida: time

class EstudianteCreate(BaseModel):
    NoControl: int
    Nombre_Estudiante: str
    Apellido_Estudiante: str
    Telefono: str
    Cuatrimestre: str
    Colonia: str
    Municipio: str
    CP: int
    Estado: str
    Calle: str
    NoCalle: int
    Contraseña: str
    id_Administrador1: Optional[int] = None
    idHorario1: Optional[int] = None

class PagoCreate(BaseModel):
    IdPago: int
    Monto: float
    Estatus: str
    Fecha: date

class ViajeCreate(BaseModel):
    idViaje: int
    Origen: str
    Destino: str
    Precio_Estimado: float
    Asientos_Disponibles: int
    Estado: str

class VehiculoCreate(BaseModel):
    idVehiculo: int
    Placa: str
    Modelo: str
    Año: int
    Color: str
    NoSeguro: str
    Capacidad_Pasajeros: int

class PasajeroCreate(BaseModel):
    IdPasajero1: int # FK a Estudiante(NoControl)
    IdPago1: Optional[int] = None # FK a Pago(IdPago)

class ConductorCreate(BaseModel):
    IdConductor: int # FK a Estudiante(NoControl)
    NumLicencia: str
    Num_Viajes: int

class SolicitaCreate(BaseModel):
    IdPasajero1: Optional[int] = None
    Fecha: date
    Hora: time
    Califica: float
    IdViaje1: Optional[int] = None

class PoseeCreate(BaseModel):
    IdConductor1: Optional[int] = None
    IdVehiculo1: Optional[int] = None

class RealizaCreate(BaseModel):
    IdConductor2: Optional[int] = None
    IdViaje2: Optional[int] = None
    IdVehiculo2: Optional[int] = None
    Fecha_Realiza: date
    Hora_Realiza: time


# ==========================================
# ENDPOINT PARA CARGAR DATOS DE PRUEBA
# ==========================================

@app.post("/api/sembrar-datos-prueba", tags=["Datos de Prueba"])
def sembrar_datos_prueba():
    """Puebla todas las tablas con datos de prueba respetando las relaciones de FK"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Desactivar temporalmente revisión de FKs para evitar conflictos al limpiar
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            
            # 1. Administrador
            cursor.execute("""
                INSERT IGNORE INTO Administrador (id_Administrador, Nombre_Administrador, Apellido_Administrador, Correo_Administrador, Contraseña_Administrador)
                VALUES (1, 'Carlos', 'Gómez', 'carlos.admin@loudi.com', 'adminPass123');
            """)

            # 2. Horario
            cursor.execute("""
                INSERT IGNORE INTO Horario (idHorario, Turno, HoraEntrada, HoraSalida)
                VALUES 
                (1, 'Matutino', '07:00:00', '14:00:00'),
                (2, 'Vespertino', '14:00:00', '21:00:00');
            """)

            # 3. Estudiante (Servirán como Pasajeros y Conductores)
            cursor.execute("""
                INSERT IGNORE INTO Estudiante (NoControl, Nombre_Estudiante, Apellido_Estudiante, Telefono, Cuatrimestre, Colonia, Municipio, CP, Estado, Calle, NoCalle, Contraseña, id_Administrador1, idHorario1)
                VALUES 
                (2023001, 'Ana', 'Martínez', '4421234567', '4to', 'Centro', 'Querétaro', 76000, 'Querétaro', 'Hidalgo', 12, 'ana12345', 1, 1),
                (2023002, 'Luis', 'Hernández', '4429876543', '5to', 'Candelaria', 'San Juan del Río', 76800, 'Querétaro', 'Juárez', 45, 'luis12345', 1, 2);
            """)

            # 4. Pago
            cursor.execute("""
                INSERT IGNORE INTO Pago (IdPago, Monto, Estatus, Fecha)
                VALUES (101, 35.50, 'Completado', '2026-03-01');
            """)

            # 5. Viaje
            cursor.execute("""
                INSERT IGNORE INTO Viaje (idViaje, Origen, Destino, Precio_Estimado, Asientos_Disponibles, Estado)
                VALUES (501, 'Centro San Juan', 'Universidad', 35.50, 3, 'Disponible');
            """)

            # 6. Vehiculo
            cursor.execute("""
                INSERT IGNORE INTO Vehiculo (idVehiculo, Placa, Modelo, Año, Color, NoSeguro, Capacidad_Pasajeros)
                VALUES (1, 'UKJ-123-A', 'Nissan Versa', 2022, 'Rojo', 'SEG-998877', 4);
            """)

            # 7. Pasajero (Vinculado a Estudiante 2023001 y Pago 101)
            cursor.execute("""
                INSERT IGNORE INTO Pasajero (IdPasajero1, IdPago1)
                VALUES (2023001, 101);
            """)

            # 8. Conductor (Vinculado a Estudiante 2023002)
            cursor.execute("""
                INSERT IGNORE INTO Conductor (IdConductor, NumLicencia, Num_Viajes)
                VALUES (2023002, 'LIC88776', 15);
            """)

            # 9. Solicita (Pasajero solicita Viaje)
            cursor.execute("""
                INSERT IGNORE INTO Solicita (IdPasajero1, Fecha, Hora, Califica, IdViaje1)
                VALUES (2023001, '2026-03-01', '07:30:00', 4.8, 501);
            """)

            # 10. Posee (Conductor posee Vehiculo)
            cursor.execute("""
                INSERT IGNORE INTO Posee (IdConductor1, IdVehiculo1)
                VALUES (2023002, 1);
            """)

            # 11. Realiza (Conductor realiza Viaje con Vehiculo)
            cursor.execute("""
                INSERT IGNORE INTO Realiza (IdConductor2, IdViaje2, IdVehiculo2, Fecha_Realiza, Hora_Realiza)
                VALUES (2023002, 501, 1, '2026-03-01', '07:30:00');
            """)

            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            connection.commit()
            return {"message": "¡Datos de prueba insertados exitosamente en todas las tablas!"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error al sembrar datos: {str(e)}")
    finally:
        connection.close()


# ==========================================
# RUTAS DE CADA TABLA (CRUD)
# ==========================================

# --- ADMINISTRADOR ---
@app.get("/api/administradores", tags=["Administrador"])
def obtener_administradores():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Administrador")
            return cursor.fetchall()
    finally:
        connection.close()

@app.post("/api/administradores", status_code=201, tags=["Administrador"])
def crear_administrador(admin: AdministradorCreate):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Administrador VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (admin.id_Administrador, admin.Nombre_Administrador, admin.Apellido_Administrador, admin.Correo_Administrador, admin.Contraseña_Administrador))
            connection.commit()
            return {"message": "Administrador registrado"}
    finally:
        connection.close()

# --- HORARIO ---
@app.get("/api/horarios", tags=["Horario"])
def obtener_horarios():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Horario")
            return cursor.fetchall()
    finally:
        connection.close()

@app.post("/api/horarios", status_code=201, tags=["Horario"])
def crear_horario(horario: HorarioCreate):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Horario VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (horario.idHorario, horario.Turno, horario.HoraEntrada, horario.HoraSalida))
            connection.commit()
            return {"message": "Horario registrado"}
    finally:
        connection.close()

# --- ESTUDIANTE ---
@app.get("/api/estudiantes", tags=["Estudiante"])
def obtener_estudiantes():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Estudiante")
            return cursor.fetchall()
    finally:
        connection.close()

@app.post("/api/estudiantes", status_code=201, tags=["Estudiante"])
def crear_estudiante(est: EstudianteCreate):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """INSERT INTO Estudiante (NoControl, Nombre_Estudiante, Apellido_Estudiante, Telefono, Cuatrimestre, Colonia, Municipio, CP, Estado, Calle, NoCalle, Contraseña, id_Administrador1, idHorario1)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (est.NoControl, est.Nombre_Estudiante, est.Apellido_Estudiante, est.Telefono, est.Cuatrimestre, est.Colonia, est.Municipio, est.CP, est.Estado, est.Calle, est.NoCalle, est.Contraseña, est.id_Administrador1, est.idHorario1))
            connection.commit()
            return {"message": "Estudiante registrado"}
    finally:
        connection.close()

# --- PAGO ---
@app.get("/api/pagos", tags=["Pago"])
def obtener_pagos():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Pago")
            return cursor.fetchall()
    finally:
        connection.close()

# --- VIAJE ---
@app.get("/api/viajes", tags=["Viaje"])
def obtener_viajes():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Viaje")
            return cursor.fetchall()
    finally:
        connection.close()

# --- VEHICULO ---
@app.get("/api/vehiculos", tags=["Vehiculo"])
def obtener_vehiculos():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Vehiculo")
            return cursor.fetchall()
    finally:
        connection.close()

# --- PASAJERO ---
@app.get("/api/pasajeros", tags=["Pasajero"])
def obtener_pasajeros():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT P.IdPasajero1, E.Nombre_Estudiante, E.Apellido_Estudiante, P.IdPago1, Pag.Monto, Pag.Estatus 
                FROM Pasajero P
                JOIN Estudiante E ON P.IdPasajero1 = E.NoControl
                LEFT JOIN Pago Pag ON P.IdPago1 = Pag.IdPago
            """)
            return cursor.fetchall()
    finally:
        connection.close()

# --- CONDUCTOR ---
@app.get("/api/conductores", tags=["Conductor"])
def obtener_conductores():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT C.IdConductor, E.Nombre_Estudiante, E.Apellido_Estudiante, C.NumLicencia, C.Num_Viajes
                FROM Conductor C
                JOIN Estudiante E ON C.IdConductor = E.NoControl
            """)
            return cursor.fetchall()
    finally:
        connection.close()

# --- SOLICITA (RELACIÓN PASAJERO - VIAJE) ---
@app.get("/api/solicitudes", tags=["Solicita"])
def obtener_solicitudes():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Solicita")
            return cursor.fetchall()
    finally:
        connection.close()

# --- POSEE (RELACIÓN CONDUCTOR - VEHICULO) ---
@app.get("/api/posee", tags=["Posee"])
def obtener_posee():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT P.IdConductor1, E.Nombre_Estudiante, V.Modelo, V.Placa 
                FROM Posee P
                JOIN Conductor C ON P.IdConductor1 = C.IdConductor
                JOIN Estudiante E ON C.IdConductor = E.NoControl
                JOIN Vehiculo V ON P.IdVehiculo1 = V.idVehiculo
            """)
            return cursor.fetchall()
    finally:
        connection.close()

# --- REALIZA (RELACIÓN CONDUCTOR - VIAJE - VEHICULO) ---
@app.get("/api/realiza", tags=["Realiza"])
def obtener_realiza():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT R.IdConductor2, E.Nombre_Estudiante, R.IdViaje2, V.Origen, V.Destino, R.IdVehiculo2, R.Fecha_Realiza, R.Hora_Realiza
                FROM Realiza R
                JOIN Conductor C ON R.IdConductor2 = C.IdConductor
                JOIN Estudiante E ON C.IdConductor = E.NoControl
                JOIN Viaje V ON R.IdViaje2 = V.idViaje
            """)
            return cursor.fetchall()
    finally:
        connection.close()
