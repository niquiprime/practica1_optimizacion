import argparse
import re
from prettytable import PrettyTable
import sys
casicero = (sys.float_info.epsilon)

def comparar_epsilon(valor):
    epsilon_maquina = sys.float_info.epsilon
    if abs(valor) <= epsilon_maquina:
        return 0
    else:
        return valor

def add_slack_variables(constraints):
    new_constraints = []
    slack_count = 1
    excess_count = 1
    artificial_count = 1

    #si la restriccion es <= agregar variable de holgura
    for constraint in constraints:
        if constraint["sign"] == "<=":
            slack_var = f"h{slack_count}"
            constraint["coefficients"][slack_var] = 1.0
            slack_count += 1
            new_constraints.append(constraint)

        #si la restriccion es >= agregar variable de exceso y artificial
        if constraint["sign"] == ">=":
            excess_var = f"e{excess_count}"
            constraint["coefficients"][excess_var] = -1.0
            excess_count += 1
            artificial_var = f"a{artificial_count}"
            constraint["coefficients"][artificial_var] = 1.0
            artificial_count += 1
            new_constraints.append(constraint)

    return new_constraints, slack_count - 1
    

def negate_objective(objective_coefs, num_slack_vars):
    negated_coefs = {}
    for var, coef in objective_coefs.items():
        negated_coefs[var] = -coef
    for i in range(1, num_slack_vars + 1):
        negated_coefs[f"h{i}"] = 0.0
    return negated_coefs

def format_equation(coefs):
    equation = ""
    for var, coef in coefs.items():
        equation += f"{'+' if coef >= 0 else ''}{coef}{var} "
    return equation + "= 0"

def generate_initial_table(objective_coefs, num_slack_vars):
    table = PrettyTable()
    
     # Crear el encabezado de la tabla
    header_row = ["VB", "Z"]
    header_row.extend(objective_coefs.keys())

    # Agregar las variables de holgura al encabezado
    for i in range(1, num_slack_vars + 1):
        header_row.append(f"H{i}")
    header_row.append("LD")
    table.field_names = header_row

   # Agregar los coeficientes de la función objetivo a la tabla
    objective_row = ["Z", 1]
    objective_row.extend([-objective_coefs.get(var, 0) for var in header_row[2:-1]])
    objective_row.append(0)
    table.add_row(objective_row)
    
   # Agregar los coeficientes de las restricciones a la tabla
    for i, constraint in enumerate(constraints, start=1):
        row = [f"H{i}",0]
        row.extend([constraint["coefficients"].get(var, 0) if var != f"H{i}" else 1 for var in header_row[2:-1]])
        row.extend([constraint["rhs"]])
        table.add_row(row)

    # Añadir bordes
    table.border = True
    # Alinear las columnas
    table.align = "l"
    # Imprimir la tabla
    print(table)
    return table

def get_column_values(table, column_name):
    column_index = table.field_names.index(column_name)
    column_values = [row[column_index] for row in table._rows]
    #column_values = [comparar_epsilon(valor) for valor in column_values]
    
    return column_values

def get_row_values(table, row_index):
    row_values = table._rows[row_index]
    row_values = [row_values[0]] + [comparar_epsilon(valor) for valor in row_values[1:]]
    #print("wañoños",row_values)
    return row_values

def get_intersection_value(table, row_index, column_name):
    column_index = table.field_names.index(column_name)
    intersection_value = table._rows[row_index][column_index]
    return intersection_value


def Elegir_pivote_M2F(objective_coefs,tablita):

    max_value = max(objective_coefs.values())
    if list(objective_coefs.values()).count(max_value) > 1:
        print("El máximo valor se repite en el diccionario.")
        max_value = max(objective_coefs.values())
        last_max_element = None
        for key, value in objective_coefs.items():
            if value == max_value:
                last_max_element = key
        pivot = last_max_element
    else:
        #pivot = max(objective_coefs, key=objective_coefs.get)
        pivot = max(objective_coefs, key=lambda x: abs(objective_coefs[x]))
        
    #si ya existe una columna de ratios borrarla y cambiar el pivote por el mayor negativo en la tabla
    if 'Ratios' in tablita.field_names:
        tablita.del_column('Ratios')
    print ("Pivote: ",pivot)

    #elejir la variable de salida
    ld_values = get_column_values(tablita, 'LD')
    pivot_values = get_column_values(tablita, pivot)

    # Calcular los valores de la división
    ratios = [ld / pivot if pivot != 0 else float('inf') for ld, pivot in zip(ld_values, pivot_values)]
    ratios[0] = -1
    

    #agregar los ratios a una columna provicional
    tablita.add_column("Ratios", ratios, align="r")

    #el ratio con menor valor (dejando de lado todo valo <= 0) es el pivote
    pivot_row = min((i for i, ratio in enumerate(ratios) if ratio > 0), key=ratios.__getitem__)
    row = get_row_values(tablita, pivot_row)

    intersection_value = get_intersection_value(tablita, pivot_row, pivot)
    
    row = get_row_values(tablita, pivot_row)
    column = get_column_values(tablita, pivot)
    arreglo_modificado = [row[0]] + [comparar_epsilon(valor) for valor in row[1:]]
    print('Valor columna ',column)
    print('valor fila sus', arreglo_modificado)
    print(tablita)

    return column,row,intersection_value,pivot

