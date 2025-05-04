import tkinter as tk
from tkinter import simpledialog
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

fig, ax = plt.subplots(figsize=(6, 6))
canvas = None
tamaño_grilla = 8
letras = []
flechas = []
modo_actual = None
origen_temporal = None
recorridos = {}  # clave: (x, y), valor: cantidad total de celdas recorridas

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
        ax.annotate("", xy=(x2 + 0.5, y2 + 0.5), xytext=(x1 + 0.5, y1 + 0.5),
                    arrowprops=dict(arrowstyle="->", color='red', lw=1.5), zorder=3)

def actualizar_canvas():
    ax.set_xlim(0, tamaño_grilla)
    ax.set_ylim(0, tamaño_grilla)
    ax.set_aspect('equal')
    ax.set_xticks(range(tamaño_grilla + 1))
    ax.set_yticks(range(tamaño_grilla + 1))
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    ax.set_frame_on(True)
    canvas.draw()

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

def activar_modo_agregar_flecha():
    global modo_actual, origen_temporal
    modo_actual = 'agregar_flecha'
    origen_temporal = None

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
            # Validar que sea en la misma fila o columna
            if origen_temporal[0] == destino[0] or origen_temporal[1] == destino[1]:
                flechas.append({"origen": origen_temporal, "destino": destino})

                # Calcular cantidad de celdas recorridas
                recorrido = abs(destino[0] - origen_temporal[0]) + abs(destino[1] - origen_temporal[1])
                if origen_temporal in recorridos:
                    recorridos[origen_temporal] += recorrido
                else:
                    recorridos[origen_temporal] = recorrido

                origen_temporal = None
                dibujar_grilla(tamaño_grilla)
                agregar_letras(letras)
                agregar_flechas(flechas)
                actualizar_canvas()
            else:
                print("Solo se permiten flechas horizontales o verticales.")
                origen_temporal = None

# Interfaz
root = tk.Tk()
root.title("Editor de Grilla")
root.geometry("1000x700")

panel_controles = tk.Frame(root, width=200, bg="lightgray")
panel_controles.pack(side=tk.LEFT, fill=tk.Y)

tk.Button(panel_controles, text="Crear Grilla", command=crear_grilla).pack(pady=10, fill=tk.X)
tk.Button(panel_controles, text="Agregar Cuadro", command=activar_modo_agregar_cuadro).pack(pady=10, fill=tk.X)
tk.Button(panel_controles, text="Agregar Flecha", command=activar_modo_agregar_flecha).pack(pady=10, fill=tk.X)

canvas_frame = tk.Frame(root)
canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

canvas.mpl_connect("button_press_event", manejar_click)

dibujar_grilla(tamaño_grilla)
actualizar_canvas()

root.mainloop()
