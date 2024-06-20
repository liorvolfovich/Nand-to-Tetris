"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # A good place to start is to initialize a new Parser object:
    # Note that you can write to output_file like so:
    # output_file.write("Hello world! \n")

    # initialization
    parser = Parser(input_file)
    symbol_table = SymbolTable()

    # first pass
    while parser.has_more_commands() is True:
        parser.advance()
        type = parser.command_type()
        if type == "L_COMMAND":
            symbol_table.add_entry(parser.symbol(), parser.current_instruction_num)
            parser.current_instruction_num -= 1

    # second pass
    n = 16
    parser.current_line = 0
    parser.current_instruction = None
    parser.current_instruction_num = -1
    while parser.has_more_commands() is True:
        parser.advance()
        type = parser.command_type()
        if type == "A_COMMAND":
            if parser.symbol().isdigit() is True:
                bits = a_instruction(parser.symbol())
                output_file.write(bits + "\n")
            elif symbol_table.contains(parser.symbol()) is True:
                bits = a_instruction(symbol_table.get_address(parser.symbol()))
                output_file.write(bits + "\n")
            else:
                symbol_table.add_entry(parser.symbol(), n)
                bits = a_instruction(str(n))
                output_file.write(bits + "\n")
                n += 1
        elif type == "C_COMMAND":
            dest_bits = Code.dest(parser.dest())
            jump_bits = Code.jump(parser.jump())
            comp_string = parser.comp()
            if ">>" in comp_string or "<<" in comp_string:
                comp_bits = extended_c_instruction(comp_string)
                output_file.write("101" + comp_bits + dest_bits + jump_bits + "\n")
            else:
                comp_bits = Code.comp(comp_string)
                output_file.write("111" + comp_bits + dest_bits + jump_bits + "\n")


def a_instruction(val: str) -> str:
    binary = "0000000000000000"
    if val == "0":
        return binary
    binary_lst = list(binary)
    curr_val = int(val)
    i = 14
    while curr_val > 0:
        if 2 ** i > curr_val:
            i -= 1
            continue
        else:
            binary_lst[15 - i] = "1"
            curr_val -= 2 ** i
            i -= 1
    return ''.join(binary_lst)


def extended_c_instruction(comp: str) -> str:
    extended_c_dict = {"A<<": "0100000", "D<<": "0110000", "M<<": "1100000",
                       "A>>": "0000000", 'D>>': "0010000", "M>>": "1000000"}
    return extended_c_dict[comp]


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
