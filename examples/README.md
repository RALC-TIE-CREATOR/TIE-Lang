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

O desde CLI:

```bash
python -m compiler.run examples/fibonacci.tie
python tie.py examples/fibonacci.tie
```

## Ejemplos disponibles

### fibonacci.tie
Calcula la secuencia de Fibonacci dentro del límite de 4 bits.

Nota: la CPU actual es de 4 bits, así que las operaciones
aritméticas hacen wraparound modular cuando exceden 15.
Por eso este ejemplo usa un contador fijo de iteraciones.

### funciones.tie
Demuestra funciones, retorno y comparaciones usando la sintaxis
recomendada con comas en argumentos.

Salida esperada: `8, 6, 9`

### busqueda.tie
Demuestra acumulación y condicionales para seleccionar el máximo
de una secuencia fija.

Salida esperada: `9`

### comparadores.tie
Demuestra que los comparadores producen booleanos normalizados.

Salida esperada: `1, 0, 1, 1, 1, 1`

## Sintaxis oficial

Para v1.0, la sintaxis pública recomendada en ejemplos es la forma
con comas en argumentos de función:

```tie
def max(a, b):
    return a
```

La forma sin comas sigue funcionando por compatibilidad, pero no es
la sintaxis recomendada para documentación pública nueva.
