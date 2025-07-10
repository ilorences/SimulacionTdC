import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

# --- Inicialización ---
DT = 0.1
Kp = 1.5
Kd = 0.355

V_in = 230  # valor inicial para que arranque controlando
V_out = 230  # corregido: que arranque en 230 para que se vea la corrección
prev_error = 0

amplitud_inductiva = 10
amplitud_em = -10
perturbacion_inductiva = 0
perturbacion_electromagnetica = 0

simulacion_pausada = False
fusible_quemado = False
microp_con_falla = False

# --- Datos ---
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
    global fusible_quemado, microp_con_falla

    t = 0
    while True:
        if simulacion_pausada:
            time.sleep(0.1)
            continue

        d_ind = perturbacion_inductiva
        d_em = perturbacion_electromagnetica
        perturbacion_total = d_ind + d_em

        perturbacion_inductiva = 0
        perturbacion_electromagnetica = 0

        f = V_out
        e = V_in - f

        de = (e - prev_error) / DT
        prev_error = e

        u_P = Kp * e
        u_D = Kd * de
        u_PD = u_P + u_D

        V_out += (u_PD + perturbacion_total) * DT
        V_out = max(min(V_out, 250), 190)

        umbral_error = 0.08 * V_in
        if abs(e) > umbral_error:
            if f > V_in + umbral_error:
                fusible_quemado = True
                V_out = 0
            elif f < V_in - umbral_error:
                microp_con_falla = True
                V_out = 0

        if fusible_quemado or microp_con_falla:
            guardar_datos(t, e, 0, 0, 0, d_ind, d_em, 0)
            t += DT
            time.sleep(DT)
            continue

        guardar_datos(t, e, u_P, u_D, u_PD, d_ind, d_em, f)
        t += DT
        time.sleep(DT)

def guardar_datos(t, e, u_P, u_D, u_PD, d_ind, d_em, f):
    tiempo.append(t)
    entrada_data.append(V_out)
    error_data.append(e)
    u_P_data.append(u_P)
    u_D_data.append(u_D)
    u_PD_data.append(u_PD)
    perturbacion_ind_data.append(d_ind)
    perturbacion_em_data.append(d_em)
    retroalimentacion_data.append(f)

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

def reiniciar_sistema():
    global fusible_quemado, microp_con_falla, V_out, prev_error
    fusible_quemado = False
    microp_con_falla = False
    V_out = V_in  # mantener coherencia en reinicio
    prev_error = 0

# --- Animación ---
def animar(i):
    ventana_tiempo = 20
    puntos_ventana = int(ventana_tiempo / DT)

    if len(tiempo) < puntos_ventana:
        t = tiempo
        idx_ini = 0
    else:
        t = tiempo[-puntos_ventana:]
        idx_ini = -puntos_ventana

    # Nuevo orden: izquierda: PD, P, D, Perturbaciones / derecha: Error, Salida, Retroalimentación, (vacío)
    datos = [
        (u_PD_data, "Control PD", "purple", -70, 70),
        (error_data, "Error e(t)", "red", -20, 20),
        (u_P_data, "Control Proporcional", "blue", -25, 25),
        (entrada_data, "Salida del sistema", "green", 190, 250),
        (u_D_data, "Control Derivativo", "orange", -40, 40), 
        (retroalimentacion_data, "Retroalimentación", "orange", 200, 240),
        (None, "Perturbaciones", None, -200, 200), 
        (None, "", None, 0, 1),  # espacio en blanco
    ]

    for i, (data, label, color, ymin, ymax) in enumerate(datos):
        row, col = divmod(i, 2)
        ax = axes[row][col]
        ax.clear()
        if data:
            ax.plot(t, data[idx_ini:], label=label, color=color)
        elif label == "Perturbaciones":
            ax.plot(t, perturbacion_ind_data[idx_ini:], label="Inductiva", color="purple")
            ax.plot(t, perturbacion_em_data[idx_ini:], label="Electromagnética", color="brown")
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(t[0], t[-1] if t else 20)
        ax.legend()
        ax.grid(True)

        if label == "Salida del sistema":
            ax.axhline(V_in, color='black', linestyle='--', label='Referencia')
            lim_inf = V_in - 0.08 * V_in
            lim_sup = V_in + 0.08 * V_in
            ax.fill_between(t, lim_inf, lim_sup, color='gray', alpha=0.3, label="Banda ±8%")


