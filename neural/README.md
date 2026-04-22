# TIE-Lang — Neural Layer (Experimental)

Esta carpeta contiene la primera base experimental para la capa neural
de TIE-Lang.

La meta de esta fase no es construir todavía una red profunda completa,
sino demostrar que el proyecto ya puede extenderse desde:

- lógica topológica
- CPU y compilador
- hacia una capa de aprendizaje mínima y verificable

## Estado actual

La implementación inicial incluye:

- `TopologicalPerceptron`
- `TopologicalMLP`
- entrenamiento binario sobre compuertas linealmente separables
- una red mínima para `XOR`
- pruebas reproducibles para `AND`, `OR` y `XOR`

## Idea

En esta primera aproximación, los pesos se representan como estados
enteros persistentes. Es una simplificación ejecutable de la intuición
de TIE: pesos robustos, discretos y resistentes a degradación accidental.

## Uso rápido

```python
from neural import build_xor_model, train_boolean_model

model = train_boolean_model("AND")
print(model.weights, model.bias)
print(model.predict([1, 1]))  # 1
print(model.predict([0, 1]))  # 0

xor = build_xor_model()
print(xor.predict([0, 1]))  # 1
print(xor.predict([1, 1]))  # 0
```

## Alcance

Esto es una base mínima, no una capa neural completa.
Los siguientes pasos naturales serían:

- datasets más ricos
- visualización del aprendizaje
- conexión explícita con pesos topológicos persistentes en la infraestructura
