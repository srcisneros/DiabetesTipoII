# -*- coding: utf-8 -*-
"""TesisDiabetesMellitus.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1O0kGqJijSoSaGf1IUb_ze1lhtTkxJlz5

# Importación de librerías necesarias
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (confusion_matrix, classification_report, roc_auc_score,
                             roc_curve, accuracy_score, precision_score, recall_score, f1_score)
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from imblearn.over_sampling import SMOTE
from tabulate import tabulate

"""# Cargar datos"""

datos = pd.read_csv('diabetesTotall.csv')

"""# imprime el numero de registros y columnas"""

datos.shape
datos.info()

"""#Registros Duplicados"""

# Verificar si hay registros duplicados
duplicados = datos.duplicated()

# Contar el número de registros duplicados
numero_duplicados = duplicados.sum()
print(f"Número de registros duplicados: {numero_duplicados}")

# Mostrar los registros duplicados si existen
if numero_duplicados > 0:
    print("Registros duplicados:")
    print(datos[duplicados])
else:
    print("No se encontraron registros duplicados.")

datos.describe()

datos.head()

"""#Selección de características relevantes según el análisis de correlación"""

caracteristicas_relevantes = ['Edad', 'Glucosa', 'HbA1c', 'Colesterol', 'Trigliceridos', 'HDL', 'LDL', 'IMC']
datos = datos[caracteristicas_relevantes + ['Diabetes']]  # Mantener solo las columnas

"""# Separar las características (X) y la variable objetivo (y)"""

X = datos.drop(columns=['Diabetes'])  # Variables predictoras
y = datos['Diabetes']  # Variable objetivo

"""# Manejo de clases desbalanceadas utilizando SMOTE"""

smote = SMOTE(random_state=42)  # Inicialización de SMOTE
X_resampleado, y_resampleado = smote.fit_resample(X, y)  # Generar ejemplos sintéticos

"""# Escalado de las características para normalización"""

escalador = StandardScaler()  # Inicialización del escalador
X_escalado = escalador.fit_transform(X_resampleado)  # Aplicar escalado

"""# División del conjunto de datos en entrenamiento y prueba"""

X_entrenamiento, X_prueba, y_entrenamiento, y_prueba = train_test_split(
    X_escalado, y_resampleado, test_size=0.3, stratify=y_resampleado, random_state=42)

"""# Definición de modelos y sus hiperparámetros para optimización"""

modelos_optimizar = {
    'Bosque Aleatorio': {  # Random Forest
        'modelo': RandomForestClassifier(random_state=42),
        'parametros': {
            'n_estimators': [100, 200, 500],  # Número de árboles en el bosque
            'max_depth': [10, 20, None],  # Profundidad máxima de cada árbol
            'min_samples_split': [2, 5, 10],  # Mínimo de muestras necesarias para dividir un nodo
            'min_samples_leaf': [1, 2, 4]  # Mínimo de muestras en una hoja
        }
    },
    'Regresión Logística': {  # Logistic Regression
        'modelo': LogisticRegression(random_state=42, max_iter=1000),
        'parametros': {
            'C': [0.01, 0.1, 1, 10],  # Parámetro de regularización
            'solver': ['liblinear', 'lbfgs']  # Algoritmos de optimización
        }
    },
    'KNN': {  # K-Nearest Neighbors
        'modelo': KNeighborsClassifier(),
        'parametros': {
            'n_neighbors': [3, 5, 10],  # Número de vecinos
            'weights': ['uniform', 'distance'],  # Pesos para los vecinos
            'metric': ['euclidean', 'manhattan']  # Métrica de distancia
        }
    },
    'Máquinas de Soporte Vectorial': {  # Support Vector Machines
        'modelo': SVC(probability=True, random_state=42),
        'parametros': {
            'C': [0.1, 1, 10],  # Parámetro de regularización
            'gamma': ['scale', 'auto'],  # Coeficiente del núcleo
            'kernel': ['linear', 'rbf']  # Tipo de núcleo
        }
    },
    'Red Neuronal': {  # Neural Network
        'modelo': MLPClassifier(random_state=42, max_iter=1000),
        'parametros': {
            'hidden_layer_sizes': [(50, 25, 10), (100, 50), (50,)],  # Estructura de capas ocultas
            'activation': ['relu', 'tanh'],  # Función de activación
            'solver': ['adam', 'sgd'],  # Optimizadores
            'alpha': [0.0001, 0.001, 0.01]  # Parámetro de regularización
        }
    }
}

