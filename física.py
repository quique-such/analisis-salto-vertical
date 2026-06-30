import numpy as np
import os
import pandas  # para cargar los ficheros excel 
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter as sf
from scipy.integrate import cumtrapz


# COLORES
# '#F2CC8F' amarillo
# '#81B29A'  verde azulado
# '#E07A5F' naranja
# '#3D405B' azul oscuro
# '#F4F1DE' crema
# '#EAB69F' rosa claro


fichero = 'quique.xlsx'
data = pandas.read_excel (fichero)
masa = 60
carpeta = os.path.dirname(os.path.abspath(__file__))

# guardar imágenes
def guardar_imagen(nombre, carpeta, nombre_archivo):
    plt.savefig(f'{carpeta}/{nombre}_{nombre_archivo}.png')
    
# función datos
def datos (data): # recoge los datos
    tiempo = np.array (data['t']) # eje de tiempo
    a = np.array (data['a'])
    ax = np.array (data['ax'])
    ay = np.array (data['ay'])
    az = np.array (data['az'])
    return (a, ax, ay, az, tiempo)

a, ax, ay, az, tiempo = datos(data)

# función filtro
def filtro (a, ay, tiempo):
    a_corregida = a * np.sign(ay) # cogemos el signo de ay
    
    t_recortado = tiempo[(tiempo >= 0.5) & (tiempo <= 3)] - 0.5
    # filtra los elementos de t que están entre 0.5 y 3, se resta -0.5 para que las gráficas comiencen en 0
    a_recortada = a_corregida[(tiempo >= 0.5) & (tiempo <= 3)]
    a_filtrada = sf (a_recortada, window_length= 5, polyorder=3)
    return (a_corregida, t_recortado, a_recortada, a_filtrada)

a_corregida, t_recortado, a_recortada, a_filtrada = filtro(a, ay, tiempo)


# máximos y mínimos:
def puntos (a_filtrada, t_recortado):
    # derivamos la aceleración 2 veces
    sacudida = np.gradient (a_filtrada)
    snap = np.gradient (sacudida)
    a_maxima = np.argmax (a_filtrada)
    impulso = np.argmax (snap)
    impacto = np.argmin (snap)# valor mínimo de la aceleración máxima
    return (impulso, a_maxima, impacto)

impulso, a_maxima, impacto = puntos (a_filtrada, t_recortado)

# gravedad
def gravedad_acelerometro (t_recortado, a_filtrada):
    t_reposo = t_recortado[0]  # tiempo de reposo inicial
    a_reposo = np.mean(a_filtrada[t_recortado <= t_reposo])  # aceleración media en la fase de reposo
    gravedad = np.abs(a_reposo)  # valor de la gravedad medida por el acelerómetro
    return (gravedad)

gravedad = gravedad_acelerometro (t_recortado, a_filtrada)

# fuerza acelerómetro
def fuerza_salto (a_filtrada, gravedad, masa):
    a_saltador = a_filtrada - gravedad
    fuerza = masa * (a_saltador + 9.81)
    return (a_saltador, fuerza)

a_saltador, fuerza = fuerza_salto (a_filtrada, gravedad, masa)

# integrales
def primitivaNumerica (variable, tiempo, y0):
    return cumtrapz(variable,x=tiempo,initial=y0)

# velocidad salto
def velocidad_salto (a_saltador, t_recortado):
    # integrar a_saltador
    velocidad = primitivaNumerica(a_saltador, t_recortado, 0)
    min_velocidad = np.argmin (velocidad)
    max_velocidad = np.argmax (velocidad)
    print (velocidad[max_velocidad])
    return (velocidad, min_velocidad, max_velocidad)

velocidad, min_velocidad, max_velocidad = velocidad_salto (a_saltador, t_recortado)
    
# máximo de fuerza en el salto
def max_fuerza (max_velocidad):
    max_fuerza = np.argmax(fuerza[:max_velocidad])
    return (max_fuerza)

max_fuerza = max_fuerza (max_velocidad)

# potencia de salto
def potencia_salto (fuerza, velocidad, masa):
    potencia = fuerza  * velocidad
    pot_max = np.argmax (potencia)
    pot_normalizada = pot_max / masa
    return (potencia, pot_max, pot_normalizada)

potencia, pot_max, pot_normalizada = potencia_salto (fuerza, velocidad, masa)


# altura salto
def altura_salto (max_velocidad, velocidad):
    h = (velocidad[max_velocidad] ** 2) / (2 * 9.81)
    return (h)
h = altura_salto (max_velocidad, velocidad)
print (h)

# GRÁFICAS
# --------------------------------------------------------------------------------
# aceleración: #EAB69F
# velocidad: #81B29A
# fuerza: #E07A5F
# potencia: #F4F1DE

# cambiamos la fuente
font = {'family': 'Calibri', 'size': 12}
plt.rc('font', **font)

