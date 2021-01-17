# BFIMDM

BrainFuck with Interlaced Multi-Dimensional Memory

## Why

- Bachelor's thesis (_Esoteric programming languages and support for real numbers_)
- Using tape memory as 2-dimensional one is annoying when you can't even dump the memory in 2 dimensions.

## Features

- Currently only supports 2-dimensional memory. Support for N-dimensions might be added later on.
- Support for tagged memory dumps using `#dumpname` (e. g. `#result`)
- Support for loading initial 2-dimensional layer values from the header of the code

## Installation

- Python package structure might be created later on.

## Usage

Set layer names and memory from the code

```python
from bfimdm import Runtime

rt = Runtime()
rt.set_layer_names(["input", "tmp", "output"])
rt.set_memory([
  [1, 2, 3, 4],
  [0, 0, 0, 0],
  [0, 0, 0, 0],
])
rt.print_steps = False

rt.run_code("[-$$+^^]>[-$$+^^]>[-$$+^^]>[-$$+^^]<<<")
```

Set layer names from the code file

```python
from bfimdm import Runtime

rt = Runtime()
rt.read("./example.bf")
rt.print_steps = False
rt.run()

# Print executed Brainfuck instructions
print("Executed brainfuck:")
print(rt.get_executed_brainfuck())
```

Example of code file that could be loaded (same layer names and initial memory as in the previous example).

Note that specifying all-zero-values for layers is not required (see tmp-layer below).

```
Layer input   1   2   3   4
Layer tmp
Layer output  0   0   0   0

move value from input{0} to output{0}
[-$$+^^]

go to column 2
>

move value from input{1} to output{1}
[-$$+^^]

go to column 3
>

move value from input{2} to output{2}
[-$$+^^]

go to column 4
>

move value from input{3} to output{3}
[-$$+^^]

go back to input{0}
<<<
```

## Examples

There are two examples in the root of this repository.

`addition.bf` adds two fixed-point binary numbers together and `multiplication.bf` multiplies a fixed-point binary number with another one.

`addition.py` runs `addition.bf` and `multiplication.py` runs `multiplication.bf`.
