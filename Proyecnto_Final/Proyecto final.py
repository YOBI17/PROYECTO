"""
sistema_completo.py
Sistema de Gestión de Mantenimiento Eléctrico (Proyecto 769)
Introducción a la Programación y Computación 1 - USAC

Versión en un solo archivo (clases + almacenamiento + interfaz + main).
Ejecutar:  python sistema_completo.py
Los datos se guardan en la carpeta datos/ junto a este archivo.
"""

import math
import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox


# ==========================================================================
# 1. CLASES (POO)
# ==========================================================================

class Equipo:
    """Equipo eléctrico registrado en el sistema."""

    def __init__(self, id_equipo, nombre, ubicacion, estado):
        self.id_equipo = id_equipo
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.estado = estado

    def __str__(self):
        return f"{self.id_equipo} - {self.nombre} ({self.ubicacion}) [{self.estado}]"

    def __repr__(self):
        return (f"Equipo(id_equipo={self.id_equipo!r}, nombre={self.nombre!r}, "
                f"ubicacion={self.ubicacion!r}, estado={self.estado!r})")


class Mantenimiento:
    """Clase base para cualquier tipo de mantenimiento."""

    TIPO = "General"

    def __init__(self, id_mantenimiento, id_equipo, codigo_servicio, fecha, costo):
        self.id_mantenimiento = id_mantenimiento
        self.id_equipo = id_equipo
        self.codigo_servicio = codigo_servicio
        self.fecha = fecha
        self.costo = costo

    def tipo(self):
        """Nombre del tipo de mantenimiento (se redefine en las clases hijas)."""
        return self.TIPO

    def detalle(self):
        """Texto con el dato propio de cada tipo (polimorfismo)."""
        return ""

    def __str__(self):
        return (f"[{self.tipo()}] {self.id_mantenimiento} | equipo {self.id_equipo} | "
                f"servicio {self.codigo_servicio} | {self.fecha} | Q{self.costo:.2f}")


class MantenimientoPreventivo(Mantenimiento):
    """Mantenimiento programado que se repite cada cierto número de días."""

    TIPO = "Preventivo"

    def __init__(self, id_mantenimiento, id_equipo, codigo_servicio, fecha, costo,
                 frecuencia_dias):
        super().__init__(id_mantenimiento, id_equipo, codigo_servicio, fecha, costo)
        self.frecuencia_dias = frecuencia_dias

    def detalle(self):
        return f"Cada {self.frecuencia_dias} días"


class MantenimientoCorrectivo(Mantenimiento):
    """Mantenimiento para reparar una falla, con su diagnóstico."""

    TIPO = "Correctivo"

    def __init__(self, id_mantenimiento, id_equipo, codigo_servicio, fecha, costo,
                 diagnostico):
        super().__init__(id_mantenimiento, id_equipo, codigo_servicio, fecha, costo)
        self.diagnostico = diagnostico

    def detalle(self):
        return self.diagnostico


# ==========================================================================
# 2. ALMACENAMIENTO (archivos .txt con delimitador |)
# ==========================================================================

SEPARADOR = "|"
ENCODING = "utf-8"

# La carpeta datos/ se ubica junto a este archivo, sin importar desde dónde
# se ejecute el programa.
DIRECTORIO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")

ARCHIVO_EQUIPOS = "equipos.txt"
ARCHIVO_PREVENTIVOS = "preventivos.txt"
ARCHIVO_CORRECTIVOS = "correctivos.txt"


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------
def _ruta(nombre_archivo):
    """Devuelve la ruta completa de un archivo dentro de datos/."""
    return os.path.join(DIRECTORIO_DATOS, nombre_archivo)


def _limpiar(valor):
    """Convierte a texto y elimina caracteres que romperían el formato."""
    texto = str(valor)
    texto = texto.replace(SEPARADOR, "/")
    texto = texto.replace("\r", " ").replace("\n", " ")
    return texto.strip()


def _guardar_linea(nombre_archivo, campos):
    """Agrega un registro al final del archivo. Retorna True si tuvo éxito."""
    if not asegurar_directorio():
        return False
    linea = SEPARADOR.join(_limpiar(c) for c in campos)
    try:
        with open(_ruta(nombre_archivo), "a", encoding=ENCODING) as archivo:
            archivo.write(linea + "\n")
        return True
    except OSError as error:
        print(f"[almacenamiento] No se pudo escribir en {nombre_archivo}: {error}")
        return False