# gráfica aceleración (figura 1)
plt.figure('ACELERACIÓN RESPECTO AL TIEMPO', facecolor='#EAB69F')
plt.plot(tiempo, ax, label='aceleración x', color = '#F2CC8F') # naranja
plt.plot(tiempo, ay, label='aceleración y', color = '#81B29A') # verde azulado
plt.plot(tiempo, az, label='aceleración z', color = '#E07A5F') # naranja
plt.plot(tiempo, a, label='aceleración', color = '#3D405B') #azul oscuro
plt.grid('True')
plt.xlabel ('$t$(s)')
plt.ylabel ('$a$(m/s$^2$)')
plt.title ('DATOS ACELERÓMETRO',fontsize = 14, fontweight = 'bold')
plt.legend (['$a_x$','$a_y$','$a_z$','$a$',])
guardar_imagen('aceleración', carpeta, fichero)

# gráfica de a corregida (figura 2)
plt.figure ('ACELERACIÓN CORREGIDA RESPECTO AL TIEMPO', facecolor='#EAB69F')
plt.plot(tiempo, a_corregida, label='aceleración corregida', color = '#E07A5F')
plt.plot(tiempo, a, '--', label='módulo de la aceleración', color = '#3D405B')
plt.grid('True')
plt.xlabel ('$t$(s)')
plt.ylabel ('$a$(m/s$^2$)')
plt.title ('MÓDULO DE LA ACELERACIÓN MEDIDA',fontsize = 14, fontweight = 'bold')
plt.legend(['$||a||$ Corregido','$||a||$ Original'])
guardar_imagen('aceleración corregida', carpeta, fichero)

# gráfica señal suavizada (figura 3)
plt.figure('SEÑAL SUAVIZADA', facecolor='#EAB69F')
plt.plot(t_recortado, a_recortada, label='aceleración', color='#81B29A')
plt.plot(t_recortado, a_filtrada, '.', markersize=3, label = 'aceleración suavizada', color='#3D405B')
plt.grid(True)
plt.xlabel('$t$(s)')
plt.ylabel('$a$(m/s$^2$)')
plt.title('SEÑAL SUAVIZADA',fontsize = 14, fontweight = 'bold')
plt.legend(['original', 'suavizada'])
guardar_imagen('señal suavizada', carpeta, fichero)

# gráfica puntos de interés (figura 4)
plt.figure ('PUNTOS DE INTERÉS', facecolor = '#EAB69F')
plt.plot(t_recortado, a_filtrada, markersize=3, label = 'aceleración filtrada', color='#3D405B')
plt.scatter(t_recortado[impulso], a_filtrada[impulso], color='#EAB69F', label='impulso')
plt.scatter(t_recortado[a_maxima], a_filtrada[a_maxima], color='#E07A5F', label='aceleración máxima')
plt.scatter(t_recortado[impacto], a_filtrada[impacto], color='#F2CC8F', label='impacto suelo')
plt.grid(True)
plt.xlabel('$t$(s)')
plt.ylabel('$a$(m/s$^2$)')
plt.title('PUNTOS DE INTERÉS',fontsize = 14, fontweight = 'bold')
plt.legend()
guardar_imagen('puntos interés', carpeta, fichero)


# gráfica fuerza ejercida por las piernas (figura 5)
plt.figure('FUERZA', facecolor='#E07A5F')
plt.plot(t_recortado, fuerza, color='#81B29A', label='fuerza piernas')
plt.scatter(t_recortado[max_fuerza], fuerza[max_fuerza], color='#3D405B', label='fuerza máxima del salto') # representa un punto en la gráfica
plt.grid(True)
plt.xlabel('$t$(s)')
plt.ylabel('$F(t)$ [N])')
plt.title('FUERZA EJERCIDA POR LAS PIERNAS',fontsize = 14, fontweight = 'bold')
plt.legend(['fuerza ejercida por las piernas','máxima fuerza del salto'])
guardar_imagen('fuerza', carpeta, fichero)

# gráfica velocidad (figura 6)
plt.figure('VELOCIDAD RESPECTO AL TIEMPO', facecolor='#81B29A')
plt.plot(t_recortado, velocidad, label='velocidad', color='#3D405B')
plt.axvspan(t_recortado[max_velocidad], t_recortado[min_velocidad], alpha=0.3, color='#F2CC8F') # pintamos el intervalo de tia
plt.text((t_recortado[max_velocidad] + t_recortado[min_velocidad]) / 2 + 0.2, np.max(velocidad) , 'Tiempo en el aire', ha='center', va='bottom', backgroundcolor='#F2CC8F')
plt.grid(True)
plt.xlabel('$t$ (s)')
plt.ylabel('$v$(m/s)')
plt.title('VELOCIDAD SALTO',fontsize = 14, fontweight = 'bold')
plt.legend(['velocidad'])
guardar_imagen('velocidad', carpeta, fichero)


# gráfica potencia

plt.figure('POTENCIA DE SALTO', facecolor='#F4F1DE')
plt.plot(t_recortado, potencia, label='potencia', color='#E07A5F')
plt.grid(True)
plt.xlabel('$t$ (s)')
plt.ylabel('$P$(t)[W]')
plt.title('POTENCIA SALTO',fontsize = 14, fontweight = 'bold')
plt.legend(['potencia'])
plt.xlim (0,1)
guardar_imagen('potencia', carpeta, fichero)

plt.show()