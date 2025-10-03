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
from generateSet import ImportWindow  


# Configuración inicial
config_flecha = {
    "color": "black",
    "grosor": 4.0,
    "punta": 0.85
}

fig, ax = plt.subplots(figsize=(6, 6))
canvas = None
tamaño_grilla = 8
letras = []
flechas = []
modo_actual = None
origen_temporal = None
recorridos = {}

# Archivos de configuración
ARCHIVO_CONFIG = "configs_flechas.json"
configs_predeterminadas = {
    "Flecha S version": {"color": "#2d2d2d", "grosor": 3.5, "punta": 0.35},
    "Flecha negra": {"color": "black", "grosor": 4.0, "punta": 0.85},
    "Flecha Azul": {"color": "blue", "grosor": 4.0, "punta": 0.85},
    "Flecha Roja": {"color": "red", "grosor": 2.5, "punta": 0.75},
}
if os.path.exists(ARCHIVO_CONFIG):
    with open(ARCHIVO_CONFIG, 'r') as f:
        configuraciones_guardadas = json.load(f)
else:
    configuraciones_guardadas = configs_predeterminadas.copy()
    with open(ARCHIVO_CONFIG, 'w') as f:
        json.dump(configuraciones_guardadas, f, indent=4)

# Funciones de dibujo
def dibujar_grilla(tamaño):
    ax.clear()
    for x in range(tamaño + 1):
        ax.plot([x, x], [0, tamaño], color='black', linewidth=0.5)
    for y in range(tamaño + 1):
        ax.plot([0, tamaño], [y, y], color='black', linewidth=0.5)

def agregar_letras(letras):
    # Calcular el tamaño de fuente base según el tamaño de la grilla
    tamaño_fuente_base = 180 / tamaño_grilla
    
    for letra in letras:
        x, y = letra["pos"]
        ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor=letra["fondo"], edgecolor='black', zorder=4))
        ax.text(x + 0.5, y + 0.5, letra["texto"], ha='center', va='center',
                color=letra["color"], fontsize=tamaño_fuente_base, weight='bold', zorder=5)
        key = (x, y)
        if key in recorridos:
            ax.text(x + 0.5, y + 0.2, f"{recorridos[key]}", ha='center', va='center',
                    color='white', fontsize=tamaño_fuente_base * 0.6, zorder=6)

def agregar_flechas(flechas):
    for f in flechas:
        x1, y1 = f["origen"]
        x2, y2 = f["destino"]
        config = f["config"]
        direction = f["dir"]
        dx = x2 - x1
        dy = y2 - y1

        if direction == 0:  #Vertical hacia abajo
            xi = 0.5
            yi = 1
        elif direction == 1:  #Vertical hacia arriba
            xi = 0.5
            yi = 0
        elif direction == 2:  #Horizontal hacia derecha
            xi = 1
            yi = 0.5
        elif direction == 3:  #Horizontal hacia izquierda
            xi = 0
            yi = 0.5
                

        ax.arrow(
            x1 + xi, y1 + yi,
            dx, dy,
            width=config["grosor"] * 0.1,
            head_width=config["punta"],
            head_length=config["punta"],
            fc=config["color"],
            ec=config["color"],
            length_includes_head=True,
            zorder=3
        )
        

def actualizar_canvas():
    ax.set_xlim(0, tamaño_grilla)
    ax.set_ylim(0, tamaño_grilla)
    ax.set_aspect('equal')
    ax.set_xticks(range(tamaño_grilla + 1))
    ax.set_yticks(range(tamaño_grilla + 1))
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    ax.set_frame_on(True)
    canvas.draw()

# Acciones de usuario
def crear_grilla():
    global tamaño_grilla, letras, flechas, recorridos
    respuesta = simpledialog.askinteger("Tamaño de la Grilla", "Introduce el tamaño de la grilla:", minvalue=1, maxvalue=20)
    if respuesta:
        tamaño_grilla = respuesta
        letras.clear()
        flechas.clear()
        recorridos.clear()
        dibujar_grilla(tamaño_grilla)
        actualizar_canvas()

def activar_modo_agregar_cuadro():
    global modo_actual, origen_temporal
    modo_actual = 'agregar_cuadro'
    origen_temporal = None
    ocultar_config_flecha()