def Elegir_pivote(objective_coefs,tablita):

    max_value = max(objective_coefs.values())
    if list(objective_coefs.values()).count(max_value) > 1:
        print("El máximo valor se repite en el diccionario.")
        max_value = max(objective_coefs.values())
        last_max_element = None
        for key, value in objective_coefs.items():
            if value == max_value:
                last_max_element = key
        pivot = last_max_element
    else:
        #pivot = max(objective_coefs, key=objective_coefs.get)
        pivot = max(objective_coefs, key=lambda x: abs(objective_coefs[x]))
        
    #si ya existe una columna de ratios borrarla y cambiar el pivote por el mayor negativo en la tabla
    if 'Ratios' in tablita.field_names:
        tablita.del_column('Ratios')
        valor_pivote = get_row_values(tablita, 0)
        for i in range(1,len(valor_pivote)):
            if valor_pivote[i] < 0:
                pivot = tablita.field_names[i]
    print ("Pivote: ",pivot)

    #elejir la variable de salida
    ld_values = get_column_values(tablita, 'LD')
    pivot_values = get_column_values(tablita, pivot)

    # Calcular los valores de la división
    ratios = [ld / pivot if pivot != 0 else float('inf') for ld, pivot in zip(ld_values, pivot_values)]
    ratios[0] = -1
    

    #agregar los ratios a una columna provicional
    tablita.add_column("Ratios", ratios, align="r")

    #el ratio con menor valor (dejando de lado todo valo <= 0) es el pivote
    pivot_row = min((i for i, ratio in enumerate(ratios) if ratio > 0), key=ratios.__getitem__)
    row = get_row_values(tablita, pivot_row)

    intersection_value = get_intersection_value(tablita, pivot_row, pivot)

    row = get_row_values(tablita, pivot_row)
    column = get_column_values(tablita, pivot)
    
    print('Valor columna ',column)
    print('valor fila ', row)
    print(tablita)

    return column,row,intersection_value,pivot


def actualizar_tabla(table,column,row,intersection_value,pivot):
    # Encontrar los índices de 'Z' y 'H3' pivot
    start_index = table.field_names.index('Z')
    end_index = table.field_names.index('Ratios')

    # Dividir los valores desde 'Z' hasta 'ratios' por el valor de intersección ademas de cambiar el primer valor por x o y respectivamente
    new_row = row[:start_index] + [value / intersection_value for value in row[start_index:end_index]] + row[end_index:]
    new_row[0] = pivot
    print('Nueva fila: ',new_row)
    
    #encontrar el numero de fila con el ratio mas bajo
    row = table._rows[1:].index(row) + 1    

    print('Fila pivote: ',row)
    print(table)

    #actualizar la fila pivote por la nueva fila
    table._rows[row] = new_row


   #restar cada fila por el valor de la interseccion multiplicado por la casilla actual
    for i in range(len(table._rows)):
        if i == row:  # Skip the pivot row
            continue

        row_actual = get_row_values(table, i)
        row_temp = []
        for j in range(len(row_actual)):
            if isinstance(row_actual[j], str):
                row_temp.append(row_actual[j])
            else:
                row_temp.append(row_actual[j] - new_row[j] * column[i])
        table._rows[i] = row_temp
    return table

