# 🚀 Plataforma de Scripts Colaborativos

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/tu-usuario/project_scripts.svg)](https://github.com/tu-usuario/project_scripts/stargazers)

Aplicación colaborativa para compartir y gestionar scripts de programación con almacenamiento en MySQL.

![Captura de pantalla de la aplicación](screenshot.png)

## ✨ Características principales

- 📤 Subida de scripts con almacenamiento en base de datos
- 🔍 Visualización de código con scroll integrado
- 📅 Contador de días hasta fecha objetivo
- 🎨 Interfaz moderna con tema oscuro
- 🔄 Sistema de base de datos MySQL integrado
- 📦 Gestión de dependencias con pip

## ⚙️ Requisitos

- Python 3.8+
- MySQL Server 5.7+
- pip para gestión de paquetes

## 🛠️ Instalación

1. Clonar repositorio:
```bash
git clone https://github.com/tu-usuario/project_scripts.git
cd project_scripts
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 🔧 Configuración

1. Crear base de datos MySQL:
```sql
CREATE DATABASE scripts_db;
USE scripts_db;
```

2. Configurar credenciales en `app.py`:
```python
self.db_config = {
    'host': 'localhost',
    'user': 'tu_usuario',    # <-- Cambiar aquí
    'password': 'tu_contraseña',  # <-- Cambiar aquí
    'database': 'scripts_db'
}
```

## 🖥️ Uso

Ejecutar la aplicación:
```bash
python app.py
```

- **Subir script**: Botón "📤 Subir Nuevo Script"
- **Ver contenido**: Doble click en cualquier script
- **Buscar**: Ctrl+F en el área de código

## 📄 Estructura del Proyecto
```
project_scripts/
├── app.py            # Código principal
├── README.md         # Documentación
├── requirements.txt  # Dependencias
└── screenshot.png    # Captura de pantalla
```

## 📜 Licencia
Este proyecto está bajo licencia [MIT](LICENSE).

## 👥 Contribuciones
Las contribuciones son bienvenidas! Por favor:
1. Haz un Fork del proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Haz Commit de tus cambios (`git commit -m 'Add new feature'`)
4. Haz Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

Creado con ❤️ por [PedroMiguel](https://github.com/tu-usuario) - ¡Dale una ⭐ si te gusta!
