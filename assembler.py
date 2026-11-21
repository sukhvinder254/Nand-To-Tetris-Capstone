import os
import sys

SYMBOLS = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
           "SCREEN": 16384, "KBD": 24576}
for i in range(16):
    SYMBOLS["R%d" % i] = i

COMP_A0 = {
    "0": "101010", "1": "111111", "-1": "111010",
    "D": "001100", "A": "110000", "!D": "001101", "!A": "110001",
    "-D": "001111", "-A": "110011", "D+1": "011111", "A+1": "110111",
    "D-1": "001110", "A-1": "110010", "D+A": "000010", "D-A": "010011",
    "A-D": "000111", "D&A": "000000", "D|A": "010101",
}
COMP = {}
for k, v in COMP_A0.items():
    COMP[k] = "0" + v
    if "A" in k:
        COMP[k.replace("A", "M")] = "1" + v

DEST = {"": "000", "M": "001", "D": "010", "MD": "011",
        "A": "100", "AM": "101", "AD": "110", "AMD": "111"}
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}


def clean(line):
    return "".join(line.split("//")[0].split())


def translate_c(line):
    dest, comp, jump = "", line, ""
    if "=" in line:
        dest, comp = line.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)
    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def main():
    if len(sys.argv) != 2:
        print("Usage: python assembler.py Prog.asm")
        sys.exit(1)

    path = sys.argv[1]
    with open(path) as f:
        lines = [clean(l) for l in f]
    lines = [l for l in lines if l]

    # first reading: labels
    labels = {}
    code = []
    n = 0
    for line in lines:
        if line.startswith("(") and line.endswith(")"):
            labels[line[1:-1]] = n
        else:
            code.append(line)
            n += 1

    # second reading: translate
    variables = {}
    next_var = 16
    out = []
    for line in code:
        if line.startswith("@"):
            x = line[1:]
            if x.isdigit():
                value = int(x)
            elif x in SYMBOLS:
                value = SYMBOLS[x]
            elif x in labels:
                value = labels[x]
            elif x in variables:
                value = variables[x]
            else:
                variables[x] = next_var
                value = next_var
                next_var += 1
            out.append(format(value, "016b"))
        else:
            out.append(translate_c(line))

    base = os.path.splitext(path)[0]
    with open(base + ".hack", "w") as f:
        f.write("\n".join(out) + "\n")

    # extra feature (K=72, K mod 3 = 0): symbols.txt
    folder = os.path.dirname(os.path.abspath(path))
    with open(os.path.join(folder, "symbols.txt"), "w") as f:
        f.write("# Labels\n")
        for name, addr in labels.items():
            f.write("%s %d\n" % (name, addr))
        f.write("# Variables\n")
        for name, addr in variables.items():
            f.write("%s %d\n" % (name, addr))

    print("Wrote %s.hack (%d instructions) and symbols.txt" % (base, len(out)))


if __name__ == "__main__":
    main()          