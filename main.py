import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from ttkbootstrap import Style
import os
import subprocess
import sys
import tempfile
import hashlib
import threading
import keyword

class AppCompartirScripts:
    def __init__(self, master):
        self.master = master
        self.master.title("Plataforma de Scripts Colaborativos")
        self.master.geometry("1200x800")
        
        self.style = Style(theme='darkly')
        self.style.configure('Titulo.TLabel', font=('Helvetica', 18, 'bold'), foreground='#00bcd4')
        self.style.configure('Panel.TFrame', background='#2d3e50')
        self.style.configure('Contador.TLabel', font=('Arial', 9, 'italic'), foreground='#95a5a6')
        
        self.db_config = {
            'host': 'roundhouse.proxy.rlwy.net',
            'port': 15111,
            'user': 'root',
            'password': 'yLGTWKFUCjGcDQiuCjWMrnObyAjHERra',
            'database': 'railway',
            'ssl_disabled': True
        }
        
        self.current_user = None
        self.language = 'es'
        self.texts = {
            'es': {
                'title': 'Plataforma de Scripts Colaborativos',
                'login': 'Iniciar Sesión',
                'register': 'Registro',
                'scripts': 'Scripts',
                'admin': 'Administración',
                'history': 'Historial',
                'execute': 'Ejecutar',
                'stats': 'Estadísticas',
                'refresh': 'Actualizar',
                'upload': 'Subir Script',
                'download': 'Descargar',
                'delete_all': 'Eliminar Todo',
                'approve': 'Aprobar',
                'delete_user': 'Eliminar',
                'export': 'Exportar',
                'save': 'Guardar',
                'preview': 'Vista Previa',
                'theme': 'Cambiar Tema',
                'language': 'Cambiar Idioma',
                'logout': 'Cerrar Sesión',
                'status_ready': 'Listo',
                'status_loading': 'Cargando...',
                'warning': 'Advertencia',
                'complete_fields': 'Complete todos los campos (Usuario: mín. 3 caracteres, Contraseña: mín. 6 caracteres)',
                'pending_approval': 'Cuenta pendiente de aprobación',
                'invalid_credentials': 'Credenciales incorrectas',
                'success': 'Éxito',
                'register_success': 'Registro exitoso. Espere aprobación.',
                'script_uploaded': 'Script subido correctamente',
                'script_downloaded': 'Script descargado correctamente',
                'script_saved': 'Script guardado correctamente',
                'script_deleted': 'Scripts eliminados',
                'user_approved': 'Usuario aprobado: {username}',
                'user_deleted': 'Usuario eliminado: {username}',
                'history_exported': 'Historial exportado correctamente',
                'no_script': 'No hay script para ejecutar',
                'select_script': 'Seleccione un script primero',
                'unsafe_script': 'El script contiene comandos potencialmente peligrosos. ¿Ejecutar de todos modos?',
                'executing': 'Ya hay un script en ejecución',
                'empty_script': 'El script está vacío',
                'select_user': 'Seleccione un usuario',
                'confirm_delete_scripts': '¿Eliminar todos los scripts?',
                'confirm_delete_user': '¿Eliminar usuario {username}?',
                'toggle_role': 'Cambiar Rol'
            },
            'en': {
                'title': 'Collaborative Scripts Platform',
                'login': 'Log In',
                'register': 'Register',
                'scripts': 'Scripts',
                'admin': 'Administration',
                'history': 'History',
                'execute': 'Execute',
                'stats': 'Statistics',
                'refresh': 'Refresh',
                'upload': 'Upload Script',
                'download': 'Download',
                'delete_all': 'Delete All',
                'approve': 'Approve',
                'delete_user': 'Delete',
                'export': 'Export',
                'save': 'Save',
                'preview': 'Preview',
                'theme': 'Change Theme',
                'language': 'Change Language',
                'logout': 'Log Out',
                'status_ready': 'Ready',
                'status_loading': 'Loading...',
                'warning': 'Warning',
                'complete_fields': 'Complete all fields (Username: min. 3 characters, Password: min. 6 characters)',
                'pending_approval': 'Account pending approval',
                'invalid_credentials': 'Invalid credentials',
                'success': 'Success',
                'register_success': 'Registration successful. Wait for approval.',
                'script_uploaded': 'Script uploaded successfully',
                'script_downloaded': 'Script downloaded successfully',
                'script_saved': 'Script saved successfully',
                'script_deleted': 'Scripts deleted',
                'user_approved': 'User approved: {username}',
                'user_deleted': 'User deleted: {username}',
                'history_exported': 'History exported successfully',
                'no_script': 'No script to execute',
                'select_script': 'Select a script first',
                'unsafe_script': 'The script contains potentially dangerous commands. Execute anyway?',
                'executing': 'A script is already executing',
                'empty_script': 'The script is empty',
                'select_user': 'Select a user',
                'confirm_delete_scripts': 'Delete all scripts?',
                'confirm_delete_user': 'Delete user {username}?',
                'toggle_role': 'Toggle Role'
            }
        }
        
        self.is_executing = False
        self.conectar_db()
        self.mostrar_login()

    def conectar_db(self):
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS scripts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    content LONGTEXT NOT NULL,
                    upload_date DATETIME NOT NULL,
                    modified_date DATETIME,
                    downloads INT DEFAULT 0,
                    last_execution DATETIME,
                    execution_count INT DEFAULT 0,
                    uploaded_by VARCHAR(255)
                )
            """)
            
            for col in [
                "ALTER TABLE scripts ADD COLUMN uploaded_by VARCHAR(255)",
                "ALTER TABLE scripts ADD COLUMN execution_count INT DEFAULT 0",
                "ALTER TABLE scripts ADD COLUMN last_execution DATETIME",
                "ALTER TABLE scripts ADD COLUMN modified_date DATETIME"
            ]:
                try:
                    self.cursor.execute(col)
                except Error as e:
                    if e.errno != 1060: raise
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('admin', 'user') DEFAULT 'user',
                    approved BOOLEAN DEFAULT FALSE
                )
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    script_id INT,
                    username VARCHAR(255),
                    execution_date DATETIME,
                    success BOOLEAN,
                    FOREIGN KEY (script_id) REFERENCES scripts(id)
                )
            """)
            
            self.cursor.execute("SELECT * FROM users WHERE username = 'pedro'")
            if not self.cursor.fetchone():
                hashed_password = self.hash_password("admin123")
                self.cursor.execute("""
                    INSERT INTO users (username, password, role, approved)
                    VALUES (%s, %s, %s, %s)
                """, ("pedro", hashed_password, "admin", True))
            
            self.conn.commit()
        except Error as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a MySQL: {str(e)}")
            self.master.destroy()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def limpiar_ventana(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpiar_ventana()
        self.master.title(self.texts[self.language]['title'])
        login_frame = ttk.Frame(self.master, padding=20)
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Label(login_frame, text=self.texts[self.language]['login'], style='Titulo.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(login_frame, text="Usuario:").grid(row=1, column=0, pady=5)
        self.login_user = ttk.Entry(login_frame)
        self.login_user.grid(row=1, column=1, pady=5)
        ttk.Label(login_frame, text="Contraseña:").grid(row=2, column=0, pady=5)
        self.login_pass = ttk.Entry(login_frame, show="*")
        self.login_pass.grid(row=2, column=1, pady=5)
        
        ttk.Button(login_frame, text=self.texts[self.language]['login'], style='success.TButton',
                  command=self.verificar_login).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(login_frame, text=self.texts[self.language]['register'], style='info.TButton',
                  command=self.mostrar_registro).grid(row=4, column=0, columnspan=2)

    def mostrar_registro(self):
        self.limpiar_ventana()
        self.master.title(self.texts[self.language]['title'])
        registro_frame = ttk.Frame(self.master, padding=20)
        registro_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Label(registro_frame, text=self.texts[self.language]['register'], style='Titulo.TLabel').grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(registro_frame, text="Usuario:").grid(row=1, column=0, pady=5)
        self.reg_user = ttk.Entry(registro_frame)
        self.reg_user.grid(row=1, column=1, pady=5)
        ttk.Label(registro_frame, text="Contraseña:").grid(row=2, column=0, pady=5)
        self.reg_pass = ttk.Entry(registro_frame, show="*")
        self.reg_pass.grid(row=2, column=1, pady=5)
        
        ttk.Button(registro_frame, text=self.texts[self.language]['register'], style='success.TButton',
                  command=self.registrar_usuario).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(registro_frame, text="Volver", style='warning.TButton',
                  command=self.mostrar_login).grid(row=4, column=0, columnspan=2)

    def verificar_login(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get()
        
        if not all([username, password]) or len(username) < 3 or len(password) < 6:
            messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['complete_fields'])
            return
            
        try:
            self.cursor.execute("SELECT id, username, password, role, approved FROM users WHERE username = %s", (username,))
            user = self.cursor.fetchone()
            if user and user[2] == self.hash_password(password):
                if user[4]:
                    self.current_user = {'id': user[0], 'username': user[1], 'role': user[3]}
                    self.crear_interfaz_moderna()
                else:
                    messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['pending_approval'])
            else:
                messagebox.showerror("Error", self.texts[self.language]['invalid_credentials'])
        except Error as e:
            messagebox.showerror("Error", f"Error en login: {str(e)}")

    def registrar_usuario(self):
        username = self.reg_user.get().strip()
        password = self.reg_pass.get()
        
        if not all([username, password]) or len(username) < 3 or len(password) < 6:
            messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['complete_fields'])
            return
            
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                              (username, self.hash_password(password)))
            self.conn.commit()
            messagebox.showinfo(self.texts[self.language]['success'], self.texts[self.language]['register_success'])
            self.mostrar_login()
        except Error as e:
            messagebox.showerror("Error", f"Error al registrar: {str(e)}")

    def crear_interfaz_moderna(self):
        self.limpiar_ventana()
        self.master.title(self.texts[self.language]['title'])
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text=self.texts[self.language]['scripts'])
        
        self.admin_tab = None
        if self.current_user['role'] == 'admin':
            self.admin_tab = ttk.Frame(self.notebook)
            self.notebook.add(self.admin_tab, text=self.texts[self.language]['admin'])
            self.crear_panel_admin(self.admin_tab)
        
        history_tab = ttk.Frame(self.notebook)
        self.notebook.add(history_tab, text=self.texts[self.language]['history'])
        self.crear_panel_historial(history_tab)
        
        left_panel = ttk.Frame(main_tab, width=300, style='Panel.TFrame')
        left_panel.pack(side='left', fill='y', padx=10, pady=10)
        self.crear_panel_scripts(left_panel)
        
        center_panel = ttk.Frame(main_tab)
        center_panel.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.crear_panel_ejecucion(center_panel)
        
        top_bar = ttk.Frame(self.master)
        top_bar.pack(fill='x', pady=5)
        self.theme_btn = ttk.Button(top_bar, text=self.texts[self.language]['theme'], command=self.toggle_theme)
        self.theme_btn.pack(side='left', padx=5)
        self.lang_btn = ttk.Button(top_bar, text=self.texts[self.language]['language'], command=self.toggle_language)
        self.lang_btn.pack(side='left', padx=5)
        self.logout_btn = ttk.Button(top_bar, text=self.texts[self.language]['logout'], style='danger.TButton', command=self.cerrar_sesion)
        self.logout_btn.pack(side='right', padx=5)
        
        self.status_bar = ttk.Label(self.master, text=self.texts[self.language]['status_ready'], style='Contador.TLabel')
        self.status_bar.pack(fill='x', side='bottom', pady=5)
        
        self.actualizar_fecha()
        self.cargar_scripts_async()

    def toggle_theme(self):
        current_theme = self.style.theme.name
        self.style.theme_use('flatly' if current_theme == 'darkly' else 'darkly')

    def toggle_language(self):
        self.language = 'en' if self.language == 'es' else 'es'
        self.update_ui_texts()

    def update_ui_texts(self):
        self.master.title(self.texts[self.language]['title'])
        self.notebook.tab(0, text=self.texts[self.language]['scripts'])
        tab_index = 1
        if self.current_user['role'] == 'admin':
            self.notebook.tab(tab_index, text=self.texts[self.language]['admin'])
            tab_index += 1
        self.notebook.tab(tab_index, text=self.texts[self.language]['history'])
        
        self.theme_btn.config(text=self.texts[self.language]['theme'])
        self.lang_btn.config(text=self.texts[self.language]['language'])
        self.logout_btn.config(text=self.texts[self.language]['logout'])
        self.status_bar.config(text=self.texts[self.language]['status_ready'])
        
        # Panel de scripts
        self.upload_btn.config(text=self.texts[self.language]['upload'])
        self.download_btn.config(text=self.texts[self.language]['download'])
        self.preview_btn.config(text=self.texts[self.language]['preview'])
        if self.current_user['role'] == 'admin':
            self.delete_all_btn.config(text=self.texts[self.language]['delete_all'])
        self.search_btn.config(text="Buscar" if self.language == 'es' else "Search")
        
        # Panel de ejecución
        self.execute_btn.config(text=self.texts[self.language]['execute'])
        self.stats_btn.config(text=self.texts[self.language]['stats'])
        self.save_btn.config(text=self.texts[self.language]['save'])
        self.refresh_scripts_btn.config(text=self.texts[self.language]['refresh'])
        
        # Panel de historial
        self.refresh_history_btn.config(text=self.texts[self.language]['refresh'])
        self.export_btn.config(text=self.texts[self.language]['export'])
        
        # Panel de administración (si existe)
        if self.current_user['role'] == 'admin':
            self.approve_btn.config(text=self.texts[self.language]['approve'])
            self.delete_user_btn.config(text=self.texts[self.language]['delete_user'])
            self.refresh_admin_btn.config(text=self.texts[self.language]['refresh'])
            self.toggle_role_btn.config(text=self.texts[self.language]['toggle_role'])

    def cerrar_sesion(self):
        self.current_user = None
        self.mostrar_login()

    def crear_panel_admin(self, parent):
        self.panel_admin = parent
        ttk.Label(parent, text=self.texts[self.language]['admin'], style='Titulo.TLabel').pack(pady=10)
        
        tree = ttk.Treeview(parent, columns=('Username', 'Approved', 'Role'), show='headings')
        tree.heading('Username', text='Usuario', anchor='center')
        tree.heading('Approved', text='Aprobado', anchor='center')
        tree.heading('Role', text='Rol', anchor='center')
        tree.column('Username', anchor='center')
        tree.column('Approved', anchor='center')
        tree.column('Role', anchor='center')
        tree.pack(fill='both', expand=True, padx=10)
        self.admin_tree = tree
        
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', pady=10)
        
        self.approve_btn = ttk.Button(btn_frame, text=self.texts[self.language]['approve'], style='success.TButton',
                                    command=self.aprobar_usuario)
        self.approve_btn.pack(side='left', padx=5)
        self.delete_user_btn = ttk.Button(btn_frame, text=self.texts[self.language]['delete_user'], style='danger.TButton',
                                        command=self.eliminar_usuario)
        self.delete_user_btn.pack(side='left', padx=5)
        self.toggle_role_btn = ttk.Button(btn_frame, text=self.texts[self.language]['toggle_role'], style='primary.TButton',
                                        command=self.toggle_role)
        self.toggle_role_btn.pack(side='left', padx=5)
        self.refresh_admin_btn = ttk.Button(btn_frame, text=self.texts[self.language]['refresh'], style='warning.TButton',
                                          command=self.cargar_usuarios_admin)
        self.refresh_admin_btn.pack(side='left', padx=5)
        
        self.cargar_usuarios_admin()

    def cargar_usuarios_admin(self):
        for item in self.admin_tree.get_children():
            self.admin_tree.delete(item)
        try:
            self.cursor.execute("SELECT username, approved, role FROM users WHERE username != %s", (self.current_user['username'],))
            for username, approved, role in self.cursor:
                self.admin_tree.insert('', 'end', values=(username, 'Sí' if approved else 'No', role))
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {str(e)}")

    def aprobar_usuario(self):
        seleccion = self.admin_tree.selection()
        if not seleccion:
            messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['select_user'])
            return
        username = self.admin_tree.item(seleccion[0])['values'][0]
        try:
            self.cursor.execute("UPDATE users SET approved = TRUE WHERE username = %s", (username,))
            self.conn.commit()
            self.cargar_usuarios_admin()
            messagebox.showinfo(self.texts[self.language]['success'], self.texts[self.language]['user_approved'].format(username=username))
        except Error as e:
            messagebox.showerror("Error", f"Error al aprobar usuario: {str(e)}")

    def eliminar_usuario(self):
        seleccion = self.admin_tree.selection()
        if not seleccion:
            messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['select_user'])
            return
        username = self.admin_tree.item(seleccion[0])['values'][0]
        if messagebox.askyesno("Confirmar", self.texts[self.language]['confirm_delete_user'].format(username=username)):
            try:
                self.cursor.execute("DELETE FROM users WHERE username = %s", (username,))
                self.conn.commit()
                self.cargar_usuarios_admin()
                messagebox.showinfo(self.texts[self.language]['success'], self.texts[self.language]['user_deleted'].format(username=username))
            except Error as e:
                messagebox.showerror("Error", f"Error al eliminar usuario: {str(e)}")

    def toggle_role(self):
        seleccion = self.admin_tree.selection()
        if not seleccion:
            messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['select_user'])
            return
        username = self.admin_tree.item(seleccion[0])['values'][0]
        current_role = self.admin_tree.item(seleccion[0])['values'][2]
        new_role = 'user' if current_role == 'admin' else 'admin'
        try:
            self.cursor.execute("UPDATE users SET role = %s WHERE username = %s", (new_role, username))
            self.conn.commit()
            self.cargar_usuarios_admin()
            messagebox.showinfo(self.texts[self.language]['success'], f"Rol cambiado a {new_role} para {username}")
        except Error as e:
            messagebox.showerror("Error", f"Error al cambiar rol: {str(e)}")

    def crear_panel_historial(self, parent):
        self.panel_historial = parent
        ttk.Label(parent, text=self.texts[self.language]['history'], style='Titulo.TLabel').pack(pady=10)
        
        self.history_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, font=('Consolas', 10),
                                                    bg='#2c3e50', fg='#bdc3c7', height=20)
        self.history_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', pady=5)
        self.refresh_history_btn = ttk.Button(btn_frame, text=self.texts[self.language]['refresh'], style='warning.TButton',
                                            command=self.cargar_historial)
        self.refresh_history_btn.pack(side='left', padx=5)
        self.export_btn = ttk.Button(btn_frame, text=self.texts[self.language]['export'], style='info.TButton',
                                   command=self.exportar_historial)
        self.export_btn.pack(side='left', padx=5)
        self.cargar_historial()

    def cargar_historial(self):
        self.history_text.delete('1.0', tk.END)
        try:
            self.cursor.execute("""
                SELECT s.filename, e.username, e.execution_date, e.success 
                FROM execution_logs e 
                JOIN scripts s ON e.script_id = s.id 
                WHERE e.username = %s 
                ORDER BY e.execution_date DESC
            """, (self.current_user['username'],))
            for filename, username, date, success in self.cursor:
                status = "Éxito" if success else "Fallo" if self.language == 'es' else "Success" if success else "Failure"
                self.history_text.insert(tk.END, f"{date.strftime('%d/%m/%Y %H:%M:%S')} - {filename} por {username}: {status}\n")
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar historial: {str(e)}")

    def exportar_historial(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                                               initialfile=f"historial_{self.current_user['username']}.txt")
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(self.history_text.get('1.0', tk.END))
            messagebox.showinfo(self.texts[self.language]['success'], self.texts[self.language]['history_exported'])

    def crear_panel_scripts(self, parent):
        self.panel_scripts = parent
        header = ttk.Frame(parent)
        header.pack(fill='x', pady=5)
        
        ttk.Label(header, text=f"{self.texts[self.language]['scripts']} - {self.current_user['username']}", style='Titulo.TLabel').pack(side='left')
        
        search_frame = ttk.Frame(header)
        search_frame.pack(side='right')
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', padx=5)
        self.search_btn = ttk.Button(search_frame, text="Buscar" if self.language == 'es' else "Search", style='info.TButton', command=self.buscar_scripts)
        self.search_btn.pack(side='left')
        
        list_container = ttk.Frame(parent)
        list_container.pack(fill='both', expand=True)
        
        self.lista_scripts = tk.Listbox(list_container, bg='#34495e', fg='#ecf0f1', 
                                      selectbackground='#2980b9', font=('Arial', 11))
        scroll = ttk.Scrollbar(list_container, orient='vertical', command=self.lista_scripts.yview)
        self.lista_scripts.configure(yscrollcommand=scroll.set)
        self.lista_scripts.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        self.lista_scripts.bind('<Double-1>', self.mostrar_contenido)
        
        self.upload_btn = ttk.Button(parent, text=self.texts[self.language]['upload'], style='success.TButton',
                                   command=self.subir_script)
        self.upload_btn.pack(fill='x', pady=5)
        self.download_btn = ttk.Button(parent, text=self.texts[self.language]['download'], style='info.TButton',
                                     command=self.descargar_script)
        self.download_btn.pack(fill='x', pady=5)
        self.preview_btn = ttk.Button(parent, text=self.texts[self.language]['preview'], style='secondary.TButton',
                                    command=self.vista_previa)
        self.preview_btn.pack(fill='x', pady=5)
        
        if self.current_user['role'] == 'admin':
            self.delete_all_btn = ttk.Button(parent, text=self.texts[self.language]['delete_all'], style='danger.TButton',
                                           command=self.eliminar_todos_scripts)
            self.delete_all_btn.pack(fill='x', pady=5)
        
        pie_pagina = ttk.Frame(parent)
        pie_pagina.pack(fill='x', pady=(10, 0))
        self.fecha_label = ttk.Label(pie_pagina, text="Cargando...", style='Contador.TLabel')
        self.fecha_label.pack(side='left', padx=10)
        ttk.Label(pie_pagina, text="Creado Por PedroMiguel", style='Contador.TLabel').pack(side='right', padx=10)

    def crear_panel_ejecucion(self, parent):
        self.panel_ejecucion = parent
        editor_frame = ttk.Frame(parent)
        editor_frame.pack(fill='both', expand=True, pady=5)
        
        self.contenido_script = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD,
                                                        font=('Consolas', 10), bg='#2c3e50',
                                                        fg='#bdc3c7', insertbackground='white')
        self.contenido_script.pack(fill='both', expand=True)
        self.configurar_resaltado_sintaxis()
        
        ejecucion_frame = ttk.Frame(parent)
        ejecucion_frame.pack(fill='x', pady=10)
        
        btn_frame = ttk.Frame(ejecucion_frame)
        btn_frame.pack(fill='x', pady=5)
        
        self.execute_btn = ttk.Button(btn_frame, text=self.texts[self.language]['execute'], style='success.TButton',
                                    command=self.ejecutar_script)
        self.execute_btn.pack(side='left', padx=5)
        self.stats_btn = ttk.Button(btn_frame, text=self.texts[self.language]['stats'], style='info.TButton',
                                  command=self.mostrar_estadisticas)
        self.stats_btn.pack(side='left', padx=5)
        self.save_btn = ttk.Button(btn_frame, text=self.texts[self.language]['save'], style='primary.TButton',
                                 command=self.guardar_script)
        self.save_btn.pack(side='left', padx=5)
        self.refresh_scripts_btn = ttk.Button(btn_frame, text=self.texts[self.language]['refresh'], style='warning.TButton',
                                            command=self.cargar_scripts_async)
        self.refresh_scripts_btn.pack(side='right', padx=5)
        
        self.salida_ejecucion = scrolledtext.ScrolledText(ejecucion_frame, wrap=tk.WORD,
                                                        font=('Consolas', 9), bg='#1a1a1a',
                                                        fg='#ffffff', height=10)
        self.salida_ejecucion.pack(fill='both', expand=True, pady=5)

    def configurar_resaltado_sintaxis(self):
        self.contenido_script.tag_configure('keyword', foreground='#ff5555')
        self.contenido_script.tag_configure('powershell_cmd', foreground='#55ff55')
        self.contenido_script.bind('<KeyRelease>', self.resaltar_sintaxis)

    def resaltar_sintaxis(self, event=None):
        contenido = self.contenido_script.get('1.0', tk.END)
        self.contenido_script.mark_set('range_start', '1.0')
        self.contenido_script.tag_remove('keyword', '1.0', tk.END)
        self.contenido_script.tag_remove('powershell_cmd', '1.0', tk.END)
        
        for word in keyword.kwlist:
            start_pos = '1.0'
            while True:
                start_pos = self.contenido_script.search(r'\b' + word + r'\b', start_pos, tk.END)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(word)}c"
                self.contenido_script.tag_add('keyword', start_pos, end_pos)
                start_pos = end_pos
        
        powershell_cmds = ['Write-Host', 'Get-Item', 'Set-Item', 'Remove-Item']
        for cmd in powershell_cmds:
            start_pos = '1.0'
            while True:
                start_pos = self.contenido_script.search(cmd, start_pos, tk.END)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(cmd)}c"
                self.contenido_script.tag_add('powershell_cmd', start_pos, end_pos)
                start_pos = end_pos

    def subir_script(self):
        ruta = filedialog.askopenfilename(filetypes=[("Scripts", "*.py *.ps1"), ("Todos", "*.*")])
        if ruta:
            try:
                with open(ruta, 'r', encoding='utf-8-sig') as f:
                    contenido = f.read()
                nombre = os.path.basename(ruta)
                self.cursor.execute("""
                    INSERT INTO scripts (filename, content, upload_date, uploaded_by)
                    VALUES (%s, %s, %s, %s)
                """, (nombre, contenido, datetime.now(), self.current_user['username']))
                self.conn.commit()
                self.cargar_scripts_async()
                messagebox.showinfo(self.texts[self.language]['success'], self.texts[self.language]['script_uploaded'])
            except Error as e:
                messagebox.showerror("Error", f"Error al subir: {str(e)}")
                self.conn.rollback()

    def cargar_scripts_async(self):
        self.status_bar.config(text=self.texts[self.language]['status_loading'])
        threading.Thread(target=self.cargar_scripts, daemon=True).start()

    def cargar_scripts(self):
        self.lista_scripts.delete(0, tk.END)
        try:
            self.cursor.execute("""
                SELECT filename, COALESCE(uploaded_by, 'Desconocido') as uploaded_by 
                FROM scripts 
                ORDER BY upload_date DESC
            """)
            for (filename, uploaded_by) in self.cursor:
                self.lista_scripts.insert(tk.END, f"{filename} (por {uploaded_by})")
            self.status_bar.config(text=self.texts[self.language]['status_ready'])
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar: {str(e)}")

    def mostrar_contenido(self, event):
        seleccion = self.lista_scripts.curselection()
        if seleccion:
            try:
                self.cursor.execute("SELECT content FROM scripts ORDER BY upload_date DESC LIMIT 1 OFFSET %s", (seleccion[0],))
                contenido = self.cursor.fetchone()[0]
                self.contenido_script.delete(1.0, tk.END)
                self.contenido_script.insert(tk.END, contenido)
                self.resaltar_sintaxis()
            except Error as e:
                messagebox.showerror("Error", f"Error al mostrar: {str(e)}")

    def vista_previa(self):
        seleccion = self.lista_scripts.curselection()
        if not seleccion:
            messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['select_script'])
            return
        try:
            self.cursor.execute("SELECT filename, content FROM scripts ORDER BY upload_date DESC LIMIT 1 OFFSET %s", (seleccion[0],))
            filename, content = self.cursor.fetchone()
            preview_window = tk.Toplevel(self.master)
            preview_window.title(f"Vista previa: {filename}")
            preview_window.geometry("600x400")
            text = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD, font=('Consolas', 10))
            text.insert(tk.END, content)
            text.config(state='disabled')
            text.pack(fill='both', expand=True)
        except Error as e:
            messagebox.showerror("Error", f"Error en vista previa: {str(e)}")

    def descargar_script(self):
        seleccion = self.lista_scripts.curselection()
        if not seleccion:
            messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['select_script'])
            return
        try:
            self.cursor.execute("SELECT filename, content FROM scripts ORDER BY upload_date DESC LIMIT 1 OFFSET %s", (seleccion[0],))
            filename, content = self.cursor.fetchone()
            save_path = filedialog.asksaveasfilename(defaultextension=os.path.splitext(filename)[1],
                                                   initialfile=filename,
                                                   filetypes=[("Scripts", "*.py *.ps1"), ("Todos", "*.*")])
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.cursor.execute("UPDATE scripts SET downloads = downloads + 1 WHERE filename = %s", (filename,))
                self.conn.commit()
                messagebox.showinfo(self.texts[self.language]['success'], self.texts[self.language]['script_downloaded'])
        except Error as e:
            messagebox.showerror("Error", f"Error al descargar: {str(e)}")

    def guardar_script(self):
        seleccion = self.lista_scripts.curselection()
        if not seleccion:
            messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['select_script'])
            return
        contenido = self.contenido_script.get("1.0", tk.END).strip()
        if not contenido:
            messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['empty_script'])
            return
        try:
            self.cursor.execute("SELECT id, filename FROM scripts ORDER BY upload_date DESC LIMIT 1 OFFSET %s", (seleccion[0],))
            script_id, filename = self.cursor.fetchone()
            self.cursor.execute("""
                UPDATE scripts 
                SET content = %s, modified_date = %s 
                WHERE id = %s
            """, (contenido, datetime.now(), script_id))
            self.conn.commit()
            messagebox.showinfo(self.texts[self.language]['success'], self.texts[self.language]['script_saved'])
        except Error as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def verificar_contenido_seguro(self, contenido):
        peligrosos = ['os.remove', 'shutil.rmtree', 'sys.exit', 'Remove-Item']
        return not any(cmd in contenido for cmd in peligrosos)

    def ejecutar_script(self):
        if self.is_executing:
            messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['executing'])
            return
            
        contenido = self.contenido_script.get("1.0", tk.END).strip()
        if not contenido:
            messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['no_script'])
            return
            
        if not self.verificar_contenido_seguro(contenido):
            if not messagebox.askyesno(self.texts[self.language]['warning'], self.texts[self.language]['unsafe_script']):
                return
                
        self.is_executing = True
        try:
            seleccion = self.lista_scripts.curselection()
            if not seleccion:
                messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['select_script'])
                return
                
            self.cursor.execute("SELECT id, filename FROM scripts ORDER BY upload_date DESC LIMIT 1 OFFSET %s", (seleccion[0],))
            script_id, filename = self.cursor.fetchone()
            extension = os.path.splitext(filename)[1].lower()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False, encoding='utf-8') as tmp:
                contenido = contenido.lstrip('\ufeff')
                tmp.write(contenido)
                tmp_path = tmp.name
            
            self.salida_ejecucion.delete('1.0', tk.END)
            self.salida_ejecucion.insert(tk.END, "Ejecutando...\n" if self.language == 'es' else "Executing...\n")
            
            if extension == '.py':
                proceso = subprocess.Popen([sys.executable, tmp_path], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True)
            elif extension == '.ps1':
                proceso = subprocess.Popen(['powershell.exe', '-File', tmp_path], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, text=True)
            else:
                raise ValueError("Extensión no soportada")
                
            stdout, stderr = proceso.communicate()
            
            if stdout:
                self.salida_ejecucion.insert(tk.END, stdout)
            if stderr:
                self.salida_ejecucion.insert(tk.END, f"Errores:\n{stderr}" if self.language == 'es' else f"Errors:\n{stderr}")
                
            success = proceso.returncode == 0
            if success:
                self.salida_ejecucion.insert(tk.END, "\nÉxito\n" if self.language == 'es' else "\nSuccess\n")
                self.actualizar_estadisticas(script_id)
            else:
                self.salida_ejecucion.insert(tk.END, f"\nError (Código: {proceso.returncode})\n")
                
            self.cursor.execute("""
                INSERT INTO execution_logs (script_id, username, execution_date, success)
                VALUES (%s, %s, %s, %s)
            """, (script_id, self.current_user['username'], datetime.now(), success))
            self.conn.commit()
                
        except Exception as e:
            self.salida_ejecucion.insert(tk.END, f"\nError crítico: {str(e)}\n" if self.language == 'es' else f"\nCritical Error: {str(e)}\n")
        finally:
            if 'tmp_path' in locals():
                os.remove(tmp_path)
            self.is_executing = False

    def actualizar_estadisticas(self, script_id):
        try:
            self.cursor.execute("""
                UPDATE scripts 
                SET execution_count = execution_count + 1, 
                    last_execution = %s 
                WHERE id = %s
            """, (datetime.now(), script_id))
            self.conn.commit()
        except Error as e:
            messagebox.showerror("Error", f"Error al actualizar stats: {str(e)}")

    def mostrar_estadisticas(self):
        seleccion = self.lista_scripts.curselection()
        if not seleccion:
            messagebox.showwarning(self.texts[self.language]['warning'], self.texts[self.language]['select_script'])
            return
            
        try:
            self.cursor.execute("""
                SELECT filename, upload_date, modified_date, last_execution, execution_count, 
                       COALESCE(uploaded_by, 'Desconocido') as uploaded_by, downloads
                FROM scripts 
                ORDER BY upload_date DESC 
                LIMIT 1 OFFSET %s
            """, (seleccion[0],))
            resultado = self.cursor.fetchone()
            if resultado:
                filename, upload_date, modified_date, last_exec, exec_count, uploaded_by, downloads = resultado
                stats = (
                    f"Estadísticas de {filename}\n" if self.language == 'es' else f"Statistics of {filename}\n"
                    f"Subido: {upload_date.strftime('%d/%m/%Y %H:%M')}\n" if self.language == 'es' else f"Uploaded: {upload_date.strftime('%d/%m/%Y %H:%M')}\n"
                    f"Modificado: {modified_date.strftime('%d/%m/%Y %H:%M') if modified_date else 'Nunca'}\n" if self.language == 'es' else f"Modified: {modified_date.strftime('%d/%m/%Y %H:%M') if modified_date else 'Never'}\n"
                    f"Por: {uploaded_by}\n" if self.language == 'es' else f"By: {uploaded_by}\n"
                    f"Última ejecución: {last_exec.strftime('%d/%m/%Y %H:%M') if last_exec else 'Nunca'}\n" if self.language == 'es' else f"Last execution: {last_exec.strftime('%d/%m/%Y %H:%M') if last_exec else 'Never'}\n"
                    f"Ejecutado: {exec_count} veces\n" if self.language == 'es' else f"Executed: {exec_count} times\n"
                    f"Descargado: {downloads} veces" if self.language == 'es' else f"Downloaded: {downloads} times"
                )
                messagebox.showinfo(self.texts[self.language]['stats'], stats)
        except Error as e:
            messagebox.showerror("Error", f"Error en estadísticas: {str(e)}")

    def buscar_scripts(self):
        query = f"%{self.search_entry.get().lower()}%"
        self.lista_scripts.delete(0, tk.END)
        try:
            self.cursor.execute("""
                SELECT filename, COALESCE(uploaded_by, 'Desconocido') as uploaded_by 
                FROM scripts 
                WHERE LOWER(filename) LIKE %s 
                ORDER BY upload_date DESC
            """, (query,))
            for (filename, uploaded_by) in self.cursor:
                self.lista_scripts.insert(tk.END, f"{filename} (por {uploaded_by})" if self.language == 'es' else f"{filename} (by {uploaded_by})")
        except Error as e:
            messagebox.showerror("Error", f"Error en búsqueda: {str(e)}")

    def eliminar_todos_scripts(self):
        if messagebox.askyesno("Confirmar", self.texts[self.language]['confirm_delete_scripts']):
            try:
                self.cursor.execute("DELETE FROM scripts")
                self.conn.commit()
                self.cargar_scripts_async()
                messagebox.showinfo(self.texts[self.language]['success'], self.texts[self.language]['script_deleted'])
            except Error as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

    def actualizar_fecha(self):
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.fecha_label.config(text=fecha_actual)
        self.master.after(1000, self.actualizar_fecha)

    def on_close(self):
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
        self.master.destroy()

if __name__ == "__main__":
    ventana = tk.Tk()
    app = AppCompartirScripts(ventana)
    ventana.protocol("WM_DELETE_WINDOW", app.on_close)
    ventana.mainloop()