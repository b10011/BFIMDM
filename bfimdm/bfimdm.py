import click
import re
from pathlib import Path


def unindent(code):
    min_indent = float("inf")
    lines = code.splitlines()
    for line in lines:
        match = re.search(r"^(\s*)\S.*$", line)
        if match:
            min_indent = min(min_indent, len(match.group(1)))

    return "\n".join([line[min_indent:] for line in lines])


def find_all(sourcestr, searchstr):
    indices = []
    index = sourcestr.find(searchstr)
    while index != -1:
        indices.append(index)
        index = sourcestr.find(searchstr, index + 1)
    return indices


class Runtime:
    def __init__(self):
        self.bits = 8
        self.bits_mod = 2 ** self.bits
        self.code = ""
        self.memory = [0]
        self.layer_count = 1
        self.layer_names = []
        self.layer_names_longest = 0
        self.code_pointer = -1
        self.memory_pointer = 0
        self.jumps = dict()
        self.lock_layer = True
        self.executed_code = ""
        self.output = ""
        self.print_steps = True
        self.suppress_output = False

    def run(self):
        if self.print_steps and not self.suppress_output:
            self.print()
        done = False
        while not done:
            done, command = self.step()
            if self.print_steps and not self.suppress_output and not done:
                click.echo(
                    "{}: {}".format(click.style("Next", fg="red"), command)
                )
                self.print()
                print()

    def read(self, readable):
        if isinstance(readable, str):
            with open(readable, "r") as f:
                code = f.read()
        elif isinstance(readable, Path):
            code = readable.read_text()
        elif hasattr(readable, "read"):
            code = readable.read()

        layernames = []
        layervalues = []
        mostcolumns = 0
        for line in code.splitlines():
            match = re.search(r"Layer\s+(\S+)\s*([0-9\s]*)", line)
            if match:
                name = match.group(1)
                values = [
                    int(value) for value in match.group(2).strip().split()
                ]
                mostcolumns = max(mostcolumns, len(values))
                layernames.append(name)
                layervalues.append(values)
            else:
                break

        for values in layervalues:
            while len(values) < mostcolumns:
                values.append(0)

        self.set_layer_names(layernames)
        self.set_memory(layervalues)
        self.set_code(code)

    def run_code(self, code):
        self.set_code(code)
        self.run()

    def step(self):
        command = " "
        while command not in "+-<>^$,.[]#":
            if self.code_pointer >= len(self.code) - 1:
                return (True, None)
            self.code_pointer += 1
            command = self.code[self.code_pointer]

        if command == "+":
            self.memory[self.memory_pointer] = (
                self.memory[self.memory_pointer] + 1 + self.bits_mod
            ) % self.bits_mod

        elif command == "-":
            self.memory[self.memory_pointer] = (
                self.memory[self.memory_pointer] - 1 + self.bits_mod
            ) % self.bits_mod

        elif command == "<":
            if self.lock_layer:
                self.memory_pointer -= self.layer_count
            else:
                self.memory_pointer -= 1

        elif command == ">":
            if self.lock_layer:
                self.memory_pointer += self.layer_count
            else:
                self.memory_pointer += 1
            while self.memory_pointer >= len(self.memory):
                self.memory.append(0)

        elif command == "^":
            self.memory_pointer -= 1

        elif command == "$":
            self.memory_pointer += 1
            while self.memory_pointer >= len(self.memory):
                self.memory.append(0)

        elif command == ".":
            self.output += chr(self.memory[self.memory_pointer])

        elif command == "[":
            if self.memory[self.memory_pointer] == 0:
                self.code_pointer = self.jumps[self.code_pointer]
            else:
                return self.step()

        elif command == "]":
            if self.memory[self.memory_pointer] != 0:
                self.code_pointer = self.jumps[self.code_pointer]
            else:
                return self.step()

        elif command == "#":
            match = re.search(
                r"^#([a-zA-Z0-9_]+)", self.code[self.code_pointer :]
            )
            if not self.suppress_output:
                if match:
                    print('Dump "{}"'.format(match.group(1)))
                else:
                    print("Unnamed dump")
                self.print()
                print()

        return (False, command)

    def set_bits(self, bits):
        self.bits = bits
        self.bits_mod = 2 ** self.bits

    def set_memory(self, memory):
        self.layer_count = len(memory)
        self.memory = [i for i in list(zip(*memory)) for i in i]

    def set_cell(self, layer, index, value):
        if isinstance(layer, str):
            layer = self.layer_names.index(layer)
        self.memory[index * self.layer_count + layer] = value

    def get_cell(self, layer, index):
        if isinstance(layer, str):
            layer = self.layer_names.index(layer)
        return self.memory[index * self.layer_count + layer]

    def set_layer_names(self, names):
        self.layer_names = names
        self.set_layer_count(len(names))
        self.layer_names_longest = max(len(name) for name in names)

    def set_layer_count(self, count):
        self.layer_count = count

    def set_code(self, code):
        self.code = code

        if self.lock_layer:
            self.executed_code += (
                self.code.replace("<", "<" * self.layer_count)
                .replace(">", ">" * self.layer_count)
                .replace("^", "<")
                .replace("$", ">")
            )
        else:
            self.executed_code += self.code

        starts = find_all(code, "[")
        ends = find_all(code, "]")
        loops = []
        self.jumps = dict()
        for i in sorted(starts + ends):
            if code[i] == "[":
                loops.append(i)
            elif code[i] == "]":
                loop = loops.pop()
                self.jumps[i] = loop
                self.jumps[loop] = i

        self.code_pointer = -1

    def print(self):
        for row in range(self.layer_count):
            if self.layer_names:
                click.echo(
                    "{} | ".format(
                        click.style(
                            "{{:{}s}}".format(self.layer_names_longest).format(
                                self.layer_names[row]
                            ),
                            fg="cyan",
                        )
                    ),
                    nl=False,
                )
            for col, value in enumerate(self.memory[row :: self.layer_count]):
                is_current = (
                    self.memory_pointer == col * self.layer_count + row
                )
                click.secho(
                    "{:3d} ".format(value),
                    nl=False,
                    fg="red"
                    if is_current
                    else ("bright_black" if value == 0 else None),
                )
            print()
        click.echo(
            "{}: {}".format(click.style("Output", fg="green"), self.output)
        )

    def get_executed_brainfuck(self):
        code = self.executed_code

        # Remove all non-brainfuck characters
        code = re.sub(r"[^\<\>\+\-\[\]\.\,]", r"", code)

        # Remove useless command pairs from the code (e. g. ">><" only does ">")
        oldlength = 0
        while oldlength != len(code):
            oldlength = len(code)
            for p in ["><", "<>", "+-", "-+"]:
                code = code.replace(p, "")

        return code
