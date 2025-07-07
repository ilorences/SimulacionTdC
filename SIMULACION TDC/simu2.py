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
Kd = 0.045

# Valores iniciales
amplitud_inductiva = 10
amplitud_em = -10
V_in = V_REF
simulacion_pausada = False

# Variables compartidas
V_out = V_REF
perturbacion_inductiva = 0
perturbacion_electromagnetica = 0
prev_error = 0

# Historial de datos
tiempo = []
entrada_data = []
error_data = []
u_P_data = []
u_D_data = []
u_PD_data = []
perturbacion_ind_data = []
perturbacion_em_data = []
retroalimentacion_data = []

# --- Simulador ---
def simulador():
    global V_out, perturbacion_inductiva, perturbacion_electromagnetica
    global Kp, Kd, simulacion_pausada, V_in, prev_error

    t = 0
    while True:
        if simulacion_pausada:
            time.sleep(0.1)
            continue

        d_ind = perturbacion_inductiva
        d_em = perturbacion_electromagnetica
        perturbacion_total = d_ind + d_em

        if d_ind != 0:
            perturbacion_inductiva = 0
        if d_em != 0:
            perturbacion_electromagnetica = 0

        f = V_out + perturbacion_total
        e = V_in - f
        de = (e - prev_error) / DT
        prev_error = e

        u_P = Kp * e
        u_D = Kd * de
        u_PD = u_P + u_D

        V_out += u_PD

        # Guardar datos
        tiempo.append(t)
        entrada_data.append(V_out)
        error_data.append(e)
        u_P_data.append(u_P)
        u_D_data.append(u_D)
        u_PD_data.append(u_PD)
        perturbacion_ind_data.append(d_ind)
        perturbacion_em_data.append(d_em)
        retroalimentacion_data.append(f)

        t += DT
        time.sleep(DT)

# --- UI Callbacks ---
def aplicar_perturbacion_inductiva():
    global perturbacion_inductiva
    perturbacion_inductiva = amplitud_inductiva

def aplicar_perturbacion_em():
    global perturbacion_electromagnetica
    perturbacion_electromagnetica = amplitud_em

def actualizar_kp(val):
    global Kp
    Kp = float(val)

def actualizar_kd(val):
    global Kd
    Kd = float(val)

def actualizar_amplitud_ind(val):
    global amplitud_inductiva
    amplitud_inductiva = float(val)

def actualizar_amplitud_em(val):
    global amplitud_em
    amplitud_em = float(val)

def actualizar_entrada(val):
    global V_in
    V_in = float(val)

def pausar_reanudar():
    global simulacion_pausada
    simulacion_pausada = not simulacion_pausada
    boton_pausa.config(text="Reanudar" if simulacion_pausada else "Pausar")

# --- Animación ---
def animar(i):
    ventana_tiempo = 20
    puntos_ventana = int(ventana_tiempo / DT)

    if len(tiempo) < puntos_ventana:
        t = tiempo
        idx_ini = 0
        x_min = 0
        x_max = ventana_tiempo
    else:
        t = tiempo[-puntos_ventana:]
        idx_ini = -puntos_ventana
        x_min = tiempo[-puntos_ventana]
        x_max = tiempo[-1]

    # u_PD
    axes[0].clear()
    axes[0].plot(t, u_PD_data[idx_ini:], label="Control PD", color="purple")
    axes[0].set_ylim(-60, 60)
    axes[0].set_xlim(x_min, x_max)
    axes[0].legend()
    axes[0].grid(True)

    # u_P
    axes[1].clear()
    axes[1].plot(t, u_P_data[idx_ini:], label="Control Proporcional", color="blue")
    axes[1].set_ylim(-40, 40)
    axes[1].set_xlim(x_min, x_max)
    axes[1].legend()
    axes[1].grid(True)

    # u_D
    axes[2].clear()
    axes[2].plot(t, u_D_data[idx_ini:], label="Control Derivativo", color="orange")
    axes[2].set_ylim(-40, 40)
    axes[2].set_xlim(x_min, x_max)
    axes[2].legend()
    axes[2].grid(True)

    # Salida del sistema
    axes[3].clear()
    axes[3].plot(t, entrada_data[idx_ini:], label="V_out", color="green")
    axes[3].set_ylim(190, 250)
    axes[3].set_xlim(x_min, x_max)
    axes[3].legend()
    axes[3].grid(True)

    # Error
    axes[4].clear()
    axes[4].plot(t, error_data[idx_ini:], label="Error e(t)", color="red")
    axes[4].fill_between(t, -0.08*V_REF, 0.08*V_REF, color='gray', alpha=0.3, label="±8%")
    axes[4].set_ylim(-20, 20)
    axes[4].set_xlim(x_min, x_max)
    axes[4].legend()
    axes[4].grid(True)

    # Perturbaciones
    axes[5].clear()
    axes[5].plot(t, perturbacion_ind_data[idx_ini:], label="Inductiva", color="purple")
    axes[5].plot(t, perturbacion_em_data[idx_ini:], label="Electromagnética", color="brown")
    axes[5].set_ylim(-40, 40)
    axes[5].set_xlim(x_min, x_max)
    axes[5].legend()
    axes[5].grid(True)

    # Retroalimentación
    axes[6].clear()
    axes[6].plot(t, retroalimentacion_data[idx_ini:], label="f(t) = V_out + perturbaciones", color="orange")
    axes[6].axhline(V_REF, color='black', linestyle='--', label='Referencia')
    axes[6].set_ylim(190, 250)
    axes[6].set_xlim(x_min, x_max)
    axes[6].legend()
    axes[6].grid(True)

