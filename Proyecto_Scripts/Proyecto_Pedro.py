import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from ttkbootstrap import Style
import os

class AppCompartirScripts:
    def __init__(self, master):
        self.master = master
        self.master.title("Plataforma de Scripts Colaborativos")
        self.master.geometry("1000x700")
        
        # Configurar estilo visual
        self.style = Style(theme='darkly')
        self.style.configure('Titulo.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('Contador.TLabel', font=('Helvetica', 10, 'italic'))
        
        # Configuración de la base de datos MySQL
        self.db_config = {
            'host': '192.168.192.205',
            'user': 'root',          # Cambiar por tu usuario
            'password': 'password',  # Cambiar por tu contraseña
            'database': 'scripts_db'
        }
        
        # Conectar a MySQL
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            
            # Crear tabla si no existe
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS scripts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    content LONGTEXT NOT NULL,
                    upload_date DATETIME NOT NULL,
                    downloads INT DEFAULT 0
                )
            """)
            self.conn.commit()
        except Error as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a MySQL: {str(e)}")
            self.master.destroy()
        
        # Interfaz gráfica
        self.crear_interfaz()
        self.actualizar_contador()
        self.cargar_scripts()
        
    def crear_interfaz(self):
        # Marco principal
        marco_principal = ttk.Frame(self.master)
        marco_principal.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Cabecera
        cabecera = ttk.Frame(marco_principal)
        cabecera.pack(fill='x', pady=(0, 20))
        
        ttk.Label(cabecera, text="📂 Plataforma de Scripts Compartidos", 
                style='Titulo.TLabel').pack(side='left')
        
        # Panel izquierdo
        panel_izquierdo = ttk.Frame(marco_principal)
        panel_izquierdo.pack(side='left', fill='y', padx=(0, 15))
        
        # Botón de subida
        ttk.Button(panel_izquierdo, text="📤 Subir Nuevo Script", 
                 command=self.subir_script,
                 style='success.TButton').pack(fill='x', pady=(0, 15))
        
        # Lista de scripts
        self.lista_scripts = tk.Listbox(panel_izquierdo, width=35, height=25,
                                       selectbackground='#e1f5fe',
                                       selectforeground='#01579b',
                                       font=('Arial', 10))
        self.lista_scripts.pack(fill='both', expand=True)
        self.lista_scripts.bind('<Double-1>', self.mostrar_contenido)
        
        # Panel derecho
        panel_derecho = ttk.Frame(marco_principal)
        panel_derecho.pack(side='right', fill='both', expand=True)
        
        # Título del script
        self.titulo_script = ttk.Label(panel_derecho, 
                                      font=('Helvetica', 12, 'bold'),
                                      foreground='#2c3e50')
        self.titulo_script.pack(pady=(0, 10))
        
        # Área de contenido
        self.contenido_script = scrolledtext.ScrolledText(panel_derecho,
                                                         wrap=tk.WORD,
                                                         font=('Consolas', 10),
                                                         padx=10,
                                                         pady=10,
                                                         bg='#f5f6fa',
                                                         insertbackground='#2d3436')
        self.contenido_script.pack(fill='both', expand=True)
        
        # Pie de página
        pie_pagina = ttk.Frame(self.master)
        pie_pagina.pack(fill='x', pady=(10, 0))
        
        # Contador de días
        self.contador = ttk.Label(pie_pagina, style='Contador.TLabel')
        self.contador.pack(side='left', padx=20)
        
        # Créditos
        ttk.Label(pie_pagina, text="Creado Por PedroMiguel 👨💻", 
                 style='Contador.TLabel').pack(side='right', padx=20)
        
    def calcular_dias_faltantes(self):
        hoy = datetime.now()
        fecha_objetivo = datetime(2025, 2, 14)
        return max((fecha_objetivo - hoy).days, 0)
    
    def actualizar_contador(self):
        self.contador.config(text=f"⏳ Días hasta 14/02/2025: {self.calcular_dias_faltantes()} días")
        self.master.after(86400000, self.actualizar_contador)  # Actualizar cada 24h
        
    def subir_script(self):
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo para subir",
            filetypes=[("Archivos Python", "*.py"), ("Todos los archivos", "*.*")]
        )
        
        if ruta_archivo:
            try:
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                nombre_archivo = os.path.basename(ruta_archivo)
                
                query = """
                    INSERT INTO scripts 
                    (filename, content, upload_date)
                    VALUES (%s, %s, %s)
                """
                valores = (nombre_archivo, contenido, datetime.now())
                
                self.cursor.execute(query, valores)
                self.conn.commit()
                self.cargar_scripts()
                messagebox.showinfo("Éxito", "Script subido correctamente ✅")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al subir: {str(e)} ❌")
                self.conn.rollback()

    def cargar_scripts(self):
        self.lista_scripts.delete(0, tk.END)
        try:
            self.cursor.execute("""
                SELECT id, filename, upload_date 
                FROM scripts 
                ORDER BY upload_date DESC
            """)
            
            for (script_id, filename, _) in self.cursor:
                self.lista_scripts.insert(tk.END, f"📄 {filename}")
                
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar scripts: {str(e)} ❌")

    def mostrar_contenido(self, event):
        seleccion = self.lista_scripts.curselection()
        if seleccion:
            try:
                self.cursor.execute("""
                    SELECT filename, content 
                    FROM scripts 
                    ORDER BY upload_date DESC
                    LIMIT 1 OFFSET %s
                """, (seleccion[0],))
                
                filename, contenido = self.cursor.fetchone()
                self.titulo_script.config(text=f"Contenido de: {filename}")
                self.contenido_script.delete(1.0, tk.END)
                self.contenido_script.insert(tk.END, contenido)
                
            except Error as e:
                messagebox.showerror("Error", f"Error al cargar contenido: {str(e)} ❌")

    def on_close(self):
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
        self.master.destroy()

if __name__ == "__main__":
    ventana = tk.Tk()
    app = AppCompartirScripts(ventana)
    ventana.protocol("WM_DELETE_WINDOW", app.on_close)
    ventana.mainloop()