"""# Entrenamiento y evaluación de los modelos"""

resultados = []  # Lista para almacenar resultados
for nombre, configuracion in modelos_optimizar.items():
    print(f"Optimizando {nombre}...")
    # Búsqueda de los mejores hiperparámetros
    grid_search = GridSearchCV(configuracion['modelo'], configuracion['parametros'], cv=5, scoring='accuracy', n_jobs=-1, verbose=1)
    grid_search.fit(X_entrenamiento, y_entrenamiento)
    mejor_modelo = grid_search.best_estimator_

    # Predicciones y evaluación
    y_predicho = mejor_modelo.predict(X_prueba)
    y_probabilidad = mejor_modelo.predict_proba(X_prueba)[:, 1] if hasattr(mejor_modelo, "predict_proba") else None
    exactitud = accuracy_score(y_prueba, y_predicho)  # Exactitud del modelo
    auc = roc_auc_score(y_prueba, y_probabilidad) if y_probabilidad is not None else None  # AUC
    precision = precision_score(y_prueba, y_predicho)  # Precisión
    sensibilidad = recall_score(y_prueba, y_predicho)  # Sensibilidad
    f1 = f1_score(y_prueba, y_predicho)  # F1-Score

    # Almacenar resultados
    resultados.append({
        'Modelo': nombre,
        'Mejores Hiperparámetros': grid_search.best_params_,
        'Exactitud': exactitud,
        'AUC': auc,
        'Precisión': precision,
        'Sensibilidad': sensibilidad,
        'F1-Score': f1
    })

    # Matriz de confusión
    matriz_confusion = confusion_matrix(y_prueba, y_predicho)
    plt.figure(figsize=(6, 4))
    sns.heatmap(matriz_confusion, annot=True, fmt='d', cmap='Blues', cbar=False)
    plt.title(f'Matriz de Confusión - {nombre}')
    plt.xlabel('Predicción')
    plt.ylabel('Real')
    plt.show()

    # Curva ROC si aplica
    if y_probabilidad is not None:
        fpr, tpr, _ = roc_curve(y_prueba, y_probabilidad)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'{nombre} (AUC = {auc:.2f})')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.title(f'Curva ROC - {nombre}')
        plt.xlabel('Tasa de Falsos Positivos')
        plt.ylabel('Tasa de Verdaderos Positivos')
        plt.legend()
        plt.show()

"""# Mostrar resultados finales"""

resultados_df = pd.DataFrame(resultados)
#print("Resultados Finales:")
#print(resultados_df)

# Convertir la DataFrame a una lista de listas para imprimir con `tabulate`
tabla_resultados = resultados_df.values.tolist()

# Definir los encabezados de las columnas
encabezados = resultados_df.columns.tolist()

# Imprimir la tabla formateada
print(tabulate(tabla_resultados, headers=encabezados, tablefmt='grid'))

"""# Gráficos de comparación"""

plt.figure(figsize=(12, 6))
sns.barplot(x='Modelo', y='Exactitud', data=resultados_df)
plt.title('Comparación de Exactitud entre Modelos Optimizados')
plt.ylabel('Exactitud')
plt.show()

sns.barplot(x='Modelo', y='AUC', data=resultados_df.dropna())
plt.title('Comparación de AUC entre Modelos Optimizados')
plt.ylabel('AUC')
plt.show()