def _cargar_registros(nombre_archivo, n_campos, construir):
    """
    Lee un archivo y construye objetos con la función `construir(partes)`.
    - Si el archivo no existe, retorna lista vacía (sin error).
    - Las líneas vacías se ignoran.
    - Las líneas corruptas se omiten con un aviso, sin detener la carga.
    """
    registros = []
    try:
        with open(_ruta(nombre_archivo), "r", encoding=ENCODING) as archivo:
            for numero, linea in enumerate(archivo, start=1):
                linea = linea.strip()
                if not linea:
                    continue
                partes = linea.split(SEPARADOR)
                if len(partes) != n_campos:
                    print(f"[almacenamiento] {nombre_archivo}, línea {numero}: "
                          f"se esperaban {n_campos} campos y hay {len(partes)}. Se omite.")
                    continue
                try:
                    registros.append(construir(partes))
                except (ValueError, TypeError) as error:
                    print(f"[almacenamiento] {nombre_archivo}, línea {numero}: "
                          f"datos inválidos ({error}). Se omite.")
    except FileNotFoundError:
        return []
    except OSError as error:
        print(f"[almacenamiento] No se pudo leer {nombre_archivo}: {error}")
        return []
    return registros


# ---------------------------------------------------------------------------
# Directorio
# ---------------------------------------------------------------------------
def asegurar_directorio():
    """Crea la carpeta datos/ si no existe. Retorna True si está disponible."""
    try:
        os.makedirs(DIRECTORIO_DATOS, exist_ok=True)
        return True
    except OSError as error:
        print(f"[almacenamiento] No se pudo crear la carpeta de datos: {error}")
        return False


# ---------------------------------------------------------------------------
# Equipos
# ---------------------------------------------------------------------------
def guardar_equipo(equipo):
    """Guarda un objeto Equipo. Retorna True/False según el resultado."""
    return _guardar_linea(ARCHIVO_EQUIPOS, [
        equipo.id_equipo, equipo.nombre, equipo.ubicacion, equipo.estado,
    ])


def cargar_equipos():
    """Retorna una lista de objetos Equipo leídos de equipos.txt."""
    return _cargar_registros(
        ARCHIVO_EQUIPOS, 4,
        lambda p: Equipo(id_equipo=p[0], nombre=p[1], ubicacion=p[2], estado=p[3]),
    )


# ---------------------------------------------------------------------------
# Mantenimientos preventivos
# ---------------------------------------------------------------------------
def guardar_preventivo(mantenimiento):
    """Guarda un objeto MantenimientoPreventivo."""
    return _guardar_linea(ARCHIVO_PREVENTIVOS, [
        mantenimiento.id_mantenimiento,
        mantenimiento.id_equipo,
        mantenimiento.codigo_servicio,
        mantenimiento.fecha,
        mantenimiento.costo,
        mantenimiento.frecuencia_dias,
    ])


def cargar_preventivos():
    """Retorna una lista de objetos MantenimientoPreventivo."""
    return _cargar_registros(
        ARCHIVO_PREVENTIVOS, 6,
        lambda p: MantenimientoPreventivo(
            id_mantenimiento=p[0],
            id_equipo=p[1],
            codigo_servicio=p[2],
            fecha=p[3],
            costo=float(p[4]),
            frecuencia_dias=int(p[5]),
        ),
    )


# ---------------------------------------------------------------------------
# Mantenimientos correctivos
# ---------------------------------------------------------------------------
def guardar_correctivo(mantenimiento):
    """Guarda un objeto MantenimientoCorrectivo."""
    return _guardar_linea(ARCHIVO_CORRECTIVOS, [
        mantenimiento.id_mantenimiento,
        mantenimiento.id_equipo,
        mantenimiento.codigo_servicio,
        mantenimiento.fecha,
        mantenimiento.costo,
        mantenimiento.diagnostico,
    ])


def cargar_correctivos():
    """Retorna una lista de objetos MantenimientoCorrectivo."""
    return _cargar_registros(
        ARCHIVO_CORRECTIVOS, 6,
        lambda p: MantenimientoCorrectivo(
            id_mantenimiento=p[0],
            id_equipo=p[1],
            codigo_servicio=p[2],
            fecha=p[3],
            costo=float(p[4]),
            diagnostico=p[5],
        ),
    )