# ==============================
# Ventana 1: Controles
# ==============================

ventana_controles = tk.Tk()
ventana_controles.title("Controles del Sistema")

frame_izq = ttk.Frame(ventana_controles)
frame_izq.pack(side=tk.LEFT, padx=10, pady=10)

frame_der = ttk.Frame(ventana_controles)
frame_der.pack(side=tk.RIGHT, padx=10, pady=10)

# Izquierda
ttk.Label(frame_izq, text="Ganancia Kp:").pack()
kp_slider = tk.Scale(frame_izq, from_=0.0, to=2.0, resolution=0.05,
                     orient=tk.HORIZONTAL, length=150, command=actualizar_kp)
kp_slider.set(Kp)
kp_slider.pack()

ttk.Label(frame_izq, text="Ganancia Kd:").pack()
kd_slider = tk.Scale(frame_izq, from_=0.0025, to=0.0045, resolution=0.1,
                     orient=tk.HORIZONTAL, length=150, command=actualizar_kd)
kd_slider.set(Kd)
kd_slider.pack()

ttk.Label(frame_izq, text="Amplitud Inductiva (+V):").pack()
slider_ind = tk.Scale(frame_izq, from_=0, to=30, resolution=1,
                      orient=tk.HORIZONTAL, length=150, command=actualizar_amplitud_ind)
slider_ind.set(amplitud_inductiva)
slider_ind.pack()

ttk.Button(frame_izq, text="Perturbación Inductiva", command=aplicar_perturbacion_inductiva).pack(pady=5)

# Derecha
ttk.Label(frame_der, text="Amplitud EM (-V):").pack()
slider_em = tk.Scale(frame_der, from_=-30, to=0, resolution=1,
                     orient=tk.HORIZONTAL, length=150, command=actualizar_amplitud_em)
slider_em.set(amplitud_em)
slider_em.pack()

ttk.Label(frame_der, text="Entrada V_in (215-225 V):").pack()
slider_vin = tk.Scale(frame_der, from_=215, to=225, resolution=0.5,
                      orient=tk.HORIZONTAL, length=150, command=actualizar_entrada)
slider_vin.set(V_REF)
slider_vin.pack()

ttk.Button(frame_der, text="Perturbación EM", command=aplicar_perturbacion_em).pack(pady=5)

boton_pausa = ttk.Button(ventana_controles, text="Pausar", command=pausar_reanudar)
boton_pausa.pack(pady=5)

# ==============================
# Ventana 2: Gráficos
# ==============================

ventana_graficos = tk.Toplevel()
ventana_graficos.title("Gráficos del Sistema")

frame_graficos = ttk.Frame(ventana_graficos)
frame_graficos.pack()

fig, axes = plt.subplots(7, 1, figsize=(10, 16))
fig.tight_layout(pad=3.0)

canvas = FigureCanvasTkAgg(fig, master=frame_graficos)
canvas.get_tk_widget().pack()

ani = animation.FuncAnimation(fig, animar, interval=100)

# --- Iniciar simulación en hilo separado ---
hilo = threading.Thread(target=simulador, daemon=True)
hilo.start()

# Ejecutar ambas ventanas
ventana_controles.mainloop()
