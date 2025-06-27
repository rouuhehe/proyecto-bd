-- Active: 1746627980787@@127.0.0.1@5433@bd

-- Tabla Persona
CREATE TABLE persona (
    dni VARCHAR(8) PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    telefono VARCHAR(9) NOT NULL
);

-- Tabla Propietario
CREATE TABLE Propietario (
    dni_persona VARCHAR(8) PRIMARY KEY REFERENCES Persona(dni)
);

-- Tabla Empleado
CREATE TABLE Empleado (
    dni_persona VARCHAR(8) PRIMARY KEY REFERENCES Persona(dni),
    fecha_ingreso DATE NOT NULL,
    inicio_turno TIME NOT NULL,
    fin_turno TIME NOT NULL,
    salario DOUBLE PRECISION NOT NULL
);

-- Tabla Veterinario
CREATE TABLE Veterinario (
    dni_persona VARCHAR(8) PRIMARY KEY REFERENCES Empleado(dni_persona),
    num_colegiatura VARCHAR(20) UNIQUE NOT NULL,
    especializacion VARCHAR(100) NOT NULL
);

-- Tabla Recepcionista
CREATE TABLE Recepcionista (
    dni_persona VARCHAR(8) PRIMARY KEY REFERENCES Empleado(dni_persona),
    telefono_fijo VARCHAR(5) NOT NULL
);

-- Tabla Administrador
CREATE TABLE Administrador (
    dni_persona VARCHAR(8) PRIMARY KEY REFERENCES Empleado(dni_persona),
    rango VARCHAR(50) NOT NULL
);

-- Tabla Mascota
CREATE TABLE Mascota (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL,
    especie VARCHAR(30) NOT NULL,
    raza VARCHAR(30) NOT NULL,
    sexo CHAR(1) NOT NULL,
    fecha_nac DATE NOT NULL
);

-- Tabla Boleta
CREATE TABLE Boleta (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    dni_persona_cliente VARCHAR(8) REFERENCES Persona(dni) NOT NULL,
    dni_persona_recepcionista VARCHAR(8) REFERENCES Recepcionista(dni_persona) NOT NULL,
    monto DECIMAL(10,2) NOT NULL
);

-- Tabla Tratamiento
CREATE TABLE Tratamiento (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL,
    id_boleta INT REFERENCES Boleta(id) NOT NULL
);

-- Tabla Cita
CREATE TABLE Cita (
    id SERIAL PRIMARY KEY,
    dni_veterinario VARCHAR(8) REFERENCES Veterinario(dni_persona) NOT NULL,
    hora TIME NOT NULL,
    fecha DATE NOT NULL,
    id_mascota INT REFERENCES Mascota(id) NOT NULL,
    dni_recepcionista VARCHAR(8) REFERENCES Recepcionista(dni_persona) NOT NULL,
    estado VARCHAR(30) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    motivo VARCHAR(100) NOT NULL
);

-- Tabla Diagnóstico
CREATE TABLE Diagnostico (
    id SERIAL PRIMARY KEY,
    id_cita INT REFERENCES Cita(id) NOT NULL,
    fecha DATE NOT NULL,
    sintomas VARCHAR(255) NOT NULL,
    observaciones VARCHAR(255) NOT NULL
);


-- Tabla Proveedor

CREATE TABLE Proveedor (
    administrador VARCHAR(8) REFERENCES Administrador(dni_persona) NOT NULL,
    ruc VARCHAR(11) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);
-- Tabla Insumo
CREATE TABLE Insumo (
    id SERIAL PRIMARY KEY ,
    dni_persona VARCHAR(8) REFERENCES Recepcionista(dni_persona) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    ruc_proveedor VARCHAR(11) REFERENCES Proveedor(ruc) NOT NULL,
    stock INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL
);



-- Especializaciones de tratamiento
CREATE TABLE Terapia (
    id_tratamiento INT PRIMARY KEY REFERENCES Tratamiento(id),
    fechaInicio DATE NOT NULL,
    fechaFin DATE NOT NULL
);

CREATE TABLE Receta (
    id_tratamiento INT PRIMARY KEY REFERENCES Tratamiento(id),
    frecuencia VARCHAR(20) NOT NULL
);

CREATE TABLE Cirugia (
    id_tratamiento INT PRIMARY KEY REFERENCES Tratamiento(id),
    duracion DECIMAL(5,2) NOT NULL
);

CREATE TABLE Vacunacion (
    id_tratamiento INT NOT NULL,
    id_insumo INT NOT NULL,
    PRIMARY KEY (id_tratamiento, id_insumo),
    FOREIGN KEY (id_tratamiento) REFERENCES Tratamiento(id),
    FOREIGN KEY (id_insumo) REFERENCES Insumo(id)
);

CREATE TABLE Vacuna (
    id_insumo INT PRIMARY KEY REFERENCES Insumo(id),
    fecha_venc DATE NOT NULL
);

