"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        self.input_lines_array = input_file.read().splitlines()
        self.current_line = 0
        self.current_instruction = None
        self.current_instruction_num = -1  # counting only A and C instructions

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        # checking that line is command
        while self.current_line < len(self.input_lines_array):
            line = self.input_lines_array[self.current_line].replace(" ", "").replace("\t",
                                                                                      "")  # line has no whitespaces
            if line.startswith("//") is True:
                self.current_line += 1
                continue
            if line == "":
                self.current_line += 1
                continue
            self.current_instruction_num += 1
            return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        # Your code goes here!
        instruction = self.input_lines_array[self.current_line]
        # removing comments from the end of instruction:
        if "//" in instruction:
            idx = instruction.index("//")
            instruction = instruction[:idx]
        # removing whitespaces
        self.current_instruction = instruction.replace(" ", "").replace("\t", "")
        self.current_line += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        # Your code goes here!
        if self.current_instruction.startswith("@") is True:
            return "A_COMMAND"
        if self.current_instruction.startswith("(") is True:
            return "L_COMMAND"
        return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        # Your code goes here!
        if self.current_instruction.startswith("@") is True:
            # removing "@"
            return self.current_instruction[1:]
        # removing "(" and ")"
        return self.current_instruction[1:-1]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        if "=" not in self.current_instruction:
            return "null"
        idx = self.current_instruction.index("=")
        return self.current_instruction[:idx]

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        ret = self.current_instruction
        if ";" in ret:
            idx_jmp = ret.index(";")
            ret = ret[:idx_jmp]
        if "=" in ret:
            idx_dest = ret.index("=")
            ret = ret[idx_dest + 1:]
        return ret

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        if ";" not in self.current_instruction:
            return "null"
        idx = self.current_instruction.index(";")
        return self.current_instruction[idx + 1:]
