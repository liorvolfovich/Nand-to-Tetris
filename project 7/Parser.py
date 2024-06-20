"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the lines end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        self.input_lines_array = input_file.read().splitlines()
        self.current_line_num = 0
        self.current_instruction = None
        # self.current_instruction_num = -1
        self.arithmetic_set = {"add", "sub", "neg", "and", "or", "not", "shiftleft", "shiftright",
                               "eq", "gt", "lt"}

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        while self.current_line_num < len(self.input_lines_array):
            line = (self.input_lines_array[self.current_line_num]
                    .replace(" ", "").replace("\t", ""))  # line has no whitespaces
            if line.startswith("//") is True:
                self.current_line_num += 1
                continue
            if line == "":
                self.current_line_num += 1
                continue
            # self.current_instruction_num += 1
            return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        # Your code goes here!
        instruction = self.input_lines_array[self.current_line_num]
        # removing comments from the end of instruction:
        if "//" in instruction:
            idx = instruction.index("//")
            instruction = instruction[:idx]
        # removing whitespaces at the beginning and at the end (not between words)
        self.current_instruction = instruction.strip()
        self.current_line_num += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        # Your code goes here!
        if self.current_instruction in self.arithmetic_set:
            return "C_ARITHMETIC"
        elif "push" in self.current_instruction:
            return "C_PUSH"
        elif "pop" in self.current_instruction:
            return "C_POP"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        # Your code goes here!
        command_type = self.command_type()
        if command_type == "C_ARITHMETIC":
            return self.current_instruction
        elif command_type == "C_PUSH" or command_type == "C_POP":
            command_arr = self.current_instruction.split()
            return command_arr[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        # Your code goes here!
        command_type = self.command_type()
        if command_type == "C_PUSH" or command_type == "C_POP":
            command_arr = self.current_instruction.split()
            return int(command_arr[2])
