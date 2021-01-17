from bfimdm import Runtime

rt = Runtime()
rt.read("./multiplication.bf")
rt.print_steps = False

rt.run()

print("CODE:")
print(rt.get_executed_brainfuck())
