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

# Amplitudes de perturbaciones (modificables)
amplitud_inductiva = 10
amplitud_em = -10

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
    perturbacion_inductiva = amplitud_inductiva

def aplicar_perturbacion_em():
    global perturbacion_electromagnetica
    perturbacion_electromagnetica = amplitud_em

def actualizar_kp(val):
    global Kp
    Kp = float(val)

def actualizar_amplitud_ind(val):
    global amplitud_inductiva
    amplitud_inductiva = float(val)

def actualizar_amplitud_em(val):
    global amplitud_em
    amplitud_em = float(val)

# --- Animación de gráficos ---
def animar(i):
    window = 2000  # Aumentamos ventana de tiempo
    min_len = min(len(tiempo), window)

    t = tiempo[-min_len:]

    # Medición
    axes[0].clear()
    axes[0].plot(t, medicion_data[-min_len:], color="blue")
    axes[0].set_title("Medición f(t)")
    axes[0].set_ylim(180, 260)
    axes[0].grid(True)

    # Salida y referencia
    axes[1].clear()
    axes[1].plot(t, referencia_data[-min_len:], '--', color="black", label="Referencia")
    axes[1].plot(t, salida_data[-min_len:], color="green", label="Salida")
    axes[1].set_title("Salida y Referencia")
    axes[1].legend()
    axes[1].set_ylim(190, 250)
    axes[1].grid(True)

    # Error con área ±8% de 220
    axes[2].clear()
    axes[2].plot(t, error_data[-min_len:], color="red", label="Error e(t)")
    tolerancia = 0.08 * V_REF
    axes[2].fill_between(t, -tolerancia, tolerancia, color='gray', alpha=0.3, label="±8% tolerancia")
    axes[2].set_title("Error e(t)")
    axes[2].set_ylim(-20, 20)
    axes[2].legend()
    axes[2].grid(True)

    # Perturbaciones
    axes[3].clear()
    axes[3].plot(t, perturbacion_ind_data[-min_len:], color="purple", label="Inductiva")
    axes[3].plot(t, perturbacion_em_data[-min_len:], color="brown", label="Electromagnética")
    axes[3].set_title("Perturbaciones")
    axes[3].legend()
    axes[3].set_ylim(-25, 25)
    axes[3].grid(True)

# --- UI principal ---
ventana = tk.Tk()
ventana.title("Simulador de Estabilizador con Control Proporcional")

# --- Controles superiores ---
frame_controles_superiores = ttk.Frame(ventana)
frame_controles_superiores.pack(pady=10)

# Kp
ttk.Label(frame_controles_superiores, text="Ganancia Kp:").pack(side=tk.LEFT)
kp_slider = tk.Scale(frame_controles_superiores, from_=0.0, to=2.0, resolution=0.05,
                     orient=tk.HORIZONTAL, length=150, command=actualizar_kp)
kp_slider.set(Kp)
kp_slider.pack(side=tk.LEFT, padx=10)

# Botones de perturbación
ttk.Button(frame_controles_superiores, text="Pert. Inductiva", command=aplicar_perturbacion_inductiva).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_controles_superiores, text="Pert. EM", command=aplicar_perturbacion_em).pack(side=tk.LEFT, padx=5)

# --- Sliders para amplitudes ---
frame_amplitudes = ttk.Frame(ventana)
frame_amplitudes.pack(pady=5)

# Slider inductiva
ttk.Label(frame_amplitudes, text="Amplitud Inductiva (+V):").pack(side=tk.LEFT)
slider_ind = tk.Scale(frame_amplitudes, from_=0, to=50, resolution=1,
                      orient=tk.HORIZONTAL, length=150, command=actualizar_amplitud_ind)
slider_ind.set(amplitud_inductiva)
slider_ind.pack(side=tk.LEFT, padx=5)

# Slider electromagnética
ttk.Label(frame_amplitudes, text="Amplitud EM (-V):").pack(side=tk.LEFT)
slider_em = tk.Scale(frame_amplitudes, from_=-50, to=0, resolution=1,
                     orient=tk.HORIZONTAL, length=150, command=actualizar_amplitud_em)
slider_em.set(amplitud_em)
slider_em.pack(side=tk.LEFT, padx=5)

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
