# malbolge-oracle

**Control de ejecucion independiente para Malbolge.**

No es otro interprete para correr tus programas — es un *control*: un runtime
escrito para implementar la semantica de referencia literalmente, para que otras
implementaciones puedan verificarse contra algo que no comparte ascendencia con
ellas.

```python
from oracle import Oracle

machine = Oracle()
machine.load_ascii("(=<`#9]~6ZY32Vx/4Rs+0No-&Jk)\"Fh}|Bcy?`=*z]Kw%oG4UUS0/@-ejc(:'8dc")
result = machine.run(max_steps=1_000_000)

result.output       # 'Hello World!'
result.halted       # True
result.halt_reason  # 'halt_opcode'
result.steps        # 40
result.a, result.c, result.d
result.memory       # las 59049 celdas completas
```

Sin dependencias. Python 3.10+, solo libreria estandar.

## Por que un control en vez de un interprete

Las implementaciones de Malbolge discrepan entre si de formas que son invisibles
hasta que las comparas. No en hello-world — en que pasa al EOF, en que estado
esta la maquina despues de parar, en si una celda fuera de rango es un
crash o un no-op.

Comparar dos interpretes que se escribieron leyendo el uno al otro dice
poco. Este se escribio desde la semantica de referencia y nada mas, asi que
cuando discrepa con un runtime, la discrepancia es informativa.

Reporta el estado completo de la maquina despues de una corrida — registros,
conteo de pasos, razon de halt y las 59,049 celdas completas — porque un control
que solo te dice que se imprimo no te puede ayudar a averiguar *por que* dos
implementaciones difieren.

## Procedencia

La semantica se transcribio del pseudocodigo del interprete en **Iizawa
(2005), Appendix C** ("Malbolge インタープリタ 実行部").

Ese pseudocodigo es en si mismo una transcripcion del **interprete de referencia** para
el lenguaje: 13 de sus 19 lineas aparecen textualmente en el `malbolge.c` de referencia
que ha circulado publicamente desde 1998 — incluyendo cada una decisiva: el
descifrado `xlat1`, el rotate ternario, y la regla de EOF. Entonces la fuente principal es
el interprete de referencia; Iizawa es donde se leyo.

Las tablas de traduccion (`xlat1`/`xlat2`) y las primitivas `op`/`rot` son
constantes publicas de la especificacion de Malbolge y se declaran aqui
independientemente.

**No se consulto, reutilizo ni copio ninguna otra implementacion de Malbolge al
escribir este modulo.** Ese es todo su valor.

## Divergencias

Donde se sabe que las implementaciones discrepan, este toma una postura y lo
dice. Ver [`DIVERGENCES.md`](DIVERGENCES.md) — actualmente dos, ambas fijadas con
pruebas.

## Pruebas

```sh
python -m pytest test_oracle.py -v      # o: python test_oracle.py
```

17 pruebas, sin dependencias. Verifican el oraculo contra hechos establecidos
independientemente de cualquier runtime: las formas de las tablas publicadas,
la aritmetica de las primitivas ternarias contra la tabla de verdad de la
especificacion, el hello-world canonico, y las dos divergencias.

## Licencia

MIT. Ver [`LICENSE`](LICENSE).
