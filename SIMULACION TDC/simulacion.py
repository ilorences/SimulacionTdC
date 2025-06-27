import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading
import time

# --- Parámetros iniciales ---
V_REF = 220
DT = 0.1

# Variables compartidas
V_in = V_REF
V_out = V_REF
perturbacion_pendiente = 0
Kp = 0.5  # Ganancia proporcional inicial

tiempo = []
entrada_data = []
salida_data = []
medicion_data = []
error_data = []
perturbacion_data = []
referencia_data = []

# --- Simulación con controlador proporcional ---
def simulador():
    global V_in, V_out, perturbacion_pendiente, Kp

    t = 0
    while True:
        d = perturbacion_pendiente
        if d != 0:
            V_out += d
            perturbacion_pendiente = 0

        f = V_out
        e = V_REF - f
        u = Kp * e

        V_out = V_in + u

        # Guardar datos
        tiempo.append(t)
        entrada_data.append(V_in)
        salida_data.append(V_out)
        medicion_data.append(f)
        error_data.append(e)
        perturbacion_data.append(d)
        referencia_data.append(V_REF)

        t += DT
        time.sleep(DT)

# --- UI: aplicar perturbación ---
def aplicar_perturbacion():
    global perturbacion_pendiente
    try:
        perturbacion_pendiente = float(entry_perturbacion.get())
        entry_perturbacion.delete(0, tk.END)
    except ValueError:
        entry_perturbacion.delete(0, tk.END)
        entry_perturbacion.insert(0, "Entrada inválida")

# --- Slider Kp ---
def actualizar_kp(val):
    global Kp
    Kp = float(val)

# --- Animación del gráfico ---
def animar(i):
    ax.clear()
    ax.plot(tiempo[-100:], referencia_data[-100:], label="Referencia r(t)", color="black", linestyle="--")
    ax.plot(tiempo[-100:], entrada_data[-100:], label="Entrada", color="orange")
    ax.plot(tiempo[-100:], salida_data[-100:], label="Salida y(t)", color="green")
    ax.plot(tiempo[-100:], medicion_data[-100:], label="Medición f(t)", color="blue")
    ax.plot(tiempo[-100:], error_data[-100:], label="Error e(t)", color="red")
    ax.plot(tiempo[-100:], perturbacion_data[-100:], label="Perturbación d(t)", color="purple")

    ax.set_ylim(150, 280)
    ax.set_title(f"Control Proporcional | Kp = {Kp:.2f}")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Voltaje (V)")
    ax.legend(loc="upper right")
    ax.grid(True)

# --- Interfaz gráfica ---
ventana = tk.Tk()
ventana.title("Simulador de Estabilizador con Control Proporcional")

frame = ttk.Frame(ventana)
frame.pack()

fig, ax = plt.subplots(figsize=(10, 5))
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.get_tk_widget().pack()

ani = animation.FuncAnimation(fig, animar, interval=100)

# Perturbación manual
input_frame = ttk.Frame(ventana)
input_frame.pack(pady=5)
ttk.Label(input_frame, text="Perturbación (ej: +30 o -40):").pack(side=tk.LEFT)
entry_perturbacion = ttk.Entry(input_frame, width=10)
entry_perturbacion.pack(side=tk.LEFT, padx=5)
ttk.Button(input_frame, text="Aplicar", command=aplicar_perturbacion).pack(side=tk.LEFT)

# Slider de Kp
slider_frame = ttk.Frame(ventana)
slider_frame.pack(pady=10)
ttk.Label(slider_frame, text="Kp:").pack(side=tk.LEFT)
kp_slider = tk.Scale(slider_frame, from_=0.0, to=2.0, resolution=0.05,
                     orient=tk.HORIZONTAL, length=200, command=actualizar_kp)
kp_slider.set(Kp)
kp_slider.pack(side=tk.LEFT)

# --- Hilo de simulación ---
hilo = threading.Thread(target=simulador, daemon=True)
hilo.start()

ventana.mainloop()
