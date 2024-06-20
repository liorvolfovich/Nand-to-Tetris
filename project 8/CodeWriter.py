"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.os = output_stream
        self.label_idx = 1
        self.filename = None
        self.funcname = ""
        self.ret_idx = 1
        self.segments_dict = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.filename = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        # Your code goes here!

        # writing the command in the output file with "//"
        self.os.write("// " + command + "\n")
        if command == "add":
            self.binary_operation("D+M")
        elif command == "sub":
            self.binary_operation("M-D")
        elif command == "neg":
            self.unary_operation("-M")
        elif command == "and":
            self.binary_operation("D&M")
        elif command == "or":
            self.binary_operation("D|M")
        elif command == "not":
            self.unary_operation("!M")
        elif command == "shiftleft":
            self.unary_operation("M<<")
        elif command == "shiftright":
            self.unary_operation("M>>")
        elif command == "eq":
            self.eq_operation()
        elif command == "gt":
            self.gt_lt_operation("JGT")
        elif command == "lt":
            self.gt_lt_operation("JLT")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.

        # writing the command in the output file with "//"
        self.os.write("// " + command + " " + segment + " " + str(index) + "\n")
        if segment == "constant":
            # only push is possible
            self.push_const(index)
        elif segment in self.segments_dict:
            if command == "push":
                self.push_segment_i(self.segments_dict.get(segment), str(index))
            elif command == "pop":
                self.pop_segment_i(self.segments_dict.get(segment), str(index))
        elif segment == "temp":
            if command == "push":
                self.push_segment_i("5", str(index))
            elif command == "pop":
                self.pop_segment_i("5", str(index))
        elif segment == "pointer":
            if command == "push":
                self.push_pointer(str(index))
            elif command == "pop":
                self.pop_pointer(str(index))
        elif segment == "static":
            if command == "push":
                self.push_static(str(index))
            elif command == "pop":
                self.pop_static(str(index))

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command.
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        self.os.write("// label " + label + "\n")
        self.os.write("(" + self.funcname + "$" + label + ")" + "\n")

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        self.os.write("// goto " + label + "\n")
        self.os.write("@" + self.funcname + "$" + label + "\n")
        self.os.write("0;JMP" + "\n")

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command.

        Args:
            label (str): the label to go to.
        """
        self.os.write("// if-goto " + label + "\n")
        self.decrement_SP()
        self.os.write("A=M" + "\n")
        self.os.write("D=M" + "\n")
        self.os.write("@" + self.funcname + "$" + label + "\n")
        self.os.write("D;JNE" + "\n")

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command.
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self.os.write("// function " + function_name + " " + str(n_vars) + "\n")
        self.os.write("(" + function_name + ")" + "\n")
        for i in range(n_vars):
            self.push_const(0)
        self.funcname = function_name

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command.
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code

        self.os.write("// call " + function_name + " " + str(n_args) + "\n")

        # push return_address
        return_address = self.filename + "." + function_name + "$ret." + str(self.ret_idx)
        self.os.write("@" + return_address + "\n")
        self.os.write("D=A" + "\n")
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=D" + "\n")
        self.increment_SP()
        self.ret_idx += 1

        # push LCL, ARG, THIS, THAT
        for seg in self.segments_dict:
            self.os.write("@" + self.segments_dict[seg] + "\n")
            self.os.write("D=M" + "\n")
            self.os.write("@SP" + "\n")
            self.os.write("A=M" + "\n")
            self.os.write("M=D" + "\n")
            self.increment_SP()

        # ARG = SP-5-n_args
        self.os.write("@SP" + "\n")
        self.os.write("D=M" + "\n")
        self.os.write("@5" + "\n")
        self.os.write("D=D-A" + "\n")
        self.os.write("@" + str(n_args) + "\n")
        self.os.write("D=D-A" + "\n")
        self.os.write("@ARG" + "\n")
        self.os.write("M=D" + "\n")

        # LCL = SP
        self.os.write("@SP" + "\n")
        self.os.write("D=M" + "\n")
        self.os.write("@LCL" + "\n")
        self.os.write("M=D" + "\n")

        # goto function_name
        self.os.write("@" + function_name + "\n")
        self.os.write("0;JMP" + "\n")
        # self.write_goto(function_name)

        # (return_adress)
        self.os.write("(" + return_address + ")" + "\n")

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address

        self.os.write("// return" + "\n")

        # frame = LCL. frame will be stored at R13
        self.os.write("@LCL" + "\n")
        self.os.write("D=M" + "\n")
        self.os.write("@R13" + "\n")
        self.os.write("M=D" + "\n")

        # return_address = *(frame-5). return_address will be stored at R14
        self.os.write("D=M" + "\n")
        self.os.write("@5" + "\n")
        self.os.write("D=D-A" + "\n")
        self.os.write("A=D" + "\n")
        self.os.write("D=M" + "\n")
        self.os.write("@R14" + "\n")
        self.os.write("M=D" + "\n")

        # *ARG = pop()
        self.decrement_SP()
        self.os.write("A=M" + "\n")
        self.os.write("D=M" + "\n")
        self.os.write("@ARG" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=D" + "\n")

        # SP = ARG + 1
        self.os.write("@ARG" + "\n")
        self.os.write("D=M+1" + "\n")
        self.os.write("@SP" + "\n")
        self.os.write("M=D" + "\n")

        # LCL = *(frame-4)
        # ARG = *(frame-3)
        # THIS = *(frame-2)
        # THAT = *(frame-1)
        count = 4
        for seg in self.segments_dict:
            self.os.write("@R13" + "\n")
            self.os.write("D=M" + "\n")
            self.os.write("@" + str(count) + "\n")
            self.os.write("D=D-A" + "\n")
            self.os.write("A=D" + "\n")
            self.os.write("D=M" + "\n")
            self.os.write("@" + self.segments_dict[seg] + "\n")
            self.os.write("M=D" + "\n")
            count -= 1

        # goto return_address
        self.os.write("@R14" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("0;JMP" + "\n")

    # helper functions:

    def bootstrap_func(self) -> None:
        # sp = 256
        self.os.write("@256" + "\n")
        self.os.write("D=A" + "\n")
        self.os.write("@SP" + "\n")
        self.os.write("M=D" + "\n")

        # call sys.init
        self.write_call("Sys.init", 0)

    def decrement_SP(self) -> None:
        self.os.write("@SP" + "\n")
        self.os.write("M=M-1" + "\n")

    def increment_SP(self) -> None:
        self.os.write("@SP" + "\n")
        self.os.write("M=M+1" + "\n")

    def push_const(self, index: int) -> None:
        # D=index
        self.os.write("@" + str(index) + "\n")
        self.os.write("D=A" + "\n")

        # *SP=D
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=D" + "\n")

        # SP++
        self.increment_SP()

    def binary_operation(self, binary_str) -> None:
        # SP--
        self.decrement_SP()

        # D = *SP
        self.os.write("A=M" + "\n")
        self.os.write("D=M" + "\n")

        # case add: *SP-1 = *SP-1 + D
        # case sub: *SP-1 = *SP-1 - D
        # case and: *SP-1 = *SP-1 & D
        # case or: *SP-1 = *SP-1 | D
        self.os.write("@SP" + "\n")
        self.os.write("A=M-1" + "\n")
        self.os.write(f"M={binary_str}" + "\n")

    def unary_operation(self, unary_str) -> None:
        # case neg: *SP-1 = -*SP-1
        # case not: *SP-1 = !*SP-1
        # case shiftleft: *SP-1 = *SP-1<<
        # case shiftright: *SP-1 = *SP-1>>
        self.os.write("@SP" + "\n")
        self.os.write("A=M-1" + "\n")
        self.os.write(f"M={unary_str}" + "\n")

    def r13_and_r14(self) -> None:
        # SP--
        self.decrement_SP()

        # D = *SP
        self.os.write("A=M" + "\n")
        self.os.write("D=M" + "\n")

        # if D>0 goto POSITIVE_Y
        self.os.write("@POSITIVE_Y_" + str(self.label_idx) + "\n")
        self.os.write("D;JGT" + "\n")

        # y <= 0, set R14 to zero
        self.os.write("@R14" + "\n")
        self.os.write("M=0" + "\n")
        self.os.write("@X_CHECK_" + str(self.label_idx) + "\n")
        self.os.write("0;JMP" + "\n")

        # y is positive, set R14 to 1
        self.os.write("(POSITIVE_Y_" + str(self.label_idx) + ")" + "\n")
        self.os.write("@R14" + "\n")
        self.os.write("M=1" + "\n")

        # checking sign of x
        self.os.write("(X_CHECK_" + str(self.label_idx) + ")" + "\n")

        # SP--
        self.decrement_SP()

        # D = *SP
        self.os.write("A=M" + "\n")
        self.os.write("D=M" + "\n")

        # if D>0 goto POSITIVE_X
        self.os.write("@POSITIVE_X_" + str(self.label_idx) + "\n")
        self.os.write("D;JGT" + "\n")

        # x <= 0, set R13 to zero
        self.os.write("@R13" + "\n")
        self.os.write("M=0" + "\n")
        self.os.write("@END_SIGN_" + str(self.label_idx) + "\n")
        self.os.write("0;JMP" + "\n")

        # x is positive, set R13 to 1
        self.os.write("(POSITIVE_X_" + str(self.label_idx) + ")" + "\n")
        self.os.write("@R13" + "\n")
        self.os.write("M=1" + "\n")

        self.os.write("(END_SIGN_" + str(self.label_idx) + ")" + "\n")

    def not_same_gt(self) -> None:
        # D = R13-1
        self.os.write("@R13" + "\n")
        self.os.write("D=M-1" + "\n")

        # *SP = -1
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=-1" + "\n")

        # if D = 0 goto IS_GRATER
        self.os.write("@IS_GRATER_" + str(self.label_idx) + "\n")
        self.os.write("D;JEQ" + "\n")

        # x is smaller, *SP=0
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=0" + "\n")

        self.os.write("(IS_GRATER_" + str(self.label_idx) + ")" + "\n")
        self.increment_SP()

        # self.true_label_idx += 1

    def not_same_lt(self) -> None:
        # D = R13-1
        self.os.write("@R13" + "\n")
        self.os.write("D=M-1" + "\n")

        # *SP = 0
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=0" + "\n")

        # if D = 0 goto IS_GRATER
        self.os.write("@IS_GRATER_" + str(self.label_idx) + "\n")
        self.os.write("D;JEQ" + "\n")

        # x is smaller, *SP = -1
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=-1" + "\n")

        self.os.write("(IS_GRATER_" + str(self.label_idx) + ")" + "\n")
        self.increment_SP()

    def gt_lt_operation(self, compare_str) -> None:
        # setting R13 and R14 to represent x and y signs:
        self.r13_and_r14()

        self.os.write("@R13" + "\n")
        self.os.write("D=M" + "\n")
        self.os.write("@R14" + "\n")
        self.os.write("D=D-M" + "\n")
        self.os.write("@SAME_SIGN_" + str(self.label_idx) + "\n")
        self.os.write("D;JEQ" + "\n")

        # X and y are not the same sign
        if compare_str == "JLT":
            self.not_same_lt()
            self.os.write("@END_" + str(self.label_idx) + "\n")
            self.os.write("0;JMP" + "\n")
        elif compare_str == "JGT":
            self.not_same_gt()
            self.os.write("@END_" + str(self.label_idx) + "\n")
            self.os.write("0;JMP" + "\n")

        # in case of same sign, no danger of overflow
        self.os.write("(SAME_SIGN_" + str(self.label_idx) + ")" + "\n")

        # D = x-y (SP now points to x)
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("D=M" + "\n")
        self.os.write("@SP" + "\n")
        self.os.write("A=M+1" + "\n")
        self.os.write("D=D-M" + "\n")

        # *SP = -1
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=-1" + "\n")

        # case gt: if D > 0 goto TRUE_i
        # case lt: if D < 0 goto TRUE_i
        self.os.write("@TRUE_" + str(self.label_idx) + "\n")
        self.os.write(f"D;{compare_str}" + "\n")

        # *SP = 0
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=0" + "\n")

        # (TRUE_i)
        self.os.write("(TRUE_" + str(self.label_idx) + ")" + "\n")
        # sp++
        self.increment_SP()

        self.os.write("(END_" + str(self.label_idx) + ")" + "\n")
        self.label_idx += 1

    def eq_operation(self) -> None:
        # SP--
        self.decrement_SP()

        # D = *SP
        self.os.write("A=M" + "\n")
        self.os.write("D=M" + "\n")

        # SP--
        self.decrement_SP()

        # D = D - *SP
        self.os.write("A=M" + "\n")
        self.os.write("D=M-D" + "\n")

        # *SP = -1
        self.os.write("M=-1" + "\n")

        # case eq: if D == 0 goto TRUE_i
        # case gt: if D > 0 goto TRUE_i
        # case lt: if D < 0 goto TRUE_i
        self.os.write("@TRUE_" + str(self.label_idx) + "\n")
        self.os.write(f"D;JEQ" + "\n")

        # *SP = 0
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=0" + "\n")

        # (TRUE_i)
        self.os.write("(TRUE_" + str(self.label_idx) + ")" + "\n")

        # sp++
        self.increment_SP()

        self.label_idx += 1

    def push_segment_i(self, pointer_name: str, i: str) -> None:
        # D = i
        self.os.write("@" + i + "\n")
        self.os.write("D=A" + "\n")

        # A = pointer_name+i
        self.os.write("@" + pointer_name + "\n")
        if pointer_name == "5":
            self.os.write("A=D+A" + "\n")
        else:
            self.os.write("A=D+M" + "\n")

        # D = *pointer_name+i
        self.os.write("D=M" + "\n")

        # *SP = D
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=D" + "\n")

        # SP++
        self.increment_SP()

    def pop_segment_i(self, pointer_name: str, i: str) -> None:
        # D = i
        self.os.write("@" + i + "\n")
        self.os.write("D=A" + "\n")

        # D = pointer_name+i
        self.os.write("@" + pointer_name + "\n")
        if pointer_name == "5":
            self.os.write("D=D+A" + "\n")
        else:
            self.os.write("D=D+M" + "\n")

        # R13 = D
        self.os.write("@R13" + "\n")
        self.os.write("M=D" + "\n")

        # SP--
        self.decrement_SP()

        # D = *SP
        self.os.write("A=M" + "\n")
        self.os.write("D=M" + "\n")

        # *R13
        self.os.write("@R13" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=D" + "\n")

    def push_pointer(self, i: str) -> None:
        if i == "0":
            pointer_name = "THIS"
        else:
            pointer_name = "THAT"

        # D = pointer_name
        self.os.write("@" + pointer_name + "\n")
        self.os.write("D=M" + "\n")

        # *SP = D
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=D" + "\n")

        # SP++
        self.increment_SP()

    def pop_pointer(self, i: str) -> None:
        if i == "0":
            pointer_name = "THIS"
        else:
            pointer_name = "THAT"

        # SP--
        self.decrement_SP()

        # D = *SP
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("D=M" + "\n")

        # pointer_name = D
        self.os.write("@" + pointer_name + "\n")
        self.os.write("M=D" + "\n")

    def push_static(self, i: str) -> None:
        # D = filename.i
        self.os.write("@" + self.filename + "." + i + "\n")
        self.os.write("D=M" + "\n")

        # *SP = D
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("M=D" + "\n")

        # sp++
        self.increment_SP()

    def pop_static(self, i: str) -> None:
        # SP--
        self.decrement_SP()

        # D = *SP
        self.os.write("@SP" + "\n")
        self.os.write("A=M" + "\n")
        self.os.write("D=M" + "\n")

        # filename.i = D
        self.os.write("@" + self.filename + "." + i + "\n")
        self.os.write("M=D" + "\n")
