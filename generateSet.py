import tkinter as tk
from tkinter import filedialog, messagebox
import csv

import tkinter as tk
from tkinter import simpledialog, colorchooser
from tkinter import messagebox
from tkinter import filedialog
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os
from datetime import datetime

#import script as engine
# Configuración inicial
data_letras = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
config_flecha = {
    "color": "black",
    "grosor": 4.0,
    "punta": 0.85
}
configs_predeterminadas = {
    "Flecha S version": {"color": "#2d2d2d", "grosor": 3.5, "punta": 0.35},
    "Flecha negra": {"color": "black", "grosor": 4.0, "punta": 0.85},
    "Flecha Azul": {"color": "blue", "grosor": 4.0, "punta": 0.85},
    "Flecha Roja": {"color": "red", "grosor": 2.5, "punta": 0.75},
}

fig, ax = plt.subplots(figsize=(6, 6))
canvas = None
tamaño_grilla = 8
letras = []
flechas = []
origen = None


class ImportWindow:
    # --- (La parte de la interfaz no cambia) ---
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("Importar Archivos para Generación")
        self.window.geometry("750x300")
        self.window.resizable(False, False)
        self.window.config(bg="lightgray")
        self.file_paths = { "blocks": "C:/Users/nicol/OneDrive/Documentos/Facultad/Becario/Rompecabezas/App-Rompecabezas/input/blocks.csv", "vectores_correctos": "C:/Users/nicol/OneDrive/Documentos/Facultad/Becario/Rompecabezas/App-Rompecabezas/input/vectoresCorrectos.csv", "vectores_promedio": "C:/Users/nicol/OneDrive/Documentos/Facultad/Becario/Rompecabezas/App-Rompecabezas/input/vectoresPromedios.csv", "relacion_grupos": "C:/Users/nicol/OneDrive/Documentos/Facultad/Becario/Rompecabezas/App-Rompecabezas/input/relacionGrupoPatron.csv"}
        self.create_widgets()

    def create_file_input_row(self, frame, label_text, file_key, row_index):
        label = tk.Label(frame, text=label_text, font=("Helvetica", 10), bg="white")
        label.grid(row=row_index, column=0, sticky="w", padx=10, pady=8)
        entry = tk.Entry(frame, width=70, state="readonly", readonlybackground="white", relief="solid", borderwidth=1)
        entry.grid(row=row_index, column=1, sticky="ew", padx=10)
        button = tk.Button(frame, text="Adjuntar...", command=lambda: self.select_file(file_key, entry))
        button.grid(row=row_index, column=2, sticky="e", padx=10)

    def create_widgets(self):
        container = tk.LabelFrame(self.window, text="Archivos CSV Requeridos", bg="white", padx=15, pady=15)
        container.pack(fill="both", expand=True, padx=15, pady=10)
        self.create_file_input_row(container, "Blocks CSV:", "blocks", 0)
        self.create_file_input_row(container, "Vectores Correctos CSV:", "vectores_correctos", 1)
        self.create_file_input_row(container, "Vectores Promedio CSV:", "vectores_promedio", 2)
        self.create_file_input_row(container, "Relación Puzzles-Grupos CSV:", "relacion_grupos", 3)
        container.columnconfigure(1, weight=1)
        button_frame = tk.Frame(self.window, bg="lightgray")
        button_frame.pack(fill="x", padx=15, pady=(0, 10))
        cancel_button = tk.Button(button_frame, text="Cancelar", width=12, command=self.window.destroy)
        cancel_button.pack(side="right", padx=5)
        start_button = tk.Button(button_frame, text="Iniciar Proceso", width=12, command=self.start_process)
        start_button.pack(side="right")

    def select_file(self, file_key, entry_widget):
        filepath = filedialog.askopenfilename(title=f"Selecciona el archivo {file_key}.csv", filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")])
        if filepath:
            self.file_paths[file_key] = filepath
            entry_widget.config(state="normal")
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)
            entry_widget.config(state="readonly")
            print(filepath)
    
    def load_csv_as_matrix(self, filepath, keep_decimals=False):
        """
        Esta función lee un archivo CSV y lo devuelve como una lista de listas (matriz),
        convirtiendo los valores numéricos a enteros o flotantes según el parámetro,
        y excluyendo la fila del encabezado.
        
        Args:
            filepath: Ruta al archivo CSV
            keep_decimals: Si es True, mantiene los decimales; si es False, convierte a enteros
        """
        matrix = []
        with open(filepath, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            
            # Leer y descartar el encabezado para que no entre en la matriz
            next(csv_reader, None)
            
            # Guardar el resto de las filas en la matriz
            for row in csv_reader:
                new_row = []
                for item in row:
                    # Intenta convertir a número, si falla, lo deja como texto
                    try:
                        if keep_decimals:
                            # Mantener como float para preservar decimales
                            new_row.append(float(item))
                        else:
                            # Convertir a int como antes
                            new_row.append(int(float(item)))
                    except (ValueError, TypeError):
                        new_row.append(item if item else '')
                matrix.append(new_row)
                
        return matrix

    def start_process(self):
        """
        Carga un CSV como matriz y la recorre con ciclos for simples.
        """
        directory = filedialog.askdirectory(title="Selecciona carpeta para guardar las imágenes")
        if not directory:
            return False
        
        block_positions = {}
        flechas_values = {}
        coordenadas = [0,0]

        try:
            # 1. Cargar el CSV en una estructura de matriz simple
            data_blocks = self.load_csv_as_matrix(self.file_paths["blocks"])
            data_vectores_correctos = self.load_csv_as_matrix(self.file_paths["vectores_correctos"])
            data_vectores_promedio = self.load_csv_as_matrix(self.file_paths["vectores_promedio"], keep_decimals=True) 
            data_relacion_grupos = self.load_csv_as_matrix(self.file_paths["relacion_grupos"])

            # Ordenar la lista data_relacion_grupos por la columna "GRUPO" (la primera columna)
            data_relacion_grupos.sort(key=lambda row: row[0])

            # Relacionar patrones de coordenadas de bloques
            for fila in data_blocks:
                pattern = fila[0]
                positions = fila[1:]
                block_positions[pattern] = positions

            # Relacionar patrones de indicaciones para flechas correctas
            for fila in data_vectores_correctos:
                pattern = fila[0]
                movements = fila[1:]
                flechas_values[pattern] = movements

            for i in range(len(data_relacion_grupos)):
                # Limpiar las listas globales para cada iteración
                global letras, flechas, origen
                letras.clear()
                flechas.clear()
                origen = None

                # Obtener el patrón del registro actual
                grupo = data_relacion_grupos[i][0]
                patron = data_relacion_grupos[i][1]
                
                # Verificar que el patrón existe en los datos
                if patron not in block_positions:
                    print(f"ERROR: Patrón {patron} no encontrado en block_positions. Saltando registro {i}")
                    continue
                    
                if patron not in flechas_values:
                    print(f"ERROR: Patrón {patron} no encontrado en flechas_values. Saltando registro {i}")
                    continue

                print(f"------- Registro {i} (Grupo: {grupo}, Patrón: {patron}) -----------------------")
                print(f"Coordenadas: {block_positions[patron]}")
                print(f"Movimientos: {flechas_values[patron]}")
                print("--------------------------------------------")
    
                # agregar todos los cuadros a lista letras en las posiciones del patron
                lista_coordenadas = block_positions[patron]
                count = 0
                for j in range(0, len(lista_coordenadas), 2):
                    coordenadas = [lista_coordenadas[j],lista_coordenadas[j+1]]
                    self.insertar_elemento(coordenadas, 'agregar_cuadro', data_letras[count])
                    count = count + 1

                # agregar todas las flechas a lista flechas en las posiciones del patron
                lista_movimientos_correctos = flechas_values[patron]
                
                # Procesar cada letra que se agregó anteriormente
                num_letras = len(letras)
                print(f"Número de letras agregadas: {num_letras}")
                print(f"Número de movimientos disponibles: {len(lista_movimientos_correctos)}")
                
                for letra_idx in range(num_letras):
                    coordenadas_origen = letras[letra_idx]['pos']
                    
                    # Cada letra tiene 4 direcciones: Left, Right, Up, Down
                    # Los índices en lista_movimientos_correctos son: letra_idx * 4 + direccion
                    base_idx = letra_idx * 4
                    
                    # Verificar que tengamos suficientes datos antes de acceder
                    if base_idx + 3 >= len(lista_movimientos_correctos):
                        print(f"Error: No hay suficientes datos de movimientos para la letra {letra_idx}")
                        continue
                    
                    # Obtener los movimientos para cada dirección de esta letra
                    # Asegurar que los valores sean enteros
                    left_movement = int(lista_movimientos_correctos[base_idx + 0])   # Left
                    right_movement = int(lista_movimientos_correctos[base_idx + 1])  # Right
                    up_movement = int(lista_movimientos_correctos[base_idx + 2])     # Up
                    down_movement = int(lista_movimientos_correctos[base_idx + 3])   # Down
                    
                    # Obtener la letra correspondiente de forma segura
                    letra_nombre = data_letras[letra_idx] if letra_idx < len(data_letras) else f"L{letra_idx}"
                    
                    # Crear flechas solo si el movimiento es mayor que 0
                    if left_movement > 0:
                        coordenadas_destino = (coordenadas_origen[0] - left_movement, coordenadas_origen[1])
                        print(f"Letra {letra_nombre} - LEFT: {coordenadas_origen} -> {coordenadas_destino}")
                        self.seleccionar_config("Flecha negra")
                        self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                        self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                    
                    if right_movement > 0:
                        coordenadas_destino = (coordenadas_origen[0] + right_movement, coordenadas_origen[1])
                        print(f"Letra {letra_nombre} - RIGHT: {coordenadas_origen} -> {coordenadas_destino}")
                        self.seleccionar_config("Flecha negra")
                        self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                        self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                    
                    if up_movement > 0:
                        coordenadas_destino = (coordenadas_origen[0], coordenadas_origen[1] + up_movement)
                        print(f"Letra {letra_nombre} - UP: {coordenadas_origen} -> {coordenadas_destino}")
                        self.seleccionar_config("Flecha negra")
                        self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                        self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                    
                    if down_movement > 0:
                        coordenadas_destino = (coordenadas_origen[0], coordenadas_origen[1] - down_movement)
                        print(f"Letra {letra_nombre} - DOWN: {coordenadas_origen} -> {coordenadas_destino}")
                        self.seleccionar_config("Flecha negra")
                        self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                        self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')

                # AGREGAR FLECHAS AZULES (vectores promedio que coinciden con correctos)
                print(f"Usando grupo actual: {grupo} para patrón {patron}")
                # Usar directamente el grupo actual (ya no necesitamos buscarlo)
                grupo_para_patron = grupo
                
                # Obtener los movimientos promedio para este grupo
                lista_movimientos_promedio = []
                if grupo_para_patron is not None:
                    for fila_promedio in data_vectores_promedio:
                        if fila_promedio[0] == grupo_para_patron:
                            lista_movimientos_promedio = fila_promedio[1:]
                            break
                
                print(f"Agregando flechas azules para coincidencias...")
                print(f"Patrón {patron} corresponde al grupo {grupo_para_patron}")
                print(f"Movimientos promedio encontrados: {len(lista_movimientos_promedio)} elementos")
                print(f"Movimientos correctos: {len(lista_movimientos_correctos)} elementos")
                if len(lista_movimientos_promedio) >= len(lista_movimientos_correctos):
                    for letra_idx in range(num_letras):
                        coordenadas_origen = letras[letra_idx]['pos']
                        base_idx = letra_idx * 4
                        
                        # Verificar que tengamos suficientes datos
                        if base_idx + 3 >= len(lista_movimientos_correctos) or base_idx + 3 >= len(lista_movimientos_promedio):
                            continue
                        
                        # Obtener movimientos correctos y promedio para esta letra
                        left_correcto = lista_movimientos_correctos[base_idx + 0]
                        right_correcto = lista_movimientos_correctos[base_idx + 1]
                        up_correcto = lista_movimientos_correctos[base_idx + 2]
                        down_correcto = lista_movimientos_correctos[base_idx + 3]
                        
                        left_promedio = lista_movimientos_promedio[base_idx + 0]
                        right_promedio = lista_movimientos_promedio[base_idx + 1]
                        up_promedio = lista_movimientos_promedio[base_idx + 2]
                        down_promedio = lista_movimientos_promedio[base_idx + 3]
                        
                        letra_nombre = data_letras[letra_idx] if letra_idx < len(data_letras) else f"L{letra_idx}"
                        
                        # Crear flechas azules solo cuando coinciden los valores y ambos son > 0
                        if left_correcto > 0 and left_correcto == left_promedio:
                            coordenadas_destino = (coordenadas_origen[0] - left_correcto, coordenadas_origen[1])
                            print(f"Letra {letra_nombre} - LEFT AZUL (coincidencia {left_correcto}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Azul")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                        
                        if right_correcto > 0 and right_correcto == right_promedio:
                            coordenadas_destino = (coordenadas_origen[0] + right_correcto, coordenadas_origen[1])
                            print(f"Letra {letra_nombre} - RIGHT AZUL (coincidencia {right_correcto}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Azul")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                        
                        if up_correcto > 0 and up_correcto == up_promedio:
                            coordenadas_destino = (coordenadas_origen[0], coordenadas_origen[1] + up_correcto)
                            print(f"Letra {letra_nombre} - UP AZUL (coincidencia {up_correcto}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Azul")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                        
                        if down_correcto > 0 and down_correcto == down_promedio:
                            coordenadas_destino = (coordenadas_origen[0], coordenadas_origen[1] - down_correcto)
                            print(f"Letra {letra_nombre} - DOWN AZUL (coincidencia {down_correcto}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Azul")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')

                # AGREGAR FLECHAS ROJAS (vectores promedio que NO coinciden con correctos)
                print(f"Agregando flechas rojas para NO coincidencias...")
                if len(lista_movimientos_promedio) >= len(lista_movimientos_correctos):
                    for letra_idx in range(num_letras):
                        coordenadas_origen = letras[letra_idx]['pos']
                        base_idx = letra_idx * 4
                        
                        # Verificar que tengamos suficientes datos
                        if base_idx + 3 >= len(lista_movimientos_correctos) or base_idx + 3 >= len(lista_movimientos_promedio):
                            continue
                        
                        # Obtener movimientos correctos y promedio para esta letra
                        left_correcto = lista_movimientos_correctos[base_idx + 0]
                        right_correcto = lista_movimientos_correctos[base_idx + 1]
                        up_correcto = lista_movimientos_correctos[base_idx + 2]
                        down_correcto = lista_movimientos_correctos[base_idx + 3]
                        
                        left_promedio = lista_movimientos_promedio[base_idx + 0]
                        right_promedio = lista_movimientos_promedio[base_idx + 1]
                        up_promedio = lista_movimientos_promedio[base_idx + 2]
                        down_promedio = lista_movimientos_promedio[base_idx + 3]
                        
                        letra_nombre = data_letras[letra_idx] if letra_idx < len(data_letras) else f"L{letra_idx}"
                        
                        # Crear flechas rojas cuando los promedios NO coinciden con correctos
                        # Los valores de promedio ahora son decimales, se usan directamente
                        if left_correcto != left_promedio:
                            coordenadas_destino = (coordenadas_origen[0] - left_promedio, coordenadas_origen[1])
                            print(f"Letra {letra_nombre} - LEFT ROJA (NO coincidencia: correcto={left_correcto}, promedio={left_promedio}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Roja")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                        
                        if right_correcto != right_promedio:
                            coordenadas_destino = (coordenadas_origen[0] + right_promedio, coordenadas_origen[1])
                            print(f"Letra {letra_nombre} - RIGHT ROJA (NO coincidencia: correcto={right_correcto}, promedio={right_promedio}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Roja")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                        
                        if up_correcto != up_promedio:
                            coordenadas_destino = (coordenadas_origen[0], coordenadas_origen[1] + up_promedio)
                            print(f"Letra {letra_nombre} - UP ROJA (NO coincidencia: correcto={up_correcto}, promedio={up_promedio}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Roja")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                        
                        if down_correcto != down_promedio:
                            coordenadas_destino = (coordenadas_origen[0], coordenadas_origen[1] - down_promedio)
                            print(f"Letra {letra_nombre} - DOWN ROJA (NO coincidencia: correcto={down_correcto}, promedio={down_promedio}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Roja")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')

                # agregar todas las flechas a la lista de flechas en los origenes y destino del patron
                # Usar el número de grupo en lugar del índice
                self.exportar_imagen(filename=os.path.join(directory, f"AD25 {grupo}.png"))
                

            messagebox.showinfo("Proceso Exitoso", "La matriz de datos se ha impreso en la consola.")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar el archivo.\n\nError: {e}")
            return
            
    def start_process_limited(self, directory, max_records=3):
        """
        Versión limitada para pruebas - procesa solo los primeros max_records registros
        """
        
        block_positions = {}
        flechas_values = {}
        coordenadas = [0,0]

        try:
            # 1. Cargar el CSV en una estructura de matriz simple
            data_blocks = self.load_csv_as_matrix(self.file_paths["blocks"])
            data_vectores_correctos = self.load_csv_as_matrix(self.file_paths["vectores_correctos"])
            data_vectores_promedio = self.load_csv_as_matrix(self.file_paths["vectores_promedio"], keep_decimals=True) 
            data_relacion_grupos = self.load_csv_as_matrix(self.file_paths["relacion_grupos"])

            # Ordenar la lista data_relacion_grupos por la columna "GRUPO" (la primera columna)
            data_relacion_grupos.sort(key=lambda row: row[0])

            # Relacionar patrones de coordenadas de bloques
            for fila in data_blocks:
                pattern = fila[0]
                positions = fila[1:]
                block_positions[pattern] = positions

            # Relacionar patrones de indicaciones para flechas correctas
            for fila in data_vectores_correctos:
                pattern = fila[0]
                movements = fila[1:]
                flechas_values[pattern] = movements

            # Procesar solo los primeros max_records registros
            for i in range(min(max_records, len(data_relacion_grupos))):
                # Limpiar las listas globales para cada iteración
                global letras, flechas, origen
                letras.clear()
                flechas.clear()
                origen = None

                # Obtener el patrón del registro actual
                grupo = data_relacion_grupos[i][0]
                patron = data_relacion_grupos[i][1]
                
                # Verificar que el patrón existe en los datos
                if patron not in block_positions:
                    print(f"ERROR: Patrón {patron} no encontrado en block_positions. Saltando registro {i}")
                    continue
                    
                if patron not in flechas_values:
                    print(f"ERROR: Patrón {patron} no encontrado en flechas_values. Saltando registro {i}")
                    continue

                print(f"------- Registro {i} (Grupo: {grupo}, Patrón: {patron}) -----------------------")
                print(f"Coordenadas: {block_positions[patron]}")
                print(f"Movimientos: {flechas_values[patron]}")
                print("--------------------------------------------")
    
                # agregar todos los cuadros a lista letras en las posiciones del patron
                lista_coordenadas = block_positions[patron]
                count = 0
                for j in range(0, len(lista_coordenadas), 2):
                    coordenadas = [lista_coordenadas[j],lista_coordenadas[j+1]]
                    self.insertar_elemento(coordenadas, 'agregar_cuadro', data_letras[count])
                    count = count + 1

                # agregar todas las flechas a lista flechas en las posiciones del patron
                lista_movimientos_correctos = flechas_values[patron]
                
                # Procesar cada letra que se agregó anteriormente
                num_letras = len(letras)
                print(f"Número de letras agregadas: {num_letras}")
                print(f"Número de movimientos disponibles: {len(lista_movimientos_correctos)}")
                
                for letra_idx in range(num_letras):
                    coordenadas_origen = letras[letra_idx]['pos']
                    
                    # Cada letra tiene 4 direcciones: Left, Right, Up, Down
                    # Los índices en lista_movimientos_correctos son: letra_idx * 4 + direccion
                    base_idx = letra_idx * 4
                    
                    # Verificar que tengamos suficientes datos antes de acceder
                    if base_idx + 3 >= len(lista_movimientos_correctos):
                        print(f"Error: No hay suficientes datos de movimientos para la letra {letra_idx}")
                        continue
                    
                    # Obtener los movimientos para cada dirección de esta letra
                    left_movement = lista_movimientos_correctos[base_idx + 0]   # Left
                    right_movement = lista_movimientos_correctos[base_idx + 1]  # Right
                    up_movement = lista_movimientos_correctos[base_idx + 2]     # Up
                    down_movement = lista_movimientos_correctos[base_idx + 3]   # Down

                    # Obtener la letra correspondiente de forma segura
                    letra_nombre = data_letras[letra_idx] if letra_idx < len(data_letras) else f"L{letra_idx}"
                    
                    # Crear flechas solo si el movimiento es mayor que 0
                    if left_movement > 0:
                        coordenadas_destino = (coordenadas_origen[0] - left_movement, coordenadas_origen[1])
                        print(f"Letra {letra_nombre} - LEFT: {coordenadas_origen} -> {coordenadas_destino}")
                        self.seleccionar_config("Flecha negra")
                        self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                        self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                    
                    if right_movement > 0:
                        coordenadas_destino = (coordenadas_origen[0] + right_movement, coordenadas_origen[1])
                        print(f"Letra {letra_nombre} - RIGHT: {coordenadas_origen} -> {coordenadas_destino}")
                        self.seleccionar_config("Flecha negra")
                        self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                        self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                    
                    if up_movement > 0:
                        coordenadas_destino = (coordenadas_origen[0], coordenadas_origen[1] + up_movement)
                        print(f"Letra {letra_nombre} - UP: {coordenadas_origen} -> {coordenadas_destino}")
                        self.seleccionar_config("Flecha negra")
                        self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                        self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                    
                    if down_movement > 0:
                        coordenadas_destino = (coordenadas_origen[0], coordenadas_origen[1] - down_movement)
                        print(f"Letra {letra_nombre} - DOWN: {coordenadas_origen} -> {coordenadas_destino}")
                        self.seleccionar_config("Flecha negra")
                        self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                        self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')

                # AGREGAR FLECHAS AZULES (vectores promedio que coinciden con correctos)
                print(f"Usando grupo actual: {grupo} para patrón {patron}")
                # Usar directamente el grupo actual (ya no necesitamos buscarlo)
                grupo_para_patron = grupo
                
                # Obtener los movimientos promedio para este grupo
                lista_movimientos_promedio = []
                if grupo_para_patron is not None:
                    for fila_promedio in data_vectores_promedio:
                        if fila_promedio[0] == grupo_para_patron:
                            lista_movimientos_promedio = fila_promedio[1:]
                            break
                
                print(f"Agregando flechas azules para coincidencias...")
                print(f"Patrón {patron} corresponde al grupo {grupo_para_patron}")
                print(f"Movimientos promedio encontrados: {len(lista_movimientos_promedio)} elementos")
                print(f"Movimientos correctos: {len(lista_movimientos_correctos)} elementos")
                if len(lista_movimientos_promedio) >= len(lista_movimientos_correctos):
                    for letra_idx in range(num_letras):
                        coordenadas_origen = letras[letra_idx]['pos']
                        base_idx = letra_idx * 4
                        
                        # Verificar que tengamos suficientes datos
                        if base_idx + 3 >= len(lista_movimientos_correctos) or base_idx + 3 >= len(lista_movimientos_promedio):
                            continue
                        
                        # Obtener movimientos correctos y promedio para esta letra
                        left_correcto = lista_movimientos_correctos[base_idx + 0]
                        right_correcto = lista_movimientos_correctos[base_idx + 1]
                        up_correcto = lista_movimientos_correctos[base_idx + 2]
                        down_correcto = lista_movimientos_correctos[base_idx + 3]
                        
                        left_promedio = lista_movimientos_promedio[base_idx + 0]
                        right_promedio = lista_movimientos_promedio[base_idx + 1]
                        up_promedio = lista_movimientos_promedio[base_idx + 2]
                        down_promedio = lista_movimientos_promedio[base_idx + 3]
                        
                        letra_nombre = data_letras[letra_idx] if letra_idx < len(data_letras) else f"L{letra_idx}"
                        
                        # Crear flechas azules solo cuando coinciden los valores y ambos son > 0
                        if left_correcto > 0 and left_correcto == left_promedio:
                            coordenadas_destino = (coordenadas_origen[0] - left_correcto, coordenadas_origen[1])
                            print(f"Letra {letra_nombre} - LEFT AZUL (coincidencia {left_correcto}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Azul")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                        
                        if right_correcto > 0 and right_correcto == right_promedio:
                            coordenadas_destino = (coordenadas_origen[0] + right_correcto, coordenadas_origen[1])
                            print(f"Letra {letra_nombre} - RIGHT AZUL (coincidencia {right_correcto}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Azul")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                        
                        if up_correcto > 0 and up_correcto == up_promedio:
                            coordenadas_destino = (coordenadas_origen[0], coordenadas_origen[1] + up_correcto)
                            print(f"Letra {letra_nombre} - UP AZUL (coincidencia {up_correcto}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Azul")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                        
                        if down_correcto > 0 and down_correcto == down_promedio:
                            coordenadas_destino = (coordenadas_origen[0], coordenadas_origen[1] - down_correcto)
                            print(f"Letra {letra_nombre} - DOWN AZUL (coincidencia {down_correcto}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Azul")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')

                # AGREGAR FLECHAS ROJAS (vectores promedio que NO coinciden con correctos)
                print(f"Agregando flechas rojas para NO coincidencias...")
                if len(lista_movimientos_promedio) >= len(lista_movimientos_correctos):
                    for letra_idx in range(num_letras):
                        coordenadas_origen = letras[letra_idx]['pos']
                        base_idx = letra_idx * 4
                        
                        # Verificar que tengamos suficientes datos
                        if base_idx + 3 >= len(lista_movimientos_correctos) or base_idx + 3 >= len(lista_movimientos_promedio):
                            continue
                        
                        # Obtener movimientos correctos y promedio para esta letra
                        left_correcto = lista_movimientos_correctos[base_idx + 0]
                        right_correcto = lista_movimientos_correctos[base_idx + 1]
                        up_correcto = lista_movimientos_correctos[base_idx + 2]
                        down_correcto = lista_movimientos_correctos[base_idx + 3]
                        
                        left_promedio = lista_movimientos_promedio[base_idx + 0]
                        right_promedio = lista_movimientos_promedio[base_idx + 1]
                        up_promedio = lista_movimientos_promedio[base_idx + 2]
                        down_promedio = lista_movimientos_promedio[base_idx + 3]
                        
                        letra_nombre = data_letras[letra_idx] if letra_idx < len(data_letras) else f"L{letra_idx}"
                        
                        # Crear flechas rojas cuando los promedios NO coinciden con correctos, pero ambos son > 0
                        if left_correcto > 0 and left_promedio > 0 and left_correcto != left_promedio:
                            coordenadas_destino = (coordenadas_origen[0] - left_promedio, coordenadas_origen[1])
                            print(f"Letra {letra_nombre} - LEFT ROJA (NO coincidencia: correcto={left_correcto}, promedio={left_promedio}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Roja")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                        
                        if right_correcto > 0 and right_promedio > 0 and right_correcto != right_promedio:
                            coordenadas_destino = (coordenadas_origen[0] + right_promedio, coordenadas_origen[1])
                            print(f"Letra {letra_nombre} - RIGHT ROJA (NO coincidencia: correcto={right_correcto}, promedio={right_promedio}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Roja")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                        
                        if up_correcto > 0 and up_promedio > 0 and up_correcto != up_promedio:
                            coordenadas_destino = (coordenadas_origen[0], coordenadas_origen[1] + up_promedio)
                            print(f"Letra {letra_nombre} - UP ROJA (NO coincidencia: correcto={up_correcto}, promedio={up_promedio}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Roja")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')
                        
                        if down_correcto > 0 and down_promedio > 0 and down_correcto != down_promedio:
                            coordenadas_destino = (coordenadas_origen[0], coordenadas_origen[1] - down_promedio)
                            print(f"Letra {letra_nombre} - DOWN ROJA (NO coincidencia: correcto={down_correcto}, promedio={down_promedio}): {coordenadas_origen} -> {coordenadas_destino}")
                            self.seleccionar_config("Flecha Roja")
                            self.insertar_elemento(coordenadas_origen, 'agregar_origen_flecha')
                            self.insertar_elemento(coordenadas_destino, 'agregar_destino_flecha')

                # agregar todas las flechas a la lista de flechas en los origenes y destino del patron
                # Usar el número de grupo en lugar del índice
                filename = os.path.join(directory, f"test_AD25_{grupo}.png")
                success = self.exportar_imagen(filename=filename)
                if success:
                    print(f"Imagen {filename} generada exitosamente")
                else:
                    print(f"Error al generar imagen {filename}")
                
            print(f"Procesamiento limitado completado. {min(max_records, len(data_relacion_grupos))} registros procesados.")

        except Exception as e:
            print(f"Error en procesamiento limitado: {e}")
            import traceback
            traceback.print_exc()
            raise
        
    def seleccionar_config(self, nombre_config):
        global config_flecha
        config_flecha = configs_predeterminadas[nombre_config]

    def insertar_elemento(self, coordenadas, modo_actual, letra=None):
        global origen
        if coordenadas is None:
            return
        
        # Permitir coordenadas decimales para las flechas de promedios
        # Solo convertir a int para cuadros (letras)
        if modo_actual == 'agregar_cuadro':
            x = int(coordenadas[0])
            y = int(coordenadas[1])
        else:
            # Para flechas, mantener las coordenadas con decimales
            x = coordenadas[0]
            y = coordenadas[1]

        if not (0 <= x < tamaño_grilla and 0 <= y < tamaño_grilla):
            print(f"SOBREPASO GRILLA")
            return

        if modo_actual == 'agregar_cuadro':
            if letra:
                letras.append({"texto": letra.upper(), "pos": (x, y), "color": "white", "fondo": "black"})

        elif modo_actual == 'agregar_origen_flecha':
            # Siempre establecer el origen para las flechas generadas automáticamente
            origen = (x, y)

        elif modo_actual == 'agregar_destino_flecha':
            if origen is not None:
                destino = (x, y)
                if destino == origen:
                    print(f"Origen y destino son iguales: {origen}")
                    origen = None
                    return
                    
                # Verificar que sea una flecha válida (horizontal o vertical)
                if origen[0] == destino[0] or origen[1] == destino[1]:
                    flechas.append({
                        "origen": origen,
                        "destino": destino,
                        "config": config_flecha.copy(),
                        "dir": self.obtener_direccion_flecha(origen, destino)
                    })
                    print(f"Flecha creada: {origen} -> {destino}")
                else:
                    print(f"Flecha diagonal rechazada: {origen} -> {destino}")
                
                # Resetear origen después de cada intento de crear flecha
                origen = None
            else:
                print("Error: No hay origen establecido para la flecha")



    def exportar_imagen(self, filename=None):
        """Exporta la imagen del rompecabezas en diferentes modos."""
        if not filename:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
        
        if not filename:
            return False
            
        try:
            # Crear una nueva figura temporal para la exportación
            temp_fig, temp_ax = plt.subplots(figsize=(6, 6))
            
            # Dibujar grilla base
            for x in range(tamaño_grilla + 1):
                temp_ax.plot([x, x], [0, tamaño_grilla], color='black', linewidth=0.5)
            for y in range(tamaño_grilla + 1):
                temp_ax.plot([0, tamaño_grilla], [y, y], color='black', linewidth=0.5)
            
            # Primero dibujamos las flechas para que queden detrás de los cuadros
            for flecha in flechas:
                origen = flecha["origen"]
                destino = flecha["destino"]
                x1, y1 = origen
                x2, y2 = destino
                direction = flecha["dir"]
                config = flecha["config"]
                # Lógica para dibujar la flecha desde el borde de la celda
                if direction == 0:  # Vertical hacia abajo
                    xi = 0.5; yi = 1
                elif direction == 1:  # Vertical hacia arriba
                    xi = 0.5; yi = 0
                elif direction == 2:  # Horizontal hacia derecha
                    xi = 1; yi = 0.5
                elif direction == 3:  # Horizontal hacia izquierda
                    xi = 0; yi = 0.5
                temp_ax.arrow(
                    x1 + xi, y1 + yi,
                    x2 - x1, y2 - y1,
                    width=config["grosor"] * 0.1,
                    head_width=config["punta"],
                    head_length=config["punta"],
                    fc=config["color"],
                    ec=config["color"],
                    length_includes_head=True,
                    zorder=3
                )
        
            for letra in letras:
                x, y = letra["pos"]
                temp_ax.add_patch(patches.Rectangle((x, y), 1, 1, 
                    facecolor=letra["fondo"], edgecolor='black'))
                temp_ax.text(x + 0.5, y + 0.5, letra["texto"], 
                    ha='center', va='center', color=letra["color"], 
                    fontsize=180/tamaño_grilla, weight='bold')
            
            # Configuración común para todos los modos
            temp_ax.set_xlim(0, tamaño_grilla)
            temp_ax.set_ylim(0, tamaño_grilla)
            temp_ax.set_aspect('equal')
            temp_ax.axis('off')
            
            # Guardar y cerrar la figura temporal
            temp_fig.savefig(filename, bbox_inches='tight', dpi=300)
            plt.close(temp_fig)

            # NO limpiar las listas aquí, se limpian al inicio de cada iteración
            
            #messagebox.showinfo("Éxito", "Imagen exportada correctamente")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar la imagen: {str(e)}")
            return False
        
    def obtener_direccion_flecha(self, origen, destino):
        """
        Determines the direction of an arrow based on its origin and destination.
        Ahora soporta flechas con coordenadas decimales.

        Parameters:
            origen (tuple): A tuple (x, y) representing the starting point of the arrow.
            destino (tuple): A tuple (x, y) representing the ending point of the arrow.

        Returns:
            int: An integer representing the direction of the arrow:
                0 - Down (vertical),
                1 - Up (vertical),
                2 - Right (horizontal),
                3 - Left (horizontal).
        """
        # Calcular las diferencias
        dx = destino[0] - origen[0]
        dy = destino[1] - origen[1]
        
        # Determinar dirección predominante
        # Si la diferencia en X es mayor (horizontal)
        if abs(dx) > abs(dy):
            if dx > 0:
                return 2  # Right
            else:
                return 3  # Left
        else:
            # Predominantemente vertical
            if dy > 0:
                return 0  # Down
            else:
                return 1  # Up