def activar_modo_agregar_flecha():
    global modo_actual, origen_temporal
    modo_actual = 'agregar_flecha'
    origen_temporal = None
    mostrar_config_flecha()

# Agregar esta función con las otras funciones de modo
def activar_modo_eliminar():
    global modo_actual, origen_temporal
    modo_actual = 'eliminar'
    origen_temporal = None
    ocultar_config_flecha()

def obtener_direccion_flecha(origen, destino):
    """
    Determines the direction of an arrow based on its origin and destination.

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
    if origen[0] == destino[0]: 
        if destino[1] > origen[1]:
            return 0  
        else:
            return 1
    elif origen[1] == destino[1]:  
        if destino[0] > origen[0]:
            return 2  
        else:
            return 3

def distancia_punto_a_linea(punto, inicio, fin):
    """Calcula la distancia de un punto a una línea"""
    x, y = punto
    x1, y1 = inicio
    x2, y2 = fin
    
    # Si la línea es vertical
    if x1 == x2:
        return abs(x - x1) if min(y1, y2) <= y <= max(y1, y2) else float('inf')
    # Si la línea es horizontal
    if y1 == y2:
        return abs(y - y1) if min(x1, x2) <= x <= max(x1, x2) else float('inf')
    return float('inf')  
        
def manejar_click(event):
    global origen_temporal
    if event.xdata is None or event.ydata is None:
        return
    x = int(event.xdata)
    y = int(event.ydata)
    if not (0 <= x < tamaño_grilla and 0 <= y < tamaño_grilla):
        return

    if modo_actual == 'agregar_cuadro':
        letra = simpledialog.askstring("Letra", "Ingresa la letra para esta celda:")
        if letra:
            letras.append({"texto": letra.upper(), "pos": (x, y), "color": "white", "fondo": "black"})
            dibujar_grilla(tamaño_grilla)
            agregar_letras(letras)
            agregar_flechas(flechas)
            actualizar_canvas()

    elif modo_actual == 'agregar_flecha':
        if origen_temporal is None:
            # Buscar si hay letra en esa celda
            if any(letra["pos"] == (x, y) for letra in letras):
                origen_temporal = (x, y)
        else:
            destino = (x, y)
            if destino == origen_temporal:
                origen_temporal = None
                return
                
            if origen_temporal[0] == destino[0] or origen_temporal[1] == destino[1]:
                flechas.append({
                    "origen": origen_temporal,
                    "destino": destino,
                    "config": config_flecha.copy(),
                    "dir": obtener_direccion_flecha(origen_temporal, destino)
                })
                recorrido = abs(destino[0] - origen_temporal[0]) + abs(destino[1] - origen_temporal[1])
                recorridos[origen_temporal] = recorridos.get(origen_temporal, 0) + recorrido
                origen_temporal = None
                dibujar_grilla(tamaño_grilla)
                agregar_letras(letras)
                agregar_flechas(flechas)
                actualizar_canvas()
            else:
                print("Solo se permiten flechas horizontales o verticales.")
                origen_temporal = None
                
    elif modo_actual == 'eliminar':
        # Verificar si hay un cuadro en la posición
        cuadro_eliminado = any(letra["pos"] == (x, y) for letra in letras)
        if cuadro_eliminado:
            # Eliminar el cuadro
            letras[:] = [l for l in letras if l["pos"] != (x, y)]

            # Eliminar todas las flechas que salen del cuadro eliminado
            flechas[:] = [f for f in flechas if f["origen"] != (x, y)]

            # Eliminar el recorrido asociado al cuadro
            if (x, y) in recorridos:
                del recorridos[(x, y)]
        else:
            # Buscar flecha cercana al clic
            punto_clic = (event.xdata, event.ydata)
            flecha_a_eliminar = None
            distancia_minima = 0.3

            for i, f in enumerate(flechas):
                distancia = distancia_punto_a_linea(
                    punto_clic, 
                    (f["origen"][0] + 0.5, f["origen"][1] + 0.5),
                    (f["destino"][0] + 0.5, f["destino"][1] + 0.5)
                )
                if distancia < distancia_minima:
                    flecha_a_eliminar = i
                    break
                
            if flecha_a_eliminar is not None:
                # Actualizar recorrido antes de eliminar la flecha
                origen = flechas[flecha_a_eliminar]["origen"]
                destino = flechas[flecha_a_eliminar]["destino"]
                recorrido = abs(destino[0] - origen[0]) + abs(destino[1] - origen[1])
                if origen in recorridos:
                    recorridos[origen] -= recorrido
                    if recorridos[origen] <= 0:
                        del recorridos[origen]

                # Eliminar la flecha
                del flechas[flecha_a_eliminar]

        # Actualizar visualización
        dibujar_grilla(tamaño_grilla)
        agregar_letras(letras)
        agregar_flechas(flechas)
        actualizar_canvas()

# Configuración de flechas
def mostrar_config_flecha():
    panel_config_flecha.pack(pady=5, fill=tk.X)

def ocultar_config_flecha():
    panel_config_flecha.pack_forget()

def seleccionar_color():
    color = colorchooser.askcolor()[1]
    if color:
        config_flecha["color"] = color
        boton_color.config(bg=color)

def actualizar_config_flecha(val=None):
    config_flecha["grosor"] = float(scale_grosor.get())
    config_flecha["punta"] = float(scale_punta.get())

def seleccionar_config(nombre_config):
    global config_flecha
    config_flecha = configuraciones_guardadas[nombre_config].copy()
    scale_grosor.set(config_flecha["grosor"])
    scale_punta.set(config_flecha["punta"])
    boton_color.config(bg=config_flecha["color"])

def guardar_nueva_config():
    nombre = simpledialog.askstring("Guardar Config", "Nombre de esta configuración:")
    if nombre:
        configuraciones_guardadas[nombre] = config_flecha.copy()
        with open(ARCHIVO_CONFIG, 'w') as f:
            json.dump(configuraciones_guardadas, f, indent=4)
        actualizar_menu_configs()

def actualizar_menu_configs():
    menu_config["menu"].delete(0, "end")
    for nombre in configuraciones_guardadas.keys():
        menu_config["menu"].add_command(label=nombre, command=lambda n=nombre: [menu_var.set(n), seleccionar_config(n)])


###################################################################################
# ADMINISTRACION DE LOS DATOS
###################################################################################

archivo_actual = None

def guardar_proyecto():
    """Guarda el estado actual del proyecto."""
    global archivo_actual
    if archivo_actual is None:
        return guardar_como()
    
    try:
        data = crear_datos_guardado()
        with open(archivo_actual, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("Éxito", "Proyecto guardado correctamente")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar el archivo: {str(e)}")
        return False

def guardar_como():
    """Guarda el proyecto con un nuevo nombre de archivo."""
    global archivo_actual
    filename = filedialog.asksaveasfilename(
        defaultextension=".puzzle",
        filetypes=[("Puzzle files", "*.puzzle"), ("All files", "*.*")]
    )
    
    if filename:
        archivo_actual = filename
        return guardar_proyecto()
    return False

def crear_datos_guardado():
    """Crea la estructura de datos para guardar."""
    return {
        "metadata": {
            "version": "1.0",
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "grid_size": tamaño_grilla
        },
        "elements": {
            "squares": [
                {
                    "position": list(letra["pos"]),
                    "text": letra["texto"],
                    "color": letra["color"],
                    "background": letra["fondo"]
                }
                for letra in letras
            ],
            "arrows": [
                {
                    "origin": list(flecha["origen"]),
                    "destination": list(flecha["destino"]),
                    "direction": flecha["dir"],
                    "config": {
                        "color": flecha["config"]["color"],
                        "thickness": flecha["config"]["grosor"],
                        "head_size": flecha["config"]["punta"]
                    }
                }
                for flecha in flechas
            ]
        },
        "routes": {
            f"{key[0]},{key[1]}": value
            for key, value in recorridos.items()
        }
    }

def abrir_proyecto():
    """Abre un archivo de proyecto guardado."""
    global archivo_actual, tamaño_grilla, letras, flechas, recorridos
    
    filename = filedialog.askopenfilename(
        defaultextension=".puzzle",
        filetypes=[("Puzzle files", "*.puzzle"), ("All files", "*.*")]
    )
    
    if not filename:
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Validar versión
        if data.get("metadata", {}).get("version") != "1.0":
            raise ValueError("Versión de archivo no compatible")
        
        # Cargar datos
        tamaño_grilla = data["metadata"]["grid_size"]
        
        # Cargar cuadros
        letras = [
            {
                "pos": tuple(square["position"]),
                "texto": square["text"],
                "color": square["color"],
                "fondo": square["background"]
            }
            for square in data["elements"]["squares"]
        ]
        
        # Cargar flechas
        flechas = [
            {
                "origen": tuple(arrow["origin"]),
                "destino": tuple(arrow["destination"]),
                "dir": arrow["direction"],
                "config": {
                    "color": arrow["config"]["color"],
                    "grosor": arrow["config"]["thickness"],
                    "punta": arrow["config"]["head_size"]
                }
            }
            for arrow in data["elements"]["arrows"]
        ]
        
        # Cargar recorridos
        recorridos = {
            tuple(map(int, key.split(","))): value
            for key, value in data["routes"].items()
        }
        
        archivo_actual = filename
        
        # Actualizar visualización
        dibujar_grilla(tamaño_grilla)
        agregar_letras(letras)
        agregar_flechas(flechas)
        actualizar_canvas()
        
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir el archivo: {str(e)}")
        return False

def exportar_imagen(modo="normal", filename=None):
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
            
        # Configurar diferentes modos de visualización
        if modo == "solo_letras":
            # Solo cuadros con letras
            for letra in letras:
                x, y = letra["pos"]
                temp_ax.add_patch(patches.Rectangle((x, y), 1, 1, 
                    facecolor=letra["fondo"], edgecolor='black'))
                temp_ax.text(x + 0.5, y + 0.5, letra["texto"], 
                    ha='center', va='center', color=letra["color"], 
                    fontsize=180/tamaño_grilla, weight='bold')
                    
        elif modo == "solo_numeros":
            # Cuadros con números en lugar de letras
            for letra in letras:
                x, y = letra["pos"]
                temp_ax.add_patch(patches.Rectangle((x, y), 1, 1, 
                    facecolor=letra["fondo"], edgecolor='black'))
                if (x, y) in recorridos:
                    temp_ax.text(x + 0.5, y + 0.5, str(recorridos[(x, y)]), 
                        ha='center', va='center', color='white', 
                        fontsize=180/tamaño_grilla, weight='bold')
        else:
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

            if modo == "completo_aqua":
                # Versión completa con números en verde claro
                # Luego dibujamos los cuadros y números
                for letra in letras:
                    x, y = letra["pos"]
                    temp_ax.add_patch(patches.Rectangle((x, y), 1, 1, 
                        facecolor=letra["fondo"], edgecolor='black', zorder=4))
                    if (x, y) in recorridos:
                        temp_ax.text(x + 0.5, y + 0.5, str(recorridos[(x, y)]), 
                            ha='center', va='center', color='#b9f4b2', 
                            fontsize=180/tamaño_grilla, weight='bold', zorder=5)
                
            elif modo == "promedios":
                # Versión completa para output actividad promedios
                # Solo cuadros con letras
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
        
        messagebox.showinfo("Éxito", "Imagen exportada correctamente")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al exportar la imagen: {str(e)}")
        return False

def exportar_todas_versiones():
    """Exporta todas las versiones del rompecabezas."""
    directory = filedialog.askdirectory(title="Selecciona carpeta para guardar las imágenes")
    if not directory:
        return False

    try:
        # Exportar versión M (solo letras)
        exportar_imagen("solo_letras", filename=os.path.join(directory, "puzzle_M.png"))
        
        # Exportar versión P (solo números)
        exportar_imagen("solo_numeros", filename=os.path.join(directory, "puzzle_P.png"))
        
        # Exportar versión S (completa con números aqua)
        exportar_imagen("completo_aqua", filename=os.path.join(directory, "puzzle_S.png"))

        # Exportar versión S (completa con números aqua)
        exportar_imagen("promedios", filename=os.path.join(directory, "AD25 #.png"))
        
        messagebox.showinfo("Éxito", "Todas las versiones han sido exportadas correctamente")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al exportar las imágenes: {str(e)}")
        return False


###################################################################################
# Interfaz
root = tk.Tk()
root.title("Editor de Grilla")
root.geometry("1000x700")

# Agregar barra de menú
barra_menu = tk.Menu(root)
root.config(menu=barra_menu)

# Menú Archivo
menu_archivo = tk.Menu(barra_menu, tearoff=0)
barra_menu.add_cascade(label="Archivo", menu=menu_archivo)
menu_archivo.add_command(label="Nuevo", command=crear_grilla)
menu_archivo.add_command(label="Abrir", command=abrir_proyecto, accelerator="Ctrl+O")
menu_archivo.add_command(label="Guardar", command=guardar_proyecto, accelerator="Ctrl+S")
menu_archivo.add_command(label="Guardar como...", command=guardar_como, accelerator="Ctrl+Shift+S")
menu_archivo.add_separator()

# Actualizar el menú Archivo
menu_exportar = tk.Menu(menu_archivo, tearoff=0)
menu_archivo.add_cascade(label="Exportar como", menu=menu_exportar)
menu_exportar.add_command(label="M version", 
    command=lambda: exportar_imagen("solo_letras"))
menu_exportar.add_command(label="P version", 
    command=lambda: exportar_imagen("solo_numeros"))
menu_exportar.add_command(label="S version", 
    command=lambda: exportar_imagen("completo_aqua"))
menu_exportar.add_command(label="Output version", 
    command=lambda: exportar_imagen("promedios"))
menu_exportar.add_separator()
menu_exportar.add_command(label="Exportar todas las versiones", 
    command=lambda: exportar_todas_versiones())

menu_archivo.add_command(label="Importar Promedios", command=lambda: ImportWindow(root))
menu_archivo.add_separator()
menu_archivo.add_command(label="Cerrar", command=root.quit)


panel_controles = tk.Frame(root, width=200, bg="lightgray")
panel_controles.pack(side=tk.LEFT, fill=tk.Y)

tk.Button(panel_controles, text="Agregar Cuadro", command=activar_modo_agregar_cuadro).pack(pady=10, fill=tk.X)
tk.Button(panel_controles, text="Agregar Flecha", command=activar_modo_agregar_flecha).pack(pady=10, fill=tk.X)
tk.Button(panel_controles, text="Eliminar elemento", command=activar_modo_eliminar).pack(pady=10, fill=tk.X)

panel_config_flecha = tk.LabelFrame(panel_controles, text="Config. Flechas", bg="white")
tk.Label(panel_config_flecha, text="Color:", bg="white").pack(anchor="w")
boton_color = tk.Button(panel_config_flecha, bg=config_flecha["color"], command=seleccionar_color)
boton_color.pack(fill=tk.X)

tk.Label(panel_config_flecha, text="Grosor:", bg="white").pack(anchor="w")
scale_grosor = tk.Scale(panel_config_flecha, from_=0.5, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, command=actualizar_config_flecha)
scale_grosor.set(config_flecha["grosor"])
scale_grosor.pack(fill=tk.X)

tk.Label(panel_config_flecha, text="Tamaño Punta:", bg="white").pack(anchor="w")
scale_punta = tk.Scale(panel_config_flecha, from_=0.1, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, command=actualizar_config_flecha)
scale_punta.set(config_flecha["punta"])
scale_punta.pack(fill=tk.X)

tk.Button(panel_config_flecha, text="Guardar Config", command=guardar_nueva_config).pack(pady=5, fill=tk.X)
menu_var = tk.StringVar()
menu_config = tk.OptionMenu(panel_config_flecha, menu_var, "")
menu_config.pack(fill=tk.X)
actualizar_menu_configs()

# Área de dibujo
canvas_frame = tk.Frame(root)
canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
canvas.mpl_connect("button_press_event", manejar_click)

# Iniciar
dibujar_grilla(tamaño_grilla)
actualizar_canvas()
root.bind('<Control-o>', lambda e: abrir_proyecto())
root.bind('<Control-s>', lambda e: guardar_proyecto())
root.bind('<Control-S>', lambda e: guardar_como())
root.mainloop()

