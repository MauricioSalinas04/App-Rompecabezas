# Editor de Rompecabezas

Una aplicación de escritorio desarrollada en Python con Tkinter y Matplotlib para crear, editar, guardar y exportar rompecabezas de grillas con letras y flechas.

## Características

- Creación de grillas de tamaño personalizable.
- Agregar cuadros con letras.
- Dibujar flechas entre cuadros.
- Modos de edición: Agregar cuadro, Agregar flecha, Eliminar.
- Guardar y Abrir proyectos en formato `.puzzle` (JSON).
- Exportar el rompecabezas a imágenes PNG en diferentes estilos.

## Instalación

Sigue estos pasos para configurar el entorno de desarrollo y ejecutar la aplicación.

### Prerrequisitos

- Tener instalado [Python 3.8](https://www.python.org/downloads/) o una versión superior.
- Tener instalado [Git](https://git-scm.com/downloads/).

### Pasos

1.  **Clonar el repositorio** (si aún no lo has hecho):
    ```bash
    git clone <URL-DEL-REPOSITORIO>
    cd <NOMBRE-DEL-REPOSITORIO>
    ```

2.  **Crear un entorno virtual:**
    Esto crea una carpeta `env` que contendrá todas las dependencias del proyecto, aislándolas del resto del sistema.
    ```bash
    python -m venv env
    ```
    > **Nota:** La carpeta `env` no debe ser subida al repositorio. El archivo `.gitignore` incluido se encarga de excluirla.

3.  **Activar el entorno virtual:**
    Deberás activar el entorno cada vez que trabajes en el proyecto.

    -   **En Windows (CMD o PowerShell):**
        ```bash
        .\env\Scripts\activate
        ```
    -   **En macOS y Linux:**
        ```bash
        source env/bin/activate
        ```
    Notarás que el nombre del entorno (`env`) aparece al principio de la línea de comandos, indicando que está activo.

4.  **Instalar las dependencias:**
    Este comando lee el archivo `requirements.txt` e instala las librerías necesarias dentro de tu entorno virtual.
    ```bash
    pip install -r requirements.txt
    ```

## Uso

Una vez que el entorno esté activado y las dependencias instaladas, puedes ejecutar la aplicación con el siguiente comando:

```bash
python script.py
```
