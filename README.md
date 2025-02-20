# Plataforma de Scripts Colaborativos

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange.svg)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/[tu-usuario]/plataforma-scripts-colaborativos.svg)](https://github.com/[tu-usuario]/plataforma-scripts-colaborativos/stargazers)

Aplicación colaborativa diseñada para facilitar la vida de los administradores de sistemas mediante la gestión, edición, ejecución y compartición de scripts en Python y PowerShell, con almacenamiento en MySQL.

![Captura de pantalla de la aplicación](screenshot.png) <!-- Sustituye por una captura real -->

## Descripción

La **Plataforma de Scripts Colaborativos** es un proyecto desarrollado por **Pedro Miguel Morales Calderín** y **Eloy Ramírez Revuelta** como parte de nuestro Trabajo de Fin de Grado (TFG) en el Ciclo Formativo de Grado Superior en Administración de Sistemas Informáticos en Red (ASIR) en el Instituto CIFP Villa de Agüimes. Este proyecto tiene como objetivo optimizar las tareas diarias de los administradores de sistemas, permitiendo la colaboración en tiempo real, la portabilidad de scripts y su accesibilidad inmediata desde una interfaz gráfica moderna. Tanto la idea como la programación general y de la base de datos fueron un esfuerzo conjunto de ambos autores, quienes diseñaron e implementaron cada aspecto del sistema.

## ✨ Características principales

- **Autenticación segura**: Sistema de login con roles (`admin` y `user`) y contraseñas cifradas con SHA-256
- **Soporte multilenguaje**: Interfaz en español e inglés, con traducción dinámica de todos los elementos
- **Ejecución de scripts**: Compatible con Python (`.py`) y PowerShell (`.ps1`), captura salida y errores en tiempo real
- **Resaltado de sintaxis**: Resaltado básico para palabras clave de Python y comandos comunes de PowerShell
- **Colaboración**: Subida, descarga y compartición de scripts entre usuarios, con estadísticas (ejecuciones y descargas)
- **Historial de ejecuciones**: Registro detallado de cada ejecución, exportable a `.txt`
- **Administración**: Panel para gestionar usuarios (aprobar, eliminar, cambiar roles), exclusivo para administradores
- **Base de datos MySQL**: Persistencia de scripts, usuarios y logs, alojada en Railway para escalabilidad
- **Interfaz moderna**: Tema personalizable (oscuro/claro) con `ttkbootstrap`
- **Carga asíncrona**: Uso de `threading` para optimizar el rendimiento

## ⚙️ Requisitos

- **Python 3.12+**: [Descargar aquí](https://www.python.org/downloads/)
- **MySQL Server 8.0+**: [Descargar aquí](https://www.mysql.com/downloads/) o usar un servicio remoto como Railway
- **PowerShell**: Requerido en Windows para scripts `.ps1`
- **Dependencias**:
  ```bash
  pip install mysql-connector-python ttkbootstrap
  ```

## 🛠️ Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/[tu-usuario]/plataforma-scripts-colaborativos.git
   cd plataforma-scripts-colaborativos
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura las credenciales de la base de datos en `main.py`:
   ```python
   self.db_config = {
       'host': 'roundhouse.proxy.rlwy.net',
       'port': 15111,
       'user': 'root',
       'password': 'yLGTWKFUCjGcDQiuCjWMrnObyAjHERra',
       'database': 'railway',
       'ssl_disabled': True
   }
   ```
   Nota: Ajusta estas credenciales si usas un servidor MySQL local o diferente.

4. Ejecuta la aplicación:
   ```bash
   python main.py
   ```

## 🔧 Configuración Inicial

- Usuario predeterminado:
  - Username: pedro
  - Password: admin123
- La base de datos se crea automáticamente al iniciar la aplicación por primera vez, incluyendo las tablas scripts, users y execution_logs.

## 🖥️ Uso

### Interfaz gráfica

La aplicación se divide en tres pestañas:

1. **Scripts**:
   - Lista de scripts disponibles
   - Editor con resaltado de sintaxis
   - Botones: Subir Script, Descargar, Ejecutar, Vista Previa, Guardar

2. **Historial**: 
   - Registro de ejecuciones con opción de exportar a .txt

3. **Administración** (solo para admin): 
   - Gestión de usuarios con botones para aprobar, eliminar y cambiar roles

### Ejemplo de uso

1. Inicia sesión con tus credenciales
2. Sube un script:
   ```python
   # Ejemplo: hello.py
   print("¡Hola, administradores!")
   for i in range(3):
       print(f"Iteración {i+1}")
   ```
3. Selecciona el script en la lista y haz clic en "Ejecutar". La salida aparecerá en el panel inferior:
   ```
   ¡Hola, administradores!
   Iteración 1
   Iteración 2
   Iteración 3
   Éxito
   ```

## 📐 Diseño Técnico

### Arquitectura

- **Cliente**: Aplicación Python con interfaz gráfica basada en Tkinter y estilizada con ttkbootstrap, ejecutada localmente
- **Servidor**: Base de datos MySQL alojada en Railway, accesible mediante mysql-connector-python

### Estructura de la Base de Datos

| Tabla | Descripción |
|-------|-------------|
| scripts | Almacena scripts: id, filename, content, upload_date, modified_date, downloads, last_execution, execution_count, uploaded_by |
| users | Gestiona usuarios: id, username, password (hash), role, approved |
| execution_logs | Registra ejecuciones: id, script_id, username, execution_date, success |

### Seguridad

- **Cifrado**: Contraseñas almacenadas como hash SHA-256:
  ```python
  def hash_password(self, password):
      return hashlib.sha256(password.encode()).hexdigest()
  ```

- **Verificación**: Detección de comandos peligrosos antes de ejecutar scripts:
  ```python
  def verificar_contenido_seguro(self, contenido):
      peligrosos = ['os.remove', 'shutil.rmtree', 'sys.exit', 'Remove-Item']
      return not any(cmd in contenido for cmd in peligrosos)
  ```

## 📊 Pruebas Realizadas

- **Funcionales**: 
  - Subida/descarga de 100 scripts
  - Ejecución de 50 scripts (25 Python, 25 PowerShell)
  - Cambio de idioma 20 veces

- **Rendimiento**: 
  - Carga de 100 scripts optimizada de 2.5s a 1.5s con threading

## 🚧 Limitaciones

- Resaltado de sintaxis básico (solo palabras clave)
- Dependencia de PowerShell en Windows

## 🔮 Líneas Futuras

- Soporte para Bash y otros lenguajes de scripting
- Resaltado avanzado con Pygments
- Ejecución en la nube para mayor portabilidad

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Sigue estos pasos:

1. Haz un Fork del proyecto
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Haz Commit: `git commit -m 'Add new feature'`
4. Haz Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

## 📫 Contacto

- Pedro Miguel Morales Calderín: email@example.com
- Eloy Ramírez Revuelta: email@example.com

---

*"Facilitando la vida de los administradores de sistemas, un script a la vez."*

Creado con ❤️ por Pedro Miguel Morales Calderín y Eloy Ramírez Revuelta - ¡Dale una ⭐ si te gusta!
