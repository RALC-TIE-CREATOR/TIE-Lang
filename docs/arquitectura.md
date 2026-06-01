
# TIE-Lang — Arquitectura v1.0

## Capas del sistema

TIE-Lang está organizado como un sistema en capas:

1. `core/`
   Implementa la base topológica y las operaciones lógicas y aritméticas primitivas.

2. `cpu/`
   Expone una CPU virtual de 4 bits con registros, flags, RAM, pila y saltos.

3. `compiler/`
   Traduce el lenguaje fuente a instrucciones de la CPU.

4. `tests/`
   Verifica cada capa de forma independiente y también el pipeline completo.

## Flujo de ejecución

El flujo actual es:

1. El `lexer` tokeniza el código fuente.
2. El `parser` construye un AST.
3. El `compiler` baja el AST a instrucciones de la CPU.
4. La `CPU` ejecuta esas instrucciones usando RAM, flags y pila.

## Modelo de compilación

- Variables: se asignan a direcciones fijas en RAM.
- Expresiones: usan registros temporales, principalmente `R0` y `R1`.
- Retorno de funciones: `R3`.
- Etiquetas: se generan para comparaciones, control de flujo y funciones.

## Modelo de función

- Los argumentos entran por `R0` a `R3`.
- Al entrar a una función se copian a los slots de RAM asociados a sus parámetros.
- El valor de retorno se deja en `R3`.

## Modelo actual de máquina

- CPU de 4 bits
- 4 registros generales
- flags `Z`, `N`, `C`
- RAM de 16 celdas
- pila para `CALL` y `RET`

## Observación importante

La semántica del lenguaje en v1.0 está definida por la máquina de 4 bits actual.
Eso significa que el compilador no está modelando enteros abstractos infinitos,
sino programas que corren sobre una CPU concreta con wraparound modular.

## Apertura de v0.3.0

La siguiente etapa del proyecto abre una nueva capa experimental:

5. `topology/`
   Introduce un backend de ejecución topológica en paralelo al backend
   estable de CPU. Su primera versión no busca reemplazar la máquina actual,
   sino modelar memoria y transición sobre una red cúbica mediante lazos
   cerrados autoevitantes y carga topológica discreta.

## Arquitectura dual a partir de v0.3.0

Desde `v0.3.0`, TIE-Lang pasa a tener dos rutas:

1. Ruta estable
   `source -> lexer -> parser -> compiler -> 4-bit CPU -> execution`

2. Ruta topológica experimental
   `topological state -> lattice/loop runtime -> measured topological state`

La intención es que, con el tiempo, una parte del compilador pueda bajar un
subconjunto del lenguaje a esta segunda ruta sin perder la primera.
