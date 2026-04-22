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
- `TrainableTopologicalMLP`
- entrenamiento binario sobre compuertas linealmente separables
- una red mínima para `XOR`
- entrenamiento real de una red multicapa mínima para `XOR`
- historial de entrenamiento por época
- visualización textual de error, pesos y sesgo
- pruebas reproducibles para `AND`, `OR` y `XOR`

## Idea

En esta primera aproximación, los pesos se representan como estados
enteros persistentes. Es una simplificación ejecutable de la intuición
de TIE: pesos robustos, discretos y resistentes a degradación accidental.

## Uso rápido

```python
from neural import (
    build_xor_model,
    render_training_report,
    train_xor_mlp,
    train_boolean_model,
)

model = train_boolean_model("AND")
print(model.weights, model.bias)
print(model.predict([1, 1]))  # 1
print(model.predict([0, 1]))  # 0

training = model.train(
    [([0, 0], 0), ([0, 1], 1), ([1, 0], 1), ([1, 1], 1)],
    epochs=10,
)
print(render_training_report(training))

xor = build_xor_model()
print(xor.predict([0, 1]))  # 1
print(xor.predict([1, 1]))  # 0

mlp = train_xor_mlp()
print(mlp.predict([0, 1]))  # 1
print(mlp.predict([1, 1]))  # 0
```

## Alcance

Esto es una base mínima, no una capa neural completa.
Los siguientes pasos naturales serían:

- datasets más ricos
- visualización de entrenamiento multicapa
- conexión explícita con pesos topológicos persistentes en la infraestructura