def two_phase_simplex(constraints):
    #########FASE 1#########
    #separar las restricciones para solamente usar las de tipo >=
    phase1_constraints = [constraint for constraint in constraints if constraint["sign"] == ">="]
    # Crear una tabla para la fase 1
    table_temp = PrettyTable()
    # Crear el encabezado de la tabla que contenga la variable de exceso seguida de una artificial
    header_row = ["VB", "Z"]
    header_row.extend(objective_coefs.keys())
    for constraint in phase1_constraints:
        header_row.append(f"e{phase1_constraints.index(constraint) + 1}")
        header_row.append(f"a{phase1_constraints.index(constraint) + 1}")
    header_row.append("LD")
    table_temp.field_names = header_row
    #agregar en la primera fila un 1 en cada A y 0 en cada E
    row = ["Z", -1]
    for i in range(len(objective_coefs)):
        row.append(0)
    for constraint in phase1_constraints:
        row.extend([0, 1])
    row.append(0)
    table_temp.add_row(row)
    
    # Agregar las restricciones a la tabla
    for i, constraint in enumerate(phase1_constraints, start=1):
        row = [f"A{i}", 0]
        for header in header_row[2:-1]:  # Ignorar 'VB', 'Z' y 'LD'
            row.append(constraint["coefficients"].get(header, 0))
        row.append(constraint["rhs"])
        table_temp.add_row(row)
    print (table_temp)

    #multiplicar cada una de las filas por -1 y sumarlas a la fila Z
    row_temp = []
    z_row_temp = get_row_values(table_temp, 0)
    tabla_temp = table_temp

    for i in range(1,len(tabla_temp._rows)):
        row_temp = get_row_values(tabla_temp, i)
        print('Fila actual: ',row_temp)
        for j in range(1,len(row_temp)):
            row_temp[j] = row_temp[j] * -1
            z_row_temp[j] = z_row_temp[j] + row_temp[j]
        for j in range(1,len(row_temp)):
            row_temp[j] = row_temp[j] * -1
    
    #actualizar solamente la fila 1
    table_temp._rows[0] = z_row_temp
    print (table_temp)

    #coseguir los coeficientes de la funcion objetivo temporal de la tabla nueva
    objective_row = get_row_values(table_temp, 0)
    # Crear una lista de valores a ignorar
    ignore_values = ['VB', 'Z', 'LD'] + [f"e{i+1}" for i in range(len(phase1_constraints))] + [f"a{i+1}" for i in range(len(phase1_constraints))]

    # Crear un diccionario que mapea los valores del encabezado a los valores de la función objetivo
    objective_dict = {header_row[i]: value for i, value in enumerate(objective_row) if header_row[i] not in ignore_values}

    #elegir el pivote
    column, row, intersection_value,pivot = Elegir_pivote_M2F(objective_dict,table_temp)
    #actualizar la tabla
    table_temp = actualizar_tabla(table_temp,column,row,intersection_value,pivot)
    print(table_temp)
    

    #continuar iterando hasta que no haya valores negativos en la funcion objetivo
    while True:
        objective_dict = {header_row[i]: value for i, value in enumerate(objective_row) if i < len(header_row) and header_row[i] not in ignore_values}
        obj_func = get_row_values(table_temp, 0)
        print (obj_func)
        obj_func_dict = {header_row[i]: value for i, value in enumerate(obj_func) if i < len(header_row) and header_row[i] not in ignore_values}
        for i in range(1,len(obj_func)+1):
            if obj_func[i] < 0:
                column, row, intersection_value,pivot = Elegir_pivote_M2F(obj_func_dict,table_temp)
                table_temp = actualizar_tabla(table_temp,column,row,intersection_value,pivot)
                #borrar la columna de ratios
                #z_row = get_row_values(table_temp,0)
                table_temp.del_column('Ratios')
                #tabla_temp._rows[0] = z_row
                #print("Prueba",z_row)
                print(table_temp)
                i = 0
                break
            
        else:
            
            print("\nSolución óptima encontrada.")
            print (table_temp)
            break
        break
    while True:
         #verificar si aun hay negativos en la funcion objetivo
        obj_func = get_row_values(table_temp, 0)
        print (obj_func)
        except_values = ['VB', 'Z', 'LD']
        obj_func_dict = {header_row[i]: value for i, value in enumerate(obj_func) if i < len(header_row) and header_row[i] not in except_values}
        #guardar solamente los negativos
        negative_values_dict = {key: value for key, value in obj_func_dict.items() if value < 0}
        for i in range(1,len(obj_func)):
            if obj_func[i] < 0:
                column, row, intersection_value,pivot = Elegir_pivote(negative_values_dict,table_temp)
                print ('columna: ',column)
                print ('fila: ',row)
                print ('interseccion: ',intersection_value)
                print ('pivote: ',pivot)
                table_temp = actualizar_tabla(table_temp,column,row,intersection_value,pivot)

                break
        #actualizar la tabla
        z_row = get_row_values(table_temp,0)
        print("Prueba en 352",z_row)
        tabla_temp._rows[0] =  z_row #sexo
        print(tabla_temp)
        break
    
