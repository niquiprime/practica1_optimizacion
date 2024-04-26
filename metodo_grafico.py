import numpy as np
import matplotlib.pyplot as plt
import re
import argparse


# Lee los parámetros
parser = argparse.ArgumentParser()
# Función objetivo
parser.add_argument("--objetivo", type=str, help="Función objetivo")
# Restricciones
parser.add_argument("--res", type=str, nargs="+", help="Restricciones")
# Maximizar
parser.add_argument("--max", action="store_true", help="Maximizar")
# Minimizar
parser.add_argument("--min", action="store_true", help="Minimizar")
args = parser.parse_args()

REG_EXP = r"[-+]?\d*\.\d+|[-+]?\d+"

# Configuración de la gráfica
fig, ax = plt.subplots()
ax.grid(True, which='both', axis='both')
ax.axhline(y=0, color='k')
ax.axvline(x=0, color='k')
x = np.linspace(0, 10, 1000)



# Restricciones
res = args.res

#Guardar coeficientes de las restricciones
A = [] # Matriz de restricciones
B = [] # Matriz de valores de restricciones

# Todos los signos de las restricciones que puede existir en el input de una restriccion
restriccionesSigno = ["<=", ">="]


def parse_restriccion_coeficientes(restriccion):    
    for signo in restriccionesSigno:
        if signo in restriccion:
            coef, const = restriccion.split(signo)
            coef = re.findall(REG_EXP, coef)
            coef = [float(x) for x in coef]
            a, b = coef
            c = float(const)
            return a, b, c

def parse_restriccion_signo(restriccion): #solo signo
    for signo in restriccionesSigno:
        if signo in restriccion:
            match = re.match(r"(.*)\s*({0})\s*(.*)".format(signo), restriccion)
            a, signo, c = match.groups()
            return signo


# Colores para las restricciones
colores = ['b', 'g', 'r', 'c', 'm', 'y', 'k']


# Graficar todas las restricciones
for i, restriccion in enumerate(res):
    a, b, c = parse_restriccion_coeficientes(restriccion)
    A.append([a, b])
    B.append(c)
    signo = parse_restriccion_signo(restriccion)
    if signo == "<=":
        if b != 0:
            max_y = c / b  
            y = np.linspace(0, max_y, 1000)
            if a != 0:
                x = (c - b * y) / a
                ax.plot(x, y, label=restriccion, color=colores[i])
            else:
                ax.axhline(y=c / b, label=restriccion, color=colores[i])
        else:
            ax.axvline(x=c / a, label=restriccion, color=colores[i])
    elif signo == ">=":
        if b != 0:
            min_y = c / b
            x = np.linspace(0, min_y, 1000)
            if a != 0:
                y = (c - b * x) / a
                ax.plot(x, y, label=restriccion, color=colores[i])
            else:
                ax.axhline(y=c / b, label=restriccion, color=colores[i])
        else:
            ax.axvline(x=c / a, label=restriccion, color=colores[i])
    
        
    


# Funcion objetivo
objetivo = args.objetivo
coef_obj = re.findall(REG_EXP, objetivo)
coef_obj = [float(x) for x in coef_obj]
a_obj, b_obj = coef_obj




# Calcular intersecciones
vertices = []
for i in range(len(A)):
    for j in range(i + 1, len(A)):
        a1, b1 = A[i]
        c1 = B[i]
        a2, b2 = A[j]
        c2 = B[j]
        if a1 * b2 - a2 * b1 != 0:
            x = (c1 * b2 - c2 * b1) / (a1 * b2 - a2 * b1)
            y = (a1 * c2 - a2 * c1) / (a1 * b2 - a2 * b1)
            vertices.append((x, y))
                    
# Calcular intersecciones con el eje x
for i in range(len(A)):
    a, b = A[i]
    c = B[i]
    if b != 0:
        x = c / a if a != 0 else float('inf')
        y = 0
    else:
        x = 0
        y = c / b if b != 0 else float('inf')
    if x >= 0 and y >= 0:
        vertices.append((x, y))

# Calcular intersecciones con el eje y
for i in range(len(A)):
    a, b = A[i]
    c = B[i]
    if b != 0:
        x = 0
        y = c / b
    else:
        x = c / a
        y = 0
    if x >= 0 and y >= 0:
        vertices.append((x, y))


#vertices.append((0, 0))
print("Puntos de intersección: ", vertices)

# grafiar puntos de interseccion eliminar puntos donde x o y sean negativos
vertices = [(x, y) for x, y in vertices if x >= 0 and y >= 0]
for x, y in vertices:
    ax.scatter(x, y, c="black")
    
vertices.append((0, 0))


# Verificar que vertices esten dentro de todas las restricciones y guardarlos en una lista teniendo en cueta si es <= o >=
vertices_validos = []
for x, y in vertices:
    valido = True
    for i in range(len(A)):
        a, b = A[i]
        c = B[i]
        signo = parse_restriccion_signo(res[i])
        if signo == "<=":
            if a * x + b * y > c:
                valido = False
                break
        elif signo == ">=":
            if a * x + b * y < c:
                valido = False
                break
    if valido:
        vertices_validos.append((x, y))

if len(vertices_validos) == 0:
    print("No hay puntos de intersección válidos")
    exit()

#### El escandalo de la semana
def calcular_angulo_polar(punto):
    x, y = punto
    dx, dy = x - centroide[0], y - centroide[1]
    return np.arctan2(dy, dx)
def dibujar_poligono(ax, vertices, color):
    x_vertices = [vertice[0] for vertice in vertices]
    y_vertices = [vertice[1] for vertice in vertices]
    ax.fill(x_vertices, y_vertices, facecolor=color)
# Calcular el centroide
centroide = np.mean(vertices_validos, axis=0)
# Ordenar los puntos en sentido antihorario
puntos_ordenados = sorted(vertices_validos, key=calcular_angulo_polar, reverse=True)
dibujar_poligono(ax, puntos_ordenados, 'lightblue')
#### primer plano

# Grafiar puntos de interseccion validos con puntos rojos
valorOptimo = float('-inf') if args.max else float('inf')
coordenadaOptima = []

for x, y in vertices_validos:
    x , y = round(x, 2), round(y, 2)
    ax.scatter(x, y, c= "cyan")
    z = round(a_obj * x + b_obj * y,2)
    ax.text(x, y, f"({x},{y}) \nValor: {z}")

    if args.max:
        if z > valorOptimo:
            valorOptimo = z
            coordenadaOptima = [x, y]
            
    elif args.min:
        if z < valorOptimo:
            valorOptimo = z
            coordenadaOptima = [x, y]

print("Puntos de intersección válidos: ", vertices_validos)

print("Coordenadas zona factible: ",coordenadaOptima)
ax.scatter(coordenadaOptima[0], coordenadaOptima[1], c=colores[2], label="Valor Óptimo")

y = np.linspace(0, valorOptimo / b_obj, 1000)
x = (valorOptimo - b_obj * y) / a_obj
ax.plot(x, y, label="Funcion objetivo", linestyle='--')

    
ax.legend(loc='upper right', fontsize='small', title='Restricciones', title_fontsize='medium') 
plt.show()