# --- Interfaz ---
ventana = tk.Tk()
ventana.title("Simulador con Gráficos en 2 Columnas")
ventana.configure(bg="#f2f2f2")  # fondo claro

frame_graficos = ttk.Frame(ventana)
frame_graficos.pack(side=tk.RIGHT)

frame_controles = ttk.Frame(ventana, padding=10)
frame_controles.pack(side=tk.LEFT, fill='y', padx=10, pady=10)

# --- Sliders ---
seccion_sliders = ttk.LabelFrame(frame_controles, text="Parámetros de Control", padding=10)
seccion_sliders.pack(fill='x', pady=5)

def crear_slider_con_valor(frame, texto, from_, to, initial, command, resolution=0.01):
    contenedor = ttk.Frame(frame)
    contenedor.pack(fill='x', pady=3)

    ttk.Label(contenedor, text=texto).pack(anchor='w')

    val_label = ttk.Label(contenedor, text=f"{initial:.2f}")
    val_label.pack(anchor='e')

    def actualizar_valor(val):
        val_label.config(text=f"{float(val):.2f}")
        command(val)

    slider = ttk.Scale(contenedor, from_=from_, to=to, orient="horizontal",
                       command=actualizar_valor)
    slider.set(initial)
    slider.pack(fill='x')
    return slider

kp_slider = crear_slider_con_valor(seccion_sliders, "Kp:", 0.0, 2.0, Kp, actualizar_kp, resolution=0.05)
kd_slider = crear_slider_con_valor(seccion_sliders, "Kd:", 0.0, 1.0, Kd, actualizar_kd, resolution=0.005)
slider_vin = crear_slider_con_valor(seccion_sliders, "V_in:", 210, 240, V_in, actualizar_entrada, resolution=10)

seccion_perturbaciones = ttk.LabelFrame(frame_controles, text="Perturbaciones", padding=10)
seccion_perturbaciones.pack(fill='x', pady=5)

slider_ind = crear_slider_con_valor(seccion_perturbaciones, "Amplitud Inductiva:", 50, 200, amplitud_inductiva, actualizar_amplitud_ind)
slider_em = crear_slider_con_valor(seccion_perturbaciones, "Amplitud EM:", -200, -50, amplitud_em, actualizar_amplitud_em)


# --- Botones ---
seccion_botones = ttk.LabelFrame(frame_controles, text="Acciones", padding=10)
seccion_botones.pack(fill='x', pady=5)

ttk.Button(seccion_botones, text="Aplicar Inductiva", command=aplicar_perturbacion_inductiva).pack(fill='x', pady=2)
ttk.Button(seccion_botones, text="Aplicar EM", command=aplicar_perturbacion_em).pack(fill='x', pady=2)

boton_pausa = ttk.Button(seccion_botones, text="Pausar", command=pausar_reanudar)
boton_pausa.pack(fill='x', pady=2)

ttk.Button(seccion_botones, text="Reiniciar", command=reiniciar_sistema).pack(fill='x', pady=2)


# --- Gráficos ---
fig, axes = plt.subplots(4, 2, figsize=(14, 10))
fig.tight_layout(pad=3.0)
canvas = FigureCanvasTkAgg(fig, master=frame_graficos)
canvas.get_tk_widget().pack()

ani = animation.FuncAnimation(fig, animar, interval=300)

# Simulación en segundo plano
threading.Thread(target=simulador, daemon=True).start()

ventana.mainloop()