def solve_simplex(maximaze, objective_coefs, num_slack_vars):
    if maximize == True:
        print("Resolviendo problema de maximización...")
        # Igualar la función objetivo a 0
        negated_objective = negate_objective(objective_coefs, num_slack_vars)
        equation = format_equation(negated_objective)
        print("Función objetivo igualada a 0:", equation)
        #comprobar si existen restricciones de tipo >=
        
        # Generar tabla inicial
        print("\nTabla inicial:")
        table = generate_initial_table(objective_coefs, num_slack_vars)
        column, row, intersection_value,pivot = Elegir_pivote(objective_coefs,table)

        for constraint in constraints:
            if constraint["sign"] == ">=":
                two_phase_simplex(constraints)
                break

        # Actualizar la tabla
        table = actualizar_tabla(table,column,row,intersection_value,pivot)
        print("\nTabla actualizada:")
        print(table)

        # Repetir el proceso hasta que no haya valores negativos en los primeros 3 valores de la primera fila'
        while True:
            prueba1 = get_row_values(table, 0)
            for i in range(1,len(objective_coefs)+2):
                if prueba1[i] < 0:
                    column, row, intersection_value,pivot = Elegir_pivote(objective_coefs,table)
                    table = actualizar_tabla(table,column,row,intersection_value,pivot)
                    print("\nTabla actualizada:")
                    #borrar la columna de ratios
                    table.del_column('Ratios')
                    print(table)
                    i = 0
                    break
            else:
                print("\nSolución óptima encontrada.")
                print (table)
            break
    if maximize == False:
        print("Resolviendo problema de minimización...")
    
    

    #calcular precio sombra

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simplex Solver")
    parser.add_argument("--objetivo", type=str, help="funcion objetivo")
    parser.add_argument("--res", nargs='+', help="restricciones")
    parser.add_argument("--maximize", action="store_true", help="Maximize the objective function")
    parser.add_argument("--minimize", action="store_true", help="Minimize the objective function")
    args = parser.parse_args()

    # Verificar si se debe maximizar o minimizar
    if args.maximize and args.minimize:
        raise ValueError("No se puede especificar maximizar y minimizar al mismo tiempo.")
    elif args.maximize:
        maximize = True
    elif args.minimize:
        maximize = False
    else:
        raise ValueError("Debe especificar si se debe maximizar o minimizar el problema.")

    # Obtener los coeficientes y términos de la función objetivo
    objective_coefs = {}
    pattern = r'([+\-]?[\d.]*)([a-zA-Z]+)'
    for coef, var in re.findall(pattern, args.objetivo):
        coef = coef.strip()
        if coef:
            objective_coefs[var] = float(coef) if coef != "-" else -1.0
        else:
            objective_coefs[var] = 1.0

    # Obtener las restricciones
    constraints = []
    for constraint_text in args.res:
        # Determinar el tipo de restricción
        constraint_sign = re.findall(r'[<>]=?', constraint_text)[0]
        if constraint_sign == '<=':
            inequality = '≤'
        elif constraint_sign == '>=':
            inequality = '≥'
        else:
            inequality = '='

        # Separar coeficientes y término independiente del lado izquierdo de la restricción
        constraint, rhs = constraint_text.split(constraint_sign)
        constraint = constraint.strip()
        rhs = float(rhs.strip())

        # Extraer coeficientes y variables de la restricción
        constraint_coefs = {}
        for coef, var in re.findall(pattern, constraint):
            coef = coef.strip()
            if coef:
                coef_value = float(coef) if coef != "-" else -1.0 if var[0] != '-' else 1.0
                constraint_coefs[var] = coef_value
            else:
                constraint_coefs[var] = 1.0

        # Almacenar restricción como un diccionario
        constraint_dict = {
            "coefficients": constraint_coefs,
            "rhs": rhs,
            "sign": constraint_sign
        }
        constraints.append(constraint_dict)

    # Agregar variables de holgura si las restricciones son de tipo <=
    if maximize == True:
        constraints, num_slack_vars = add_slack_variables(constraints)
        solve_simplex(maximize,objective_coefs, num_slack_vars)
    else:
        constraints, num_slack_vars = add_slack_variables(constraints)
        solve_simplex(maximize,objective_coefs, num_slack_vars)

    # Llamar a la función del solucionador simplex
    
