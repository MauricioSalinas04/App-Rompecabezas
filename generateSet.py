import tkinter as tk
from tkinter import filedialog, messagebox
import csv

class ImportWindow:
    # --- (La parte de la interfaz no cambia) ---
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("Importar Archivos para Generación")
        self.window.geometry("750x300")
        self.window.resizable(False, False)
        self.window.config(bg="lightgray")
        self.file_paths = { "blocks": "", "vectores_correctos": "", "vectores_promedio": "", "relacion_grupos": "" }
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
    
    def load_csv_as_matrix(self, filepath):
        """
        Esta función lee un archivo CSV y lo devuelve como una lista de listas (matriz).
        También devuelve el encabezado por separado.
        """
        matrix = []
        with open(filepath, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            
            # Leer el encabezado para separarlo de los datos
            header = next(csv_reader, None)
            
            # Guardar el resto de las filas en la matriz
            for row in csv_reader:
                matrix.append(row)
                
        return header, matrix

    def start_process(self):
        """
        Carga un CSV como matriz y la recorre con ciclos for simples.
        """
        filepath = self.file_paths["blocks"]
        if not filepath:
            messagebox.showwarning("Falta archivo", "Por favor, adjunta el archivo para 'blocks'.")
            return

        try:
            # 1. Cargar el CSV en una estructura de matriz simple
            header, data_matrix = self.load_csv_as_matrix(filepath)
            
            print(f"Encabezado del CSV: {header}")
            print("--- Recorriendo la matriz con ciclos 'for' ---\n")

            # 2. Usar ciclos simples para recorrer la matriz (lista de listas)
            # Ciclo exterior para las filas (índice i)
            for i in range(len(data_matrix)):
                # Ciclo interior para las columnas (índice j)
                for j in range(len(data_matrix[i])):
                    # Acceder al valor usando los índices de la matriz: matriz[fila][columna]
                    cell_value = data_matrix[i][j]
                    if cell_value == '':
                        print(f"  Fila {i}, Columna {j} | Valor: NULL")
                    else:
                        print(f"  Fila {i}, Columna {j} | Valor: {cell_value}")

            
            messagebox.showinfo("Proceso Exitoso", "La matriz de datos se ha impreso en la consola.")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar el archivo.\n\nError: {e}")
            return