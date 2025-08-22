-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS fitness CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Usar la base de datos fitness
USE fitness;

-- ===========================
-- Tabla de contactos/usuarios
-- ===========================
CREATE TABLE IF NOT EXISTS contactos (
    id_contacto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    mensaje TEXT NOT NULL,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_correo (correo),
    INDEX idx_fecha (fecha_envio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================
-- Tabla de programas
-- ===========================
CREATE TABLE IF NOT EXISTS programas (
    id_programa INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT NOT NULL,
    INDEX idx_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================
-- Relación contactos con programas (tabla intermedia)
-- ===========================
CREATE TABLE IF NOT EXISTS contacto_programa (
    id_contacto INT NOT NULL,
    id_programa INT NOT NULL,
    fecha_asociacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_contacto, id_programa),
    FOREIGN KEY (id_contacto) REFERENCES contactos(id_contacto) ON DELETE CASCADE,
    FOREIGN KEY (id_programa) REFERENCES programas(id_programa) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================
-- Insertar programas iniciales
-- ===========================
INSERT IGNORE INTO programas (nombre, descripcion) VALUES
('Yoga Natural', 'Conecta con tu respiración y el entorno, mejora tu flexibilidad y encuentra paz interior mediante prácticas de yoga al aire libre.'),
('Bootcamp al Aire Libre', 'Entrenamiento intenso que combina ejercicios de fuerza, cardio y agilidad en un entorno natural estimulante.'),
('Running en Senderos', 'Explora rutas únicas en la naturaleza y mejora tu resistencia cardiovascular con nuestros grupos de running guiados.');

-- ===========================
-- Crear usuario para la aplicación (opcional)
-- ===========================
-- Solo ejecutar si se necesita crear un usuario específico
-- GRANT ALL PRIVILEGES ON fitness.* TO 'fitnessuser'@'%' IDENTIFIED BY 'userpassword';
-- FLUSH PRIVILEGES;