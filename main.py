import streamlit as st
import pandas as pd
import scipy.stats as stats

# Configuración para pantalla completa
st.set_page_config(layout="wide")

st.title("Prueba de Huecos")
st.divider()

# Función para realizar las operaciones
def multiplicador_constante(constante, semilla1, iteraciones):
    # Lista para almacenar los resultados
    resultados = []
    
    # Longitud de semilla
    longitud_semilla = len(str(semilla1))
    
    for i in range(iteraciones):
        # Calcula el producto de la semilla
        producto = semilla1 * constante
        longitud = len(str(producto))
        
        # Asegurándonos de que producto tenga 0 a la izquierda si es necesario
        if longitud <= 8:
            producto = f"{producto:08}"
        elif longitud <= 16:
            producto = f"{producto:016}"
        elif longitud <= 32:
            producto = f"{producto:032}"
        
        # Tomando los 4 dígitos de en medio según la longitud
        if longitud <= 8:
            medio = producto[2:6]
        elif longitud <= 16:
            medio = producto[6:10]
        elif longitud <= 32:
            medio = producto[14:18]
        
        # Convirtiendo a int()
        medio = int(medio)
        
        # Obteniendo ri
        ri = medio / 10**longitud_semilla
        
        # Guardamos los resultados en una lista
        resultados.append({
            'Semilla 1': semilla1,
            'Constante': constante,
            'Producto': producto,
            'Longitud': longitud,
            'Medio': medio,
            'ri': ri
        })
                
        # La nueva semilla será el valor de 'medio' calculado en esta iteración
        semilla1 = medio
        
    return resultados

# Lógica para navegar entre páginas
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"  # Página inicial por defecto
    
# Página inicial
if st.session_state.pagina == "inicio":
    # Crear columnas para organizar el diseño (entrada en la izquierda y resultados en la derecha)
    col1, espacio, col2 = st.columns([2, 0.5, 3])

    with col1:
        st.header("1. Ingresa los datos")
        semilla_input = st.text_input("Ingresa tu semilla (número de dígitos pares y mayor a 0):")
        constante_input = st.text_input("Ingresa tu constante (número de dígitos pares y mayor a 0):")
        iteraciones_input = st.number_input("Ingresa las iteraciones:", min_value = 0, max_value = 30, step = 1)
    

    # Si ambos inputs están llenos, hacer las validaciones y mostrar los resultados
    if semilla_input and constante_input and iteraciones_input:
        try:
            semilla1 = int(semilla_input)  # Convertir la semilla a entero
            constante = int(constante_input)  # Convertir la semilla a entero
            iteraciones = int(iteraciones_input)  # Convertir las iteraciones a entero

            # Validación de las condiciones de entrada
            if semilla1 > 0 and len(str(semilla1)) % 2 == 0 and constante > 0 and len(str(constante)) % 2 == 0 and iteraciones > 0:
                # Obtener los resultados de las operaciones
                resultados = multiplicador_constante(constante, semilla1, iteraciones) 
                
                # Guardar los resultados en session_state para usarlos en otra página
                st.session_state.datos = resultados
                            
                # Mostrar la tabla en la columna derecha
                with col2:
                    st.header("Tabla Generada con Multiplicador Constante")
                                    
                    # Convertir la lista de diccionarios en un DataFrame
                    df = pd.DataFrame(resultados)
                    
                    df.index = df.index + 1
                    df = df.rename_axis("Iteración")
                    st.dataframe(df, use_container_width = True)  
                    
                with col1:
                    st.divider()
                    st.header("2. Genera")
                    if st.button("Ir a Prueba de Huecos"):
                        st.session_state.pagina = "Resolver"
                        st.rerun()  # Recarga la página               

            else:
                st.error("Recuerda que la semilla debe tener un número de dígitos pares y mayor a 0, y las iteraciones deben ser mayores a 0.")
        except ValueError:
            st.error("Por favor, ingresa valores numéricos válidos para la semilla y las iteraciones.")
            
# Página de resolución
elif st.session_state.pagina == "Resolver":
    # Crear columnas para organizar el diseño (entrada en la izquierda y resultados en la derecha)
    col1, espacio, col2 = st.columns([2, 0.2, 3])
    
    if "resultados" in st.session_state:  # Verifica que los datos existan
        resultados = st.session_state.resultados

    if "datos" in st.session_state:  # Verifica que los datos existan
        datos = st.session_state["datos"]
    
        with col1:
            # Crear un DataFrame solo con la columna 'ri'
            df_ri = pd.DataFrame(datos)[['ri']]

            # Mostrar la tabla con solo la columna 'ri'
            st.subheader("Números Pseudoaleatorios")
            df_ri.index += 1
            df = df_ri.rename_axis("Datos")
            st.dataframe(df, use_container_width=True)

        with col2:
            st.subheader("Ingreso de Datos")

            # Intervalo de confianza
            intervalo_de_cf = st.number_input("Ingresa el intervalo de confianza:", min_value=0, max_value=100, step=1)

            intervalo_alfa = st.number_input("Ingresa el intervalo de alfa:", min_value=0.0, max_value=1.0, step=0.01, format="%f")

            intervalo_beta = st.number_input("Ingresa el intervalo de beta:", min_value=0.0, max_value=1.0, step=0.01, format="%f")

            # Alpha
            alpha = (100 - intervalo_de_cf) / 100
            
            # Grados de libertad
            grados_de_libertad = 6 - 1

            resultados_intervalos = []

            # Verificar que alfa < beta
        if intervalo_beta:
            if intervalo_beta > intervalo_alfa:
                for i in range(len(df_ri)):
                    if df_ri.iloc[i]['ri'] > intervalo_alfa and df_ri.iloc[i]['ri'] < intervalo_beta:
                        intervalo = 1
                    else:
                        intervalo = 0

                    resultados_intervalos.append({
                        'Pertenece al intervalo': intervalo,
                    })

                st.subheader("Validación de números pseudoaleatorios en intervalos")
                df_resultados_intervalos = pd.DataFrame(resultados_intervalos)
                df_resultados_intervalos = df_resultados_intervalos.rename_axis("Número de Dato")
                df_resultados_intervalos.index += 1

                # Agregar columna con los valores de 'ri'
                df_resultados_intervalos.insert(0, 'ri', df_ri['ri'].values)
                
                st.dataframe(df_resultados_intervalos, use_container_width=True)
                
                # Tabla de Prueba de Huecos
                st.subheader("Tabla de Prueba de Huecos")

                # Inicializar variables
                huecos = []  # Para almacenar el tamaño de los huecos
                conteo_huecos = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}  # Inicializar con los tamaños de hueco esperados
                contador = False
                tamaño_hueco = 0

                # Iterar sobre la columna 'Pertenece al intervalo' para contar los huecos
                for i in range(1, len(df_resultados_intervalos)):
                    if df_resultados_intervalos.iloc[i-1]['Pertenece al intervalo'] == 1 and df_resultados_intervalos.iloc[i]['Pertenece al intervalo'] == 1:  # Dos 1 consecutivos
                        tamaño_hueco = 0
                        huecos.append(tamaño_hueco)  # Hueco de tamaño 0
                    elif df_resultados_intervalos.iloc[i-1]['Pertenece al intervalo'] == 1 and df_resultados_intervalos.iloc[i]['Pertenece al intervalo'] == 0:  # Primer 1 y luego ceros
                        contador = True
                        tamaño_hueco = 1  # Comenzamos a contar el primer cero
                    elif df_resultados_intervalos.iloc[i-1]['Pertenece al intervalo'] == 0 and df_resultados_intervalos.iloc[i]['Pertenece al intervalo'] == 0 and contador:  # Ceros después del primer 1
                        tamaño_hueco += 1
                    elif df_resultados_intervalos.iloc[i-1]['Pertenece al intervalo'] == 0 and df_resultados_intervalos.iloc[i]['Pertenece al intervalo'] == 1 and contador:  # Cero seguido de un 1
                        # Si el hueco es mayor o igual a 5, lo contamos como 5
                        if tamaño_hueco >= 5:
                            tamaño_hueco = 5
                        huecos.append(tamaño_hueco)
                        tamaño_hueco = 0
                        contador = False

                # Contar las repeticiones de cada hueco
                for hueco in huecos:
                    if hueco in conteo_huecos:
                        conteo_huecos[hueco] += 1
                    else:
                        conteo_huecos[hueco] = 1

                # Asegurarse de que todos los tamaños de hueco estén presentes
                resultados_huecos = []
                total = 0
                
                for i in range(6):  # Para tamaños de hueco 0 a 4
                    
                    if i in conteo_huecos:
                        Oi = conteo_huecos[i]
                        resultados_huecos.append({
                            'Tamaño de Hueco (i)': i,
                            'Observadas': conteo_huecos[i],
                            'Esperada (Ei)': 1,  
                            '(Ei - Oi)^2 / Ei': 1,
                        })
                    total += Oi  # Acumulamos el total
                
                # Calculando ei y (ei - oi)^2 / ei
                
                total_estadistico = 0
                
                for i in range(6):
                    # Obtener Observada (Oi)
                    Oi = conteo_huecos.get(i, 0)  # Si no está en el conteo, asignamos 0

                    # Calcular Esperada (Ei)
                    Ei = total * (intervalo_beta - intervalo_alfa) * (1 - (intervalo_beta - intervalo_alfa))**i 

                    # Calcular (Ei - Oi)^2 / Ei
                    estadistico = (Ei - Oi)**2 / Ei if Ei != 0 else 0  # Asegurarnos de no dividir por cero
                    
                    # Total
                    total_estadistico += estadistico

                    # Actualizar el valor en la tabla
                    for row in resultados_huecos:
                        if row['Tamaño de Hueco (i)'] == i:
                            row['Esperada (Ei)'] = Ei
                            row['(Ei - Oi)^2 / Ei'] = estadistico
                            
                # Fila de total
                resultados_huecos.append({
                    'Tamaño de Hueco (i)': 'Total',
                    'Observadas': total,
                    'Esperada (Ei)': None,
                    '(Ei - Oi)^2 / Ei': total_estadistico                    
                })
                                    
                # Crear DataFrame con los resultados
                df_resultados_huecos = pd.DataFrame(resultados_huecos)
                st.dataframe(df_resultados_huecos, use_container_width=True, hide_index=True)
                                
                # Muestra la imagen de la tabla Chi Cuadrada            
                st.image("assets/chi_cuadrada.png", caption = "Tabla de Chi Cuadrada.")
                
                # Valor en tabla de chi cuadrada
                chi2_critico = stats.chi2.ppf(1 - alpha, grados_de_libertad)

                # Estadístico de chi cuadrada
                st.write(f"El estadístico en tabla de Prueba de Huecos fue {total_estadistico}")
                
                # Mostrar el valor crítico para referencia
                st.write(f"Valor crítico de chi-cuadrada: {chi2_critico}")

                # Ahora compara el valor calculado (chi_cuadrada) con el valor crítico
                if total_estadistico < chi2_critico:
                    st.success("Se acepta la hipótesis nula")
                else:
                    st.error("Hipótesis nula rechazada")
            else:
                st.error("El valor de alfa debe ser menor al de beta.")
    else:
        st.error("No hay datos disponibles. Regresa a la página principal.")

    with st.expander("Hecho por:"):
        st.write("Rodrigo González López S4A")