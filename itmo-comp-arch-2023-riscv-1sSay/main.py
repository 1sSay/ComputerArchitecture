import os
import sys


def printf(format, *args):
    sys.stdout.write(format % args)


""" 
TODO:
    RISC-V:
    RV32I
    RV32M

https://riscv.org/technical/specifications/

encodin: little endian
output:  ABI
"""


class ElfParser:
    idx: int
    data: bytes
    entry_types = {
        0: "NOTYPE",
        1: "OBJECT",
        2: "FUNC",
        3: "SECTION",
        4: "FILE",
        5: "COMMON",
        6: "TLS",
        10: "LOOS",
        12: "HIOS",
        13: "LOPROC",
        15: "HIPROC",
    }
    entry_binds = {
        0: "LOCAL",
        1: "GLOBAL",
        2: "WEAK",
        10: "LOOS",
        12: "HIOS",
        13: "LOPROC",
        15: "HIPROC",
    }
    entry_visibility = {0: "DEFAULT", 1: "INTERNAL", 2: "HIDDEN", 3: "PROTECTED"}

    def __init__(self) -> None:
        self.idx = 0
        self.data = b"0"

    def print_error(message: str, code: int = -1) -> None:
        sys.stderr.write(f"Error occured: {message}")
        exit(code)

    def get(self, cnt: int) -> bytes:
        result = self.data[self.idx : self.idx + cnt]
        self.idx += cnt
        return result

    def get_int(self, cnt: int) -> int:
        return int.from_bytes(self.get(cnt), "little")

    def get_file_header(self) -> dict:
        file_header = dict()
        try:
            self.idx = 0
            file_header["EI_MAG"] = self.get_int(4)
            file_header["EI_CLASS"] = self.get_int(1)
            file_header["EI_DATA"] = self.get_int(1)
            file_header["EI_VERSION"] = self.get_int(1)
            file_header["EI_OSABI"] = self.get_int(1)
            file_header["EI_ABIVERSION"] = self.get_int(1)
            file_header["EI_PAD"] = self.get_int(7)
            file_header["e_type"] = self.get_int(2)
            file_header["e_machine"] = self.get_int(2)
            file_header["e_version"] = self.get_int(4)

            if file_header["EI_CLASS"] == 1:
                file_header["e_entry"] = self.get_int(4)
                file_header["e_phoff"] = self.get_int(4)
                file_header["e_shoff"] = self.get_int(4)
            elif file_header["EI_CLASS"] == 2:
                file_header["e_entry"] = self.get_int(8)
                file_header["e_phoff"] = self.get_int(8)
                file_header["e_shoff"] = self.get_int(8)
            else:
                self.parse_elfrint_error(
                    f"Wrong ELF class\nExpected: 1 or 2\nActual: {file_header['EI_CLASS']}",
                    code=2,
                )

            file_header["e_flags"] = self.get_int(4)
            file_header["e_ehsize"] = self.get_int(2)
            file_header["e_phentsize"] = self.get_int(2)
            file_header["e_phnum"] = self.get_int(2)
            file_header["e_shentsize"] = self.get_int(2)
            file_header["e_shnum"] = self.get_int(2)
            file_header["e_shstrndx"] = self.get_int(2)

        except IndexError:
            self.print_error("Too small file", code=1)
        return file_header

    def get_section_header_table(self, header_size=40) -> dict:
        section_header_table = dict()
        if header_size == 40:
            section_header_table["sh_name"] = self.get_int(4)
            section_header_table["sh_type"] = self.get_int(4)
            section_header_table["sh_flags"] = self.get_int(4)
            section_header_table["sh_addr"] = self.get_int(4)
            section_header_table["sh_offset"] = self.get_int(4)
            section_header_table["sh_size"] = self.get_int(4)
            section_header_table["sh_link"] = self.get_int(4)
            section_header_table["sh_info"] = self.get_int(4)
            section_header_table["sh_addralign"] = self.get_int(4)
            section_header_table["sh_entsize"] = self.get_int(4)
        elif header_size == 64:
            section_header_table["sh_name"] = self.get_int(4)
            section_header_table["sh_type"] = self.get_int(4)
            section_header_table["sh_flags"] = self.get_int(8)
            section_header_table["sh_addr"] = self.get_int(8)
            section_header_table["sh_offset"] = self.get_int(8)
            section_header_table["sh_size"] = self.get_int(8)
            section_header_table["sh_link"] = self.get_int(4)
            section_header_table["sh_info"] = self.get_int(4)
            section_header_table["sh_addralign"] = self.get_int(8)
            section_header_table["sh_entsize"] = self.get_int(8)
        else:
            self.print_error("Wrong header size", code=4)
        return section_header_table

    def get_name(self, start, offset):
        idx = start + offset
        while self.data[idx] > 0:
            idx += 1
        return self.data[start + offset : idx]

    def get_entry(self, offset, size):
        entry = dict()
        self.idx = offset

        if size == 16:
            entry["st_name"] = self.get_int(4)
            entry["st_value"] = self.get_int(4)
            entry["st_size"] = self.get_int(4)
            entry["st_info"] = self.get_int(1)
            entry["st_other"] = self.get_int(1)
            entry["st_shndx"] = self.get_int(2)
        else:
            entry["st_name"] = self.get_int(8)
            entry["st_info"] = self.get_int(2)
            entry["st_other"] = self.get_int(2)
            entry["st_shndx"] = self.get_int(8)
            entry["st_value"] = self.get_int(8)
            entry["st_size"] = self.get_int(8)
        return entry

    def parse_elf(self, path: str) -> (list, list):
        with open(path, "rb") as elf:
            self.data = elf.read()

        text = None
        symtab = None
        strtab = None
        shstrtab = None

        try:
            file_header = self.get_file_header()
            section_header_table = self.get_section_header_table()

            self.idx = file_header["e_shoff"]
            if self.idx == 0:
                self.print_error("Zero section tables", code=2)

            section_headers = []

            for i in range(file_header["e_shnum"]):
                section = self.get_section_header_table(file_header["e_shentsize"])
                section_headers.append(section)

                if section["sh_type"] == 3 and i != file_header["e_shstrndx"]:
                    strtab = section.copy()
                if i == file_header["e_shstrndx"]:
                    shstrtab = section.copy()

            if strtab is None:
                self.print_error("No strtab in file", code=3)

            for section in section_headers:
                name = self.get_name(shstrtab["sh_offset"], section["sh_name"])

                if name == b".text":
                    text = section.copy()
                if name == b".symtab":
                    symtab = section.copy()

        except IndexError:
            self.print_error("File is too small", code=1)

        commands = []
        table = []

        if text is not None:
            offset = text["sh_offset"]
            size = text["sh_size"]
            if size % 4:
                self.print_error("Wrong text section size", code=1)
            for idx in range(offset, offset + size, 4):
                commands.append(int.from_bytes(self.data[idx : idx + 4], "little"))

        if symtab is not None:
            offset = symtab["sh_offset"]
            size = symtab["sh_size"]
            if size % symtab["sh_entsize"]:
                self.print_error("Wrong symtab size", code=1)
            for idx in range(offset, offset + size, symtab["sh_entsize"]):
                entry = self.get_entry(idx, symtab["sh_entsize"])

                current = dict()
                current["Value"] = entry["st_value"]
                current["Size"] = entry["st_size"]
                current["Type"] = self.entry_types[entry["st_info"] & 0xF]
                current["Bind"] = self.entry_binds[entry["st_info"] >> 4]
                current["Vis"] = self.entry_visibility[entry["st_other"] & 0x3]
                # current["Vis"] = "DEFAULT"

                match entry["st_shndx"]:
                    case 0:
                        current["Index"] = "UNDEF"
                    case 0xFF00:
                        current["Index"] = "LORESERVE"
                    case 0xFF1F:
                        current["Index"] = "HIPROC"
                    case 0xFFF1:
                        current["Index"] = "ABS"
                    case 0xFFF2:
                        current["Index"] = "COMMON"
                    case 0xFFFF:
                        current["Index"] = "HIRESERVE"
                    case _:
                        current["Index"] = entry["st_shndx"]
                if entry["st_name"] > 0:
                    current["Name"] = str(
                        self.get_name(strtab["sh_offset"], entry["st_name"])
                    )[2:-1]
                else:
                    current["Name"] = ""

                table.append(current)

        return commands, table, file_header["e_entry"]