CREATE TABLE Medicamento (
    id_insumo INT PRIMARY KEY REFERENCES Insumo(id)
);

-- Relación UsoInsumo
CREATE TABLE UsoInsumo (
    id_boleta INT,
    id_insumo INT,
    motivo VARCHAR(100) NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (id_boleta, id_insumo),
    FOREIGN KEY (id_boleta) REFERENCES Boleta(id),
    FOREIGN KEY (id_insumo) REFERENCES Insumo(id)
);

-- Relación Compra
CREATE TABLE Compra (
    dni_persona VARCHAR(8),
    id_boleta INT,
    PRIMARY KEY (dni_persona, id_boleta),
    FOREIGN KEY (dni_persona) REFERENCES Propietario(dni_persona),
    FOREIGN KEY (id_boleta) REFERENCES Boleta(id)
);

-- Relación BoletaTieneCita
CREATE TABLE BoletaTieneCita (
    id_boleta INT,
    id_cita INT,
    PRIMARY KEY (id_boleta, id_cita),
    FOREIGN KEY (id_boleta) REFERENCES Boleta(id),
    FOREIGN KEY (id_cita) REFERENCES Cita(id)
);

-- Relación PropietarioTieneMascota
CREATE TABLE PropietarioTieneMascota (
    dni_propietario VARCHAR(8),
    id_mascota INT,
    PRIMARY KEY (dni_propietario, id_mascota),
    FOREIGN KEY (dni_propietario) REFERENCES Propietario(dni_persona),
    FOREIGN KEY (id_mascota) REFERENCES Mascota(id)
);

-- Relación Documenta
CREATE TABLE Documenta (
    id_boleta INT,
    id_tratamiento INT,
    PRIMARY KEY (id_boleta, id_tratamiento),
    FOREIGN KEY (id_boleta) REFERENCES Boleta(id),
    FOREIGN KEY (id_tratamiento) REFERENCES Tratamiento(id)
);

-- Relación Recibe
CREATE TABLE Recibe (
    id_mascota INT,
    id_tratamiento INT,
    id_cita INT REFERENCES Cita(id),
    PRIMARY KEY (id_mascota, id_tratamiento),
    FOREIGN KEY (id_mascota) REFERENCES Mascota(id),
    FOREIGN KEY (id_tratamiento) REFERENCES Tratamiento(id)
);

-- Relación Resulta
CREATE TABLE Resulta (
    id_tratamiento INT,
    id_diagnostico INT,
    PRIMARY KEY (id_tratamiento, id_diagnostico),
    FOREIGN KEY (id_tratamiento) REFERENCES Tratamiento(id),
    FOREIGN KEY (id_diagnostico) REFERENCES Diagnostico(id)
);

-- Relación Deriva
CREATE TABLE Deriva (
    id_diagnostico INT,
    id_cita INT,
    PRIMARY KEY (id_diagnostico, id_cita),
    FOREIGN KEY (id_diagnostico) REFERENCES Diagnostico(id),
    FOREIGN KEY (id_cita) REFERENCES Cita(id)
);

-- Relación Usa
CREATE TABLE Usa (
    id_cita INT,
    id_insumo INT,
    cantidad INT,
    PRIMARY KEY (id_cita, id_insumo),
    FOREIGN KEY (id_cita) REFERENCES Cita(id),
    FOREIGN KEY (id_insumo) REFERENCES Insumo(id)
);

-- Relación Gestiona
CREATE TABLE Gestiona (
    dni_persona VARCHAR(8),
    id_insumo INT,
    PRIMARY KEY (dni_persona, id_insumo),
    FOREIGN KEY (dni_persona) REFERENCES Recepcionista(dni_persona),
    FOREIGN KEY (id_insumo) REFERENCES Insumo(id)
);

-- Relación Provee
CREATE TABLE Provee (
    ruc_proveedor VARCHAR(11),
    id_insumo INT,
    PRIMARY KEY (ruc_proveedor, id_insumo),
    FOREIGN KEY (ruc_proveedor) REFERENCES Proveedor(ruc),
    FOREIGN KEY (id_insumo) REFERENCES Insumo(id)
);

-- Relación Contacta
CREATE TABLE Contacta (
    dni_persona VARCHAR(8),
    ruc_proveedor VARCHAR(11),
    PRIMARY KEY (dni_persona, ruc_proveedor),
    FOREIGN KEY (dni_persona) REFERENCES Administrador(dni_persona),
    FOREIGN KEY (ruc_proveedor) REFERENCES Proveedor(ruc)
);

-- Relación Usa_m
CREATE TABLE Usa_m (
    id_tratamiento INT,
    id_insumo INT,
    cantidad INT,
    PRIMARY KEY (id_tratamiento, id_insumo),
    FOREIGN KEY (id_tratamiento) REFERENCES Tratamiento(id),
    FOREIGN KEY (id_insumo) REFERENCES Insumo(id)
);


