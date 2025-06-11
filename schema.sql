-- schema.sql: crea la tabla trabajadores
DROP TABLE IF EXISTS trabajadores;

CREATE TABLE trabajadores (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  rol VARCHAR(100) NOT NULL,
  habilidades TEXT,
  semanas_disponible INTEGER
);
