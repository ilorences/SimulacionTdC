import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

# --- Parámetros del sistema ---
V_REF = 220
DT = 0.1
Kp = 0.5

# Variables compartidas
V_in = V_REF
V_out = V_REF
perturbacion_inductiva = 0
perturbacion_electromagnetica = 0

# Historial de datos
tiempo = []
salida_data = []
medicion_data = []
error_data = []
referencia_data = []
perturbacion_ind_data = []
perturbacion_em_data = []

# --- Simulador principal ---
def simulador():
    global V_out, perturbacion_inductiva, perturbacion_electromagnetica, Kp
    t = 0
    while True:
        d_ind = perturbacion_inductiva
        d_em = perturbacion_electromagnetica
        perturbacion_total = d_ind + d_em

        # Resetear perturbaciones (impulsivas)
        if d_ind != 0:
            perturbacion_inductiva = 0
        if d_em != 0:
            perturbacion_electromagnetica = 0

        f = V_out + perturbacion_total  # Medición
        e = V_REF - f                   # Error
        u = Kp * e                      # Control proporcional
        V_out = V_in + u               # Salida corregida

        # Guardar datos
        tiempo.append(t)
        salida_data.append(V_out)
        medicion_data.append(f)
        error_data.append(e)
        referencia_data.append(V_REF)
        perturbacion_ind_data.append(d_ind)
        perturbacion_em_data.append(d_em)

        t += DT
        time.sleep(DT)

# --- Funciones de UI ---
def aplicar_perturbacion_inductiva():
    global perturbacion_inductiva
    perturbacion_inductiva = 20

def aplicar_perturbacion_em():
    global perturbacion_electromagnetica
    perturbacion_electromagnetica = -25

def actualizar_kp(val):
    global Kp
    Kp = float(val)

# --- Animación de gráficos ---
def animar(i):
    window = 100
    min_len = min(len(tiempo), len(salida_data), len(medicion_data), len(error_data),
                  len(referencia_data), len(perturbacion_ind_data), len(perturbacion_em_data), window)

    t = tiempo[-min_len:]

    # Medición
    axes[0].clear()
    axes[0].plot(t, medicion_data[-min_len:], color="blue")
    axes[0].set_title("Medición f(t)")
    axes[0].set_ylim(150, 280)
    axes[0].grid(True)

    # Salida y referencia
    axes[1].clear()
    axes[1].plot(t, referencia_data[-min_len:], '--', color="black", label="Referencia")
    axes[1].plot(t, salida_data[-min_len:], color="green", label="Salida")
    axes[1].set_title("Salida y Referencia")
    axes[1].legend()
    axes[1].set_ylim(150, 280)
    axes[1].grid(True)

    # Error
    axes[2].clear()
    axes[2].plot(t, error_data[-min_len:], color="red")
    axes[2].set_title("Error e(t)")
    axes[2].set_ylim(-100, 100)
    axes[2].grid(True)

    # Perturbaciones
    axes[3].clear()
    axes[3].plot(t, perturbacion_ind_data[-min_len:], color="purple", label="Inductiva")
    axes[3].plot(t, perturbacion_em_data[-min_len:], color="brown", label="Electromagnética")
    axes[3].set_title("Perturbaciones")
    axes[3].legend()
    axes[3].set_ylim(-50, 50)
    axes[3].grid(True)

# --- UI principal ---
ventana = tk.Tk()
ventana.title("Simulador de Estabilizador con Control Proporcional")

# --- Controles superiores (Kp + botones) ---
frame_controles_superiores = ttk.Frame(ventana)
frame_controles_superiores.pack(pady=10)

# Slider Kp
ttk.Label(frame_controles_superiores, text="Ganancia Kp:").pack(side=tk.LEFT)
kp_slider = tk.Scale(frame_controles_superiores, from_=0.0, to=2.0, resolution=0.05,
                     orient=tk.HORIZONTAL, length=200, command=actualizar_kp)
kp_slider.set(Kp)
kp_slider.pack(side=tk.LEFT, padx=10)

# Botones de perturbación
ttk.Button(frame_controles_superiores, text="Perturbación Inductiva (+20V)", command=aplicar_perturbacion_inductiva).pack(side=tk.LEFT, padx=10)
ttk.Button(frame_controles_superiores, text="Perturbación Electromagnética (-25V)", command=aplicar_perturbacion_em).pack(side=tk.LEFT, padx=10)

# --- Área de gráficos ---
frame_graficos = ttk.Frame(ventana)
frame_graficos.pack()

fig, axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
fig.tight_layout(pad=3.0)
canvas = FigureCanvasTkAgg(fig, master=frame_graficos)
canvas.get_tk_widget().pack()

ani = animation.FuncAnimation(fig, animar, interval=100)

# --- Iniciar simulación ---
hilo = threading.Thread(target=simulador, daemon=True)
hilo.start()

ventana.mainloop()
