# TIE-Lang — Ejemplos

Programas de ejemplo escritos en TIE-Lang v1.0.
Cada archivo `.tie` es código fuente de alto nivel
que el compilador transforma en instrucciones CPU topológicas.

## Ejecutar un ejemplo

```python
from compiler.compiler import compile_and_run

# Leer y ejecutar un archivo .tie
with open('examples/fibonacci.tie') as f:
    fuente = f.read()

compile_and_run(fuente, titulo="Fibonacci")
```

## Ejemplos disponibles

### fibonacci.tie
Calcula la secuencia de Fibonacci dentro del límite de 4 bits.