def get_imm(command, t):
    if t == "U":
        return command >> 12
    elif t == "I":
        l = (command >> 20) & ((1 << 13) - 1)
        r = (1 << 19) - 1 if l >> 31 else 0
        return (r << 12) + l
    elif t == "I_shamt":
        return (command >> 20) % 32
    elif t == "S":
        l = (command >> 7) % 32
        c = (command >> 25) % 64
        a = (1 << 20) - 1 if command >> 31 else 0
        return (a << 12) + (c << 5) + l
    elif t == "B":
        command = bin(command)[2:].zfill(32)[::-1]
        return int(
            (
                "0"
                + command[8:12]
                + command[25:30]
                + command[7]
                + command[30]
                + command[31] * 20
            )[::-1],
            2,
        )

    elif t == "J":
        command = bin(command)[2:].zfill(32)[::-1]
        return int(
            ("0" + command[21:31] + command[20] + command[12:20] + command[31] * 12)[
                ::-1
            ],
            2,
        )


def disassemble(commands, symtab, start):
    ABI_table = {
        0: "zero",
        1: "ra",
        2: "sp",
        3: "gp",
        4: "tp",
        5: "t0",
        6: "t1",
        7: "t2",
        8: "s0",
        9: "s1",
        10: "a0",
        11: "a1",
        12: "a2",
        13: "a3",
        14: "a4",
        15: "a5",
        16: "a6",
        17: "a7",
        18: "s2",
        19: "s3",
        20: "s4",
        21: "s5",
        22: "s6",
        23: "s7",
        24: "s8",
        25: "s9",
        26: "s10",
        27: "s11",
        28: "t3",
        29: "t4",
        30: "t5",
        31: "t6",
    }

    result = []
    idx = start
    L = 0
    marks = dict()
    for symbol in symtab:
        if symbol["Name"] != "":
            marks[symbol["Value"]] = symbol["Name"]

    for command in commands:
        l = len(result)
        b = bin(command)[2:].zfill(32)

        if command == 0b00000000000000000000000001110011:
            result.append("   %05x:\t%08x\t%7s\n" % (idx, command, "ecall"))
            idx += 4
            continue
        elif command == 0b00000000000100000000000001110011:
            result.append("   %05x:\t%08x\t%7s\n" % (idx, command, "ebreak"))
            idx += 4
            continue

        opcode = command % (1 << 7)
        rm = (command >> 12) % 8
        rk = command >> 25

        match opcode:
            case 0b0110111:  # U type
                rd = (command >> 7) % 32
                imm = get_imm(command, "U")
                result.append(
                    "   %05x:\t%08x\t%7s\t%s, 0x%x\n"
                    % (idx, command, "lui", ABI_table[rd], imm)
                )
            case 0b0010111:  # U type
                rd = (command >> 7) % 32
                imm = command >> 12
                imm -= 2 * (imm & (1 << 20))
                result.append(
                    "   %05x:\t%08x\t%7s\t%s, 0x%x\n"
                    % (idx, command, "auipc", ABI_table[rd], imm)
                )
            case 0b1101111:  # J Type
                rd = (command >> 7) % 32
                imm = get_imm(command, "J")
                imm = (imm + idx) & ((1 << 32) - 1)
                name = None
                if marks.get(imm) is not None:
                    name = marks[imm]
                if name is None:
                    name = "L" + str(L)
                    L += 1

                marks[imm] = name
                result.append(
                    "   %05x:\t%08x\t%7s\t%s, 0x%x <%s>\n"
                    % (idx, command, "jal", ABI_table[rd], imm, name)
                )
            case 0b1100111:  # I type
                if rm == 0b000:
                    rd = (command >> 7) % 32
                    rs1 = (command >> 15) % 32
                    imm = command >> 20
                    imm -= 2 * (imm & (1 << 11))

                    result.append(
                        "   %05x:\t%08x\t%7s\t%s, %d(%s)\n"
                        % (idx, command, "jalr", ABI_table[rd], imm, ABI_table[rs1])
                    )
            case 0b1100011:  # B type
                rs1 = (command >> 15) % 32
                rs2 = (command >> 20) % 32
                imm = get_imm(command, "B")
                imm = (idx + imm) & ((1 << 32) - 1)

                res = None
                match rm:
                    case 0b000:
                        res = "beq"
                    case 0b001:
                        res = "bne"
                    case 0b100:
                        res = "blt"
                    case 0b101:
                        res = "bge"
                    case 0b110:
                        res = "bltu"
                    case 0b111:
                        res = "bgeu"
                if res is not None:
                    name = None
                    if marks.get(imm) is not None:
                        name = marks[imm]
                    if name is None:
                        name = "L" + str(L)
                        L += 1

                    marks[imm] = name
                    result.append(
                        "   %05x:\t%08x\t%7s\t%s, %s, 0x%x, <%s>\n"
                        % (idx, command, res, ABI_table[rs1], ABI_table[rs2], imm, name)
                    )

            case 0b0000011:  # I type
                rd = (command >> 7) % 32
                rs1 = (command >> 15) % 32
                imm = command >> 20
                imm -= 2 * (imm & (1 << 11))

                res = None
                match rm:
                    case 0b000:
                        res = "lb"
                    case 0b001:
                        res = "lh"
                    case 0b010:
                        res = "lw"
                    case 0b100:
                        res = "lbu"
                    case 0b101:
                        res = "lhu"

                if res is not None:
                    result.append(
                        "   %05x:\t%08x\t%7s\t%s, %d(%s)\n"
                        % (idx, command, res, ABI_table[rd], imm, ABI_table[rs1])
                    )
            case 0b0100011:  # S type
                rs1 = (command >> 15) % 32
                rs2 = (command >> 20) % 32
                imm = ((command >> 25) << 5) + (command >> 7) % 32
                imm -= 2 * (1 << 11 & imm)

                res = None
                match rm:
                    case 0b000:
                        res = "sb"
                    case 0b001:
                        res = "sh"
                    case 0b010:
                        res = "sw"
                if res is not None:
                    result.append(
                        "   %05x:\t%08x\t%7s\t%s, %d(%s)\n"
                        % (idx, command, res, ABI_table[rs2], imm, ABI_table[rs1])
                    )
            case 0b0010011:  # I type
                rd = (command >> 7) % 32
                rs1 = (command >> 15) % 32
                imm = command >> 20

                res = None

                match rm:
                    case 0b000:
                        res = "addi"
                    case 0b010:
                        res = "slti"
                    case 0b011:
                        res = "sltiu"
                    case 0b100:
                        res = "xori"
                    case 0b110:
                        res = "ori"
                    case 0b111:
                        res = "andi"
                    case 0b001:
                        if rk == 0b0000000:
                            res = "slli"
                    case 0b101:
                        if rk == 0b0000000:
                            res = "srli"
                        elif rk == 0b0100000:
                            res = "srai"

                if res is not None:
                    if res not in ("slli", "srli", "srai"):
                        imm -= 2 * (imm & (1 << 11))
                        result.append(
                            "   %05x:\t%08x\t%7s\t%s, %s, %u\n"
                            % (
                                idx,
                                command,
                                res,
                                ABI_table[rd],
                                ABI_table[rs1],
                                imm,
                            )
                        )
                    else:
                        shamt = imm % 32
                        result.append(
                            "   %05x:\t%08x\t%7s\t%s, %s, %u\n"
                            % (
                                idx,
                                command,
                                res,
                                ABI_table[rd],
                                ABI_table[rs1],
                                shamt,
                            )
                        )
            case 0b0110011:
                if command >> 25 == 1:
                    rd = (command >> 7) % 32
                    rs1 = (command >> 15) % 32
                    rs2 = (command >> 20) % 32
                    res = None
                    match rm:
                        case 0b000:
                            res = "mul"
                        case 0b001:
                            res = "mulh"
                        case 0b010:
                            res = "mulhsu"
                        case 0b011:
                            res = "mulhu"
                        case 0b100:
                            res = "div"
                        case 0b101:
                            res = "divu"
                        case 0b110:
                            res = "rem"
                        case 0b111:
                            res = "remu"
                    if res is not None:
                        result.append(
                            "   %05x:\t%08x\t%7s\t%s, %s, %s\n"
                            % (
                                idx,
                                command,
                                res,
                                ABI_table[rd],
                                ABI_table[rs1],
                                ABI_table[rs2],
                            )
                        )
                    idx += 4
                    continue
                rd = (command >> 7) % 32
                rs1 = (command >> 15) % 32
                rs2 = (command >> 20) % 32
                res = None
                if rm == 0b000 and rk == 0b0000000:
                    res = "add"
                elif rm == 0b000 and rk == 0b0100000:
                    res = "sub"
                elif rm == 0b001 and rk == 0b0000000:
                    res = "sll"
                elif rm == 0b010 and rk == 0b0000000:
                    res = "slt"
                elif rm == 0b011 and rk == 0b0000000:
                    res = "sltu"
                elif rm == 0b100 and rk == 0b0000000:
                    res = "xor"
                elif rm == 0b101 and rk == 0b0000000:
                    res = "srl"
                elif rm == 0b101 and rk == 0b0100000:
                    res = "sra"
                elif rm == 0b110 and rk == 0b0000000:
                    res = "or"
                elif rm == 0b111 and rk == 0b0000000:
                    res = "and"
                if res is not None:
                    result.append(
                        "   %05x:\t%08x\t%7s\t%s, %s, %s\n"
                        % (
                            idx,
                            command,
                            res,
                            ABI_table[rd],
                            ABI_table[rs1],
                            ABI_table[rs2],
                        )
                    )
            case 0b1110011:
                csr = command >> 20
                rs1 = (command >> 15) % 32
                rd = (command >> 7) % 32

                res = None

                match rm:
                    case 0b001:
                        res = "csrrw"
                    case 0b010:
                        res = "csrrs"
                    case 0b011:
                        res = "csrrc"
                    case 0b101:
                        res = "csrrwi"
                    case 0b110:
                        res = "csrrsi"
                    case 0b111:
                        res = "csrrci"

                if res is not None:
                    if res in ("csrrw", "csrrs", "csrrc"):
                        result.append(
                            "   %05x:\t%08x\t%7s\t%s,%s,%s\n"
                            % (idx, command, res, ABI_table[rd], csr, ABI_table[rs1])
                        )
                    else:
                        result.append(
                            "   %05x:\t%08x\t%7s\t%s,%s,%s\n"
                            % (idx, command, res, ABI_table[rd], csr, rs1)
                        )
            case 0b0001111:
                if rm == 0b000:
                    rd = (command >> 7) % 32
                    rs1 = (command >> 15) % 32
                    succ = (command >> 20) % 16
                    pred = (command >> 24) % 16
                    fm = (command >> 28) % 16
                    result.append(
                        "   %05x:\t%08x\t%7s\t%s, %s\n"
                        % (idx, command, "fence", "iorw", "iorw")
                    )

        if len(result) != l + 1:
            result.append(
                "   %05x:\t%08x\t%7s %s\n"
                % (idx, command, "invalid instruction", bin(opcode))
            )
        idx += 4
    return result, marks


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write(
            f"Wrong argument count.\n"
            f"\tExpected: 2\n"
            f"\tActual: {len(sys.argv) - 1}"
        )
        exit(1)
    if not os.path.exists(sys.argv[1]):
        sys.stderr.write(f"Elf file does not exist: {sys.argv[1]}")
        exit(2)

    TEST_DATA = sys.argv[1]
    OUTPUT_DATA = sys.argv[2]

    sys.stdout = open(OUTPUT_DATA, "w")

    parser = ElfParser()
    commands, table, entry = parser.parse_elf(TEST_DATA)

    res, marks = disassemble(commands, table, int("10074", 16))

    print(".text")
    idx = int("10074", 16)
    for i in res:
        if marks.get(idx) is not None:
            print("\n%08x \t<%s>:" % (idx, marks[idx]))
        print(i, end="")
        idx += 4

    print("\n.symtab")
    printf("\nSymbol Value              Size Type     Bind     Vis       Index Name\n")
    for i, var in enumerate(table):
        printf("[%4i] 0x%-15X %5i %-8s %-8s %-8s %6s %s\n", i, *list(var.values()))