# ==========================================================================
# 3. INTERFAZ GRÁFICA (Tkinter)
# ==========================================================================

TITULO = "Sistema de Gestión de Mantenimiento Eléctrico"

CATALOGO_PREVENTIVO = {
    "P01": "Inspección visual general",
    "P02": "Limpieza de contactos y terminales",
    "P03": "Ajuste de conexiones",
    "P04": "Medición de aislamiento",
    "P05": "Lubricación y revisión mecánica",
}

CATALOGO_CORRECTIVO = {
    "C01": "Reemplazo de fusible o interruptor",
    "C02": "Reparación de cableado",
    "C03": "Cambio de componente dañado",
    "C04": "Reparación de motor",
    "C05": "Reemplazo completo del equipo",
}

ESTADOS = ["Operativo", "En mantenimiento", "Fuera de servicio"]

COLOR_PRINCIPAL = "#1f3a5f"
COLOR_ACENTO = "#f2a900"


class Aplicacion(tk.Tk):
    """Ventana principal de la aplicación."""

    def __init__(self):
        super().__init__()
        self.title(TITULO)
        self.geometry("1020x700")
        self.minsize(940, 640)

        self._configurar_estilos()

        # Carga inicial de datos desde los archivos .txt
        asegurar_directorio()
        self.equipos = cargar_equipos()
        self.preventivos = cargar_preventivos()
        self.correctivos = cargar_correctivos()

        self.form = {}               # widgets de los formularios de mantenimiento
        self._mapa_equipos = {}      # texto del combo -> id_equipo

        self.marco_bienvenida = self._crear_bienvenida()
        self.marco_principal = self._crear_principal()
        self._mostrar(self.marco_bienvenida)

    # ------------------------------------------------------------------
    # Estilos y navegación
    # ------------------------------------------------------------------
    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("Treeview", rowheight=24)
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        estilo.configure("Acceso.TButton", font=("Segoe UI", 14, "bold"), padding=12)
        estilo.configure("Registrar.TButton", font=("Segoe UI", 10, "bold"), padding=6)

    def _mostrar(self, marco):
        self.marco_bienvenida.pack_forget()
        self.marco_principal.pack_forget()
        marco.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Pantalla de bienvenida
    # ------------------------------------------------------------------
    def _crear_bienvenida(self):
        marco = tk.Frame(self, bg=COLOR_PRINCIPAL)
        centro = tk.Frame(marco, bg=COLOR_PRINCIPAL)
        centro.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(centro, text="⚡", font=("Segoe UI Emoji", 54),
                 bg=COLOR_PRINCIPAL, fg=COLOR_ACENTO).pack(pady=(0, 10))
        tk.Label(centro, text=TITULO, font=("Segoe UI", 26, "bold"),
                 bg=COLOR_PRINCIPAL, fg="white", wraplength=800,
                 justify="center").pack(pady=(0, 10))
        tk.Label(centro, text="Proyecto 769 · Introducción a la Programación y Computación 1 · USAC",
                 font=("Segoe UI", 12), bg=COLOR_PRINCIPAL, fg="#d0d9e6").pack(pady=(0, 35))
        ttk.Button(centro, text="Ingresar al sistema", style="Acceso.TButton",
                   command=lambda: self._mostrar(self.marco_principal)).pack()
        return marco

    # ------------------------------------------------------------------
    # Ventana principal con pestañas
    # ------------------------------------------------------------------
    def _crear_principal(self):
        marco = ttk.Frame(self)

        cabecera = tk.Frame(marco, bg=COLOR_PRINCIPAL)
        cabecera.pack(fill="x")
        tk.Label(cabecera, text=TITULO, font=("Segoe UI", 15, "bold"),
                 bg=COLOR_PRINCIPAL, fg="white").pack(side="left", padx=15, pady=10)
        ttk.Button(cabecera, text="Volver al inicio",
                   command=lambda: self._mostrar(self.marco_bienvenida)).pack(
            side="right", padx=15, pady=10)

        self.notebook = ttk.Notebook(marco)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        tab_equipos = ttk.Frame(self.notebook)
        tab_prev = ttk.Frame(self.notebook)
        tab_corr = ttk.Frame(self.notebook)
        tab_hist = ttk.Frame(self.notebook)
        self.notebook.add(tab_equipos, text="  Equipos  ")
        self.notebook.add(tab_prev, text="  Mantenimiento Preventivo  ")
        self.notebook.add(tab_corr, text="  Mantenimiento Correctivo  ")
        self.notebook.add(tab_hist, text="  Historial General  ")

        self._crear_tab_equipos(tab_equipos)
        self._crear_tab_mantenimiento(tab_prev, "preventivo")
        self._crear_tab_mantenimiento(tab_corr, "correctivo")
        self._crear_tab_historial(tab_hist)

        self._refrescar_todo()
        return marco

    # ------------------------------------------------------------------
    # Helpers de widgets
    # ------------------------------------------------------------------
    @staticmethod
    def _entrada(padre, texto, fila):
        ttk.Label(padre, text=texto).grid(row=fila, column=0, sticky="w", padx=5, pady=4)
        entrada = ttk.Entry(padre, width=32)
        entrada.grid(row=fila, column=1, sticky="w", padx=5, pady=4)
        return entrada

    @staticmethod
    def _combo(padre, texto, fila, valores):
        ttk.Label(padre, text=texto).grid(row=fila, column=0, sticky="w", padx=5, pady=4)
        combo = ttk.Combobox(padre, values=valores, state="readonly", width=40)
        combo.grid(row=fila, column=1, sticky="w", padx=5, pady=4)
        return combo

    @staticmethod
    def _crear_tabla(padre, columnas, anchos):
        contenedor = ttk.Frame(padre)
        contenedor.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        tabla = ttk.Treeview(contenedor, columns=columnas, show="headings")
        for columna, ancho in zip(columnas, anchos):
            tabla.heading(columna, text=columna)
            tabla.column(columna, width=ancho, anchor="w")
        barra = ttk.Scrollbar(contenedor, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return tabla

    @staticmethod
    def _llenar_tabla(tabla, filas):
        tabla.delete(*tabla.get_children())
        for fila in filas:
            tabla.insert("", "end", values=fila)

    # ------------------------------------------------------------------
    # Pestaña: Equipos
    # ------------------------------------------------------------------
    def _crear_tab_equipos(self, tab):
        form = ttk.LabelFrame(tab, text="Registrar equipo", padding=12)
        form.pack(fill="x", padx=10, pady=10)

        self.e_id = self._entrada(form, "ID del equipo:", 0)
        self.e_nombre = self._entrada(form, "Nombre:", 1)
        self.e_ubicacion = self._entrada(form, "Ubicación:", 2)
        self.c_estado = self._combo(form, "Estado:", 3, ESTADOS)
        self.c_estado.configure(width=30)

        ttk.Button(form, text="Registrar equipo", style="Registrar.TButton",
                   command=self._registrar_equipo).grid(
            row=4, column=0, columnspan=2, pady=(10, 0))

        ttk.Label(tab, text="Equipos registrados",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12)
        self.tabla_equipos = self._crear_tabla(
            tab, ("ID", "Nombre", "Ubicación", "Estado"), (120, 280, 280, 160))

    def _registrar_equipo(self):
        id_equipo = self.e_id.get().strip()
        nombre = self.e_nombre.get().strip()
        ubicacion = self.e_ubicacion.get().strip()
        estado = self.c_estado.get().strip()

        if not (id_equipo and nombre and ubicacion and estado):
            messagebox.showerror("Campos vacíos", "Complete todos los campos antes de registrar.")
            return
        if any("|" in texto for texto in (id_equipo, nombre, ubicacion)):
            messagebox.showerror("Carácter no permitido", "No se puede usar el carácter '|'.")
            return
        if any(e.id_equipo == id_equipo for e in self.equipos):
            messagebox.showerror("ID duplicado", f"Ya existe un equipo con el ID '{id_equipo}'.")
            return

        equipo = Equipo(id_equipo, nombre, ubicacion, estado)
        if not guardar_equipo(equipo):
            messagebox.showerror("Error de archivo", "No se pudo guardar el equipo en el archivo.")
            return

        self.equipos.append(equipo)
        self._refrescar_todo()

        # Limpieza de campos tras el registro exitoso
        for entrada in (self.e_id, self.e_nombre, self.e_ubicacion):
            entrada.delete(0, "end")
        self.c_estado.set("")
        messagebox.showinfo("Registro exitoso", "El equipo fue registrado correctamente.")

    # ------------------------------------------------------------------
    # Pestañas: Mantenimiento preventivo / correctivo (misma estructura)
    # ------------------------------------------------------------------
    def _crear_tab_mantenimiento(self, tab, tipo):
        es_prev = tipo == "preventivo"
        catalogo = CATALOGO_PREVENTIVO if es_prev else CATALOGO_CORRECTIVO
        titulo = "Registrar mantenimiento preventivo" if es_prev else "Registrar mantenimiento correctivo"

        form = ttk.LabelFrame(tab, text=titulo, padding=12)
        form.pack(fill="x", padx=10, pady=10)

        w = {}
        w["id"] = self._entrada(form, "ID del mantenimiento:", 0)
        w["equipo"] = self._combo(form, "Equipo:", 1, [])
        w["servicio"] = self._combo(
            form, "Servicio:", 2, [f"{cod} - {desc}" for cod, desc in catalogo.items()])
        w["fecha"] = self._entrada(form, "Fecha (AAAA-MM-DD):", 3)
        w["costo"] = self._entrada(form, "Costo (Q):", 4)
        etiqueta_extra = "Frecuencia (días):" if es_prev else "Diagnóstico:"
        w["extra"] = self._entrada(form, etiqueta_extra, 5)
        if not es_prev:
            w["extra"].configure(width=60)

        ttk.Button(form, text="Registrar mantenimiento", style="Registrar.TButton",
                   command=lambda: self._registrar_mantenimiento(tipo)).grid(
            row=6, column=0, columnspan=2, pady=(10, 0))

        ttk.Label(tab, text="Mantenimientos registrados",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12)
        if es_prev:
            columnas = ("ID", "Equipo", "Servicio", "Fecha", "Costo (Q)", "Frecuencia (días)")
            anchos = (90, 110, 280, 110, 110, 130)
        else:
            columnas = ("ID", "Equipo", "Servicio", "Fecha", "Costo (Q)", "Diagnóstico")
            anchos = (90, 110, 250, 110, 110, 260)
        w["tabla"] = self._crear_tabla(tab, columnas, anchos)
        self.form[tipo] = w

    def _registrar_mantenimiento(self, tipo):
        es_prev = tipo == "preventivo"
        w = self.form[tipo]

        id_mant = w["id"].get().strip()
        texto_equipo = w["equipo"].get().strip()
        texto_servicio = w["servicio"].get().strip()
        fecha = w["fecha"].get().strip()
        texto_costo = w["costo"].get().strip()
        extra = w["extra"].get().strip()

        # --- Validaciones: campos vacíos ---
        if not (id_mant and texto_equipo and texto_servicio and fecha and texto_costo and extra):
            messagebox.showerror("Campos vacíos", "Complete todos los campos antes de registrar.")
            return
        if any("|" in texto for texto in (id_mant, extra)):
            messagebox.showerror("Carácter no permitido", "No se puede usar el carácter '|'.")
            return

        # --- Validaciones: ID único (entre preventivos y correctivos) ---
        ids_usados = {m.id_mantenimiento for m in self.preventivos + self.correctivos}
        if id_mant in ids_usados:
            messagebox.showerror("ID duplicado",
                                 f"Ya existe un mantenimiento con el ID '{id_mant}'.")
            return

        # --- Validaciones: fecha ---
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Fecha inválida",
                                 "Use el formato AAAA-MM-DD con una fecha real (ej. 2026-03-15).")
            return

        # --- Validaciones: costo numérico ---
        try:
            costo = float(texto_costo.replace(",", "."))
            if not math.isfinite(costo) or costo < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Costo inválido", "El costo debe ser un número mayor o igual a 0.")
            return

        # --- Validaciones: frecuencia numérica (solo preventivo) ---
        frecuencia = None
        if es_prev:
            try:
                frecuencia = int(extra)
                if frecuencia <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Frecuencia inválida",
                                     "La frecuencia debe ser un número entero mayor que 0.")
                return

        id_equipo = self._mapa_equipos.get(texto_equipo)
        if id_equipo is None:
            messagebox.showerror("Equipo inválido", "Seleccione un equipo de la lista.")
            return
        codigo = texto_servicio.split(" - ", 1)[0]

        if es_prev:
            mantenimiento = MantenimientoPreventivo(id_mant, id_equipo, codigo, fecha, costo, frecuencia)
            guardado = guardar_preventivo(mantenimiento)
        else:
            mantenimiento = MantenimientoCorrectivo(id_mant, id_equipo, codigo, fecha, costo, extra)
            guardado = guardar_correctivo(mantenimiento)

        if not guardado:
            messagebox.showerror("Error de archivo",
                                 "No se pudo guardar el mantenimiento en el archivo.")
            return

        (self.preventivos if es_prev else self.correctivos).append(mantenimiento)
        self._refrescar_todo()

        # Limpieza de campos tras el registro exitoso
        for clave in ("id", "fecha", "costo", "extra"):
            w[clave].delete(0, "end")
        w["equipo"].set("")
        w["servicio"].set("")
        messagebox.showinfo("Registro exitoso", "El mantenimiento fue registrado correctamente.")

    # ------------------------------------------------------------------
    # Pestaña: Historial general
    # ------------------------------------------------------------------
    def _crear_tab_historial(self, tab):
        ttk.Label(tab, text="Historial general de servicios",
                  font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(12, 6))
        self.tabla_historial = self._crear_tabla(
            tab, ("Tipo", "ID", "Equipo", "Servicio", "Fecha", "Costo (Q)", "Detalle"),
            (95, 90, 190, 230, 100, 100, 200))
        self.lbl_totales = ttk.Label(tab, text="", font=("Segoe UI", 10, "bold"))
        self.lbl_totales.pack(anchor="e", padx=14, pady=(0, 10))

    # ------------------------------------------------------------------
    # Actualización de tablas y combos
    # ------------------------------------------------------------------
    def _refrescar_todo(self):
        nombres = {e.id_equipo: e.nombre for e in self.equipos}

        # Combos de equipos en los formularios de mantenimiento
        self._mapa_equipos = {f"{e.id_equipo} - {e.nombre}": e.id_equipo for e in self.equipos}
        for tipo in self.form:
            self.form[tipo]["equipo"].configure(values=list(self._mapa_equipos.keys()))

        # Tabla de equipos
        self._llenar_tabla(
            self.tabla_equipos,
            [(e.id_equipo, e.nombre, e.ubicacion, e.estado) for e in self.equipos])

        # Tablas de mantenimiento
        if "preventivo" in self.form:
            self._llenar_tabla(self.form["preventivo"]["tabla"], [
                (m.id_mantenimiento, m.id_equipo,
                 f"{m.codigo_servicio} - {CATALOGO_PREVENTIVO.get(m.codigo_servicio, '')}",
                 m.fecha, f"{m.costo:,.2f}", m.frecuencia_dias)
                for m in self.preventivos])
        if "correctivo" in self.form:
            self._llenar_tabla(self.form["correctivo"]["tabla"], [
                (m.id_mantenimiento, m.id_equipo,
                 f"{m.codigo_servicio} - {CATALOGO_CORRECTIVO.get(m.codigo_servicio, '')}",
                 m.fecha, f"{m.costo:,.2f}", m.diagnostico)
                for m in self.correctivos])

        # Historial general (ordenado por fecha)
        todos = sorted(self.preventivos + self.correctivos, key=lambda m: m.fecha)
        catalogo = {**CATALOGO_PREVENTIVO, **CATALOGO_CORRECTIVO}
        self._llenar_tabla(self.tabla_historial, [
            (m.tipo(), m.id_mantenimiento,
             f"{m.id_equipo} - {nombres.get(m.id_equipo, 'Equipo no registrado')}",
             f"{m.codigo_servicio} - {catalogo.get(m.codigo_servicio, '')}",
             m.fecha, f"{m.costo:,.2f}", m.detalle())
            for m in todos])

        total = sum(m.costo for m in todos)
        self.lbl_totales.configure(
            text=f"Servicios registrados: {len(todos)}    |    Costo total: Q{total:,.2f}")


def iniciar_aplicacion():
    """Crea la ventana principal y arranca el ciclo de eventos de Tkinter."""
    app = Aplicacion()
    app.mainloop()


# ==========================================================================
# 4. PUNTO DE ENTRADA
# ==========================================================================

def main():
    iniciar_aplicacion()


if __name__ == "__main__":
    main()