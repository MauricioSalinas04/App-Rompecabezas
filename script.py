import tkinter as tk
from tkinter import simpledialog, colorchooser
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os

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
    for letra in letras:
        x, y = letra["pos"]
        ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor=letra["fondo"], edgecolor='black', zorder=4))
        ax.text(x + 0.5, y + 0.5, letra["texto"], ha='center', va='center',
                color=letra["color"], fontsize=14, weight='bold', zorder=5)
        key = (x, y)
        if key in recorridos:
            ax.text(x + 0.5, y + 0.2, f"🡺{recorridos[key]}", ha='center', va='center',
                    color='darkgreen', fontsize=10, zorder=6)

def agregar_flechas(flechas):
    for f in flechas:
        x1, y1 = f["origen"]
        x2, y2 = f["destino"]
        config = f["config"]
        direction = f["dir"]
        dx = x2 - x1
        dy = y2 - y1

        if direction == 0:  #Vertical
            yi = 1
            xi = 0.5
        elif direction == 1:
            xi = 1
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
            letras.append({"texto": letra.upper(), "pos": (x, y), "color": "black", "fondo": "lightblue"})
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
            
            if origen_temporal[0] == destino[0]:  # Flecha vertical
                direc = 0
            elif origen_temporal[1] == destino[1]:  # Flecha horizontal
                direc = 1
            
                
            if origen_temporal[0] == destino[0] or origen_temporal[1] == destino[1]:
                flechas.append({
                    "origen": origen_temporal,
                    "destino": destino,
                    "config": config_flecha.copy(),
                    "dir": direc
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

# Interfaz
root = tk.Tk()
root.title("Editor de Grilla")
root.geometry("1000x700")

panel_controles = tk.Frame(root, width=200, bg="lightgray")
panel_controles.pack(side=tk.LEFT, fill=tk.Y)

tk.Button(panel_controles, text="Crear Grilla", command=crear_grilla).pack(pady=10, fill=tk.X)
tk.Button(panel_controles, text="Agregar Cuadro", command=activar_modo_agregar_cuadro).pack(pady=10, fill=tk.X)
tk.Button(panel_controles, text="Agregar Flecha", command=activar_modo_agregar_flecha).pack(pady=10, fill=tk.X)

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
root.mainloop()

