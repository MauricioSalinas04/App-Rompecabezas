import tkinter as tk
from tkinter import simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches

# Lógica de dibujo
def dibujar_grilla(ax, tamaño):
    for x in range(tamaño + 1):
        ax.plot([x, x], [0, tamaño], color='black', linewidth=0.5, zorder=0)
    for y in range(tamaño + 1):
        ax.plot([0, tamaño], [y, y], color='black', linewidth=0.5, zorder=0)

def agregar_letras(ax, letras):
    for letra in letras:
        x, y = letra["pos"]
        ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor=letra["fondo"], edgecolor='black', zorder=4))
        ax.text(x + 0.5, y + 0.5, letra["texto"], ha='center', va='center',
                color=letra["color"], fontsize=14, weight='bold', zorder=5)

def agregar_flechas(ax, flechas):
    for flecha in flechas:
        x, y = flecha["inicio"]
        dx, dy = flecha["delta"]
        ax.arrow(x + 0.5, y + 0.5, dx, dy, width=flecha["grosor"],
                 head_width=flecha["cabeza"], head_length=flecha["cabeza"],
                 fc=flecha["color"], ec=flecha["color"], zorder=flecha.get("z", 3), length_includes_head=True)

# Función principal para actualizar el gráfico
def crear_grilla():
    tamaño = simpledialog.askinteger("Crear Grilla", "Tamaño de la grilla:", minvalue=2, maxvalue=20)
    if tamaño is None:
        return

    ax.clear()
    dibujar_grilla(ax, tamaño)
    agregar_letras(ax, letras)
    agregar_flechas(ax, flechas)
    ax.set_xlim(0, tamaño)
    ax.set_ylim(0, tamaño)
    ax.set_aspect('equal')
    ax.set_xticks(range(tamaño + 1))
    ax.set_yticks(range(tamaño + 1))
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    fig.tight_layout()
    canvas.draw()

# Datos de prueba
letras = [
    {"texto": "A", "pos": (3, 4), "color": "white", "fondo": "black"},
    {"texto": "B", "pos": (1, 6), "color": "white", "fondo": "black"},
    {"texto": "C", "pos": (6, 2), "color": "white", "fondo": "black"},
]

flechas = [
    {"inicio": (1, 6), "delta": (0, -6), "color": "red", "grosor": 0.08, "cabeza": 0.2, "z": 3},
    {"inicio": (0, 0), "delta": (0, 7.5), "color": "blue", "grosor": 0.3, "cabeza": 0.6, "z": 2},
    {"inicio": (6, 2), "delta": (0, 4.5), "color": "black", "grosor": 0.3, "cabeza": 0.6, "z": 1},
]

# Interfaz gráfica
root = tk.Tk()
root.title("Editor de Grillas")

# Menú
menubar = tk.Menu(root)
grilla_menu = tk.Menu(menubar, tearoff=0)
grilla_menu.add_command(label="Crear Grilla", command=crear_grilla)
menubar.add_cascade(label="Opciones", menu=grilla_menu)
root.config(menu=menubar)

# Área de visualización con matplotlib embebido
fig, ax = plt.subplots(figsize=(6, 6))
ax.axis('off')  # Oculta ejes al inicio
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


# Espacio reservado para el panel de controles
panel_controles = tk.Frame(root, width=200)
panel_controles.pack(side=tk.RIGHT, fill=tk.Y)

root.mainloop()

