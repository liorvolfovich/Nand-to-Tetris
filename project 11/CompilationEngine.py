"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from SymbolTable import SymbolTable
from VMWriter import VMWriter
from JackTokenizer import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        self.input_stream = input_stream
        self.symboltable = SymbolTable()
        self.vm_writer = VMWriter(output_stream)
        self.class_name = None
        self.call_subroutine_args_lst = []
        self.label_counter = 1

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        if self.input_stream.current_token is None:
            self.input_stream.advance()

        # 'class'
        self.input_stream.advance()

        # className '{'
        self.class_name = self.input_stream.current_token
        for i in range(2):
            self.input_stream.advance()

        # classVarDec* subroutineDec*
        while self.input_stream.current_token in ["static", "field"]:
            self.compile_class_var_dec()
        while self.input_stream.current_token in ["constructor", "function", "method"]:
            self.compile_subroutine()

        # '}'
        self.input_stream.advance()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        # ('static'|'field') type varName
        cur_kind = self.input_stream.current_token
        self.input_stream.advance()
        cur_type = self.input_stream.current_token
        self.input_stream.advance()
        cur_name = self.input_stream.current_token
        self.symboltable.define(cur_name, cur_type, cur_kind)
        self.input_stream.advance()

        # (',' varname)*
        while self.input_stream.current_token != ";":
            self.input_stream.advance()
            cur_name = self.input_stream.current_token
            self.symboltable.define(cur_name, cur_type, cur_kind)
            self.input_stream.advance()

        # ';'
        self.input_stream.advance()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        self.symboltable.start_subroutine()

        # ('constructor'|'function'|'method') ('void'|type) subroutineName '('
        subroutine_type = self.input_stream.current_token

        for i in range(2):
            self.input_stream.advance()
        subroutine_name = self.input_stream.current_token
        for i in range(2):
            self.input_stream.advance()

        if subroutine_type == "method":
            self.symboltable.define("this", self.class_name, "argument")

        # parameterList
        self.compile_parameter_list()

        # ')'
        self.input_stream.advance()

        # subroutineBody
        # '{'
        self.input_stream.advance()

        # varDec*
        while self.input_stream.current_token not in ["let", "if", "while", "do", "return"]:
            self.compile_var_dec()

        # method / constructor preparation
        if subroutine_type == "method":
            self.vm_writer.write_function(f"{self.class_name}.{subroutine_name}",
                                          self.symboltable.var_count("var"))
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)

        elif subroutine_type == "constructor":
            self.vm_writer.write_function(f"{self.class_name}.{subroutine_name}",
                                          self.symboltable.var_count("var"))
            self.vm_writer.write_push("constant", self.symboltable.var_count("field"))
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)

        else:
            self.vm_writer.write_function(f"{self.class_name}.{subroutine_name}",
                                          self.symboltable.var_count("var"))

        # statements
        while self.input_stream.current_token in ["let", "if", "while", "do", "return"]:
            self.compile_statements()

        # '}'
        self.input_stream.advance()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        # Your code goes here!
        # ((type varName) (',' type varName)*)?
        if self.input_stream.current_token != ")":
            cur_type = self.input_stream.current_token
            self.input_stream.advance()
            cur_name = self.input_stream.current_token
            self.symboltable.define(cur_name, cur_type, "argument")
            self.input_stream.advance()

        while self.input_stream.current_token != ")":
            self.input_stream.advance()
            cur_type = self.input_stream.current_token
            self.input_stream.advance()
            cur_name = self.input_stream.current_token
            self.symboltable.define(cur_name, cur_type, "argument")
            self.input_stream.advance()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        # var type varName
        self.input_stream.advance()
        cur_type = self.input_stream.current_token
        self.input_stream.advance()
        cur_name = self.input_stream.current_token
        self.symboltable.define(cur_name, cur_type, "var")
        self.input_stream.advance()

        # (',' varName)*
        while self.input_stream.current_token != ";":
            self.input_stream.advance()
            cur_name = self.input_stream.current_token
            self.symboltable.define(cur_name, cur_type, "var")
            self.input_stream.advance()

        # ';'
        self.input_stream.advance()

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        # Your code goes here!

        while self.input_stream.current_token in ["let", "if", "while", "do", "return"]:
            if self.input_stream.current_token == "let":
                self.compile_let()
            elif self.input_stream.current_token == "if":
                self.compile_if()
            elif self.input_stream.current_token == "while":
                self.compile_while()
            elif self.input_stream.current_token == "do":
                self.compile_do()
            else:
                self.compile_return()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!

        # 'do'
        self.input_stream.advance()

        # subroutineCall
        self.subroutine_call()

        # ';'
        self.input_stream.advance()

        self.vm_writer.write_pop("temp", 0)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!

        # 'let' varName
        self.input_stream.advance()
        cur_name = self.input_stream.current_token
        cur_kind = self.symboltable.kind_of(cur_name)
        idx = self.symboltable.index_of(cur_name)
        self.input_stream.advance()

        # ('['expression']')?
        if self.input_stream.current_token == "[":
            self.vm_writer.write_push(cur_kind, idx)
            self.input_stream.advance()
            self.compile_expression()
            self.input_stream.advance()
            self.vm_writer.write_arithmetic("add")
            # '=' expression ';'
            self.input_stream.advance()
            self.compile_expression()
            self.input_stream.advance()

            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)

        else:
            # '=' expression ';'
            self.input_stream.advance()
            self.compile_expression()
            self.input_stream.advance()
            self.vm_writer.write_pop(cur_kind, idx)

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        first_label_name = f"L{self.label_counter}"
        self.label_counter += 1
        second_label_name = f"L{self.label_counter}"
        self.label_counter += 1
        self.vm_writer.write_label(first_label_name)
        # 'while' '(' expression
        for i in range(2):
            self.input_stream.advance()
        self.compile_expression()
        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if(second_label_name)
        # ')' '{' statements '}'
        for i in range(2):
            self.input_stream.advance()
        self.compile_statements()
        self.input_stream.advance()
        self.vm_writer.write_goto(first_label_name)
        self.vm_writer.write_label(second_label_name)

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!

        # 'return' expression? ';'
        self.input_stream.advance()
        if self.input_stream.current_token != ";":
            self.compile_expression()
        else:
            # void function
            self.vm_writer.write_push("constant", 0)
        self.input_stream.advance()
        self.vm_writer.write_return()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!

        # if '(' expression
        for i in range(2):
            self.input_stream.advance()
        self.compile_expression()
        self.vm_writer.write_arithmetic("not")
        first_label_name = f"L{self.label_counter}"
        self.label_counter += 1
        second_label_name = f"L{self.label_counter}"
        self.label_counter += 1
        self.vm_writer.write_if(first_label_name)

        # ')' '{' statements '}'
        for i in range(2):
            self.input_stream.advance()
        self.compile_statements()
        self.input_stream.advance()
        self.vm_writer.write_goto(second_label_name)
        self.vm_writer.write_label(first_label_name)

        # ('else' '{' statements '}')?
        if self.input_stream.current_token == "else":
            for i in range(2):
                self.input_stream.advance()
            self.compile_statements()
            self.input_stream.advance()
        self.vm_writer.write_label(second_label_name)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!

        # term
        self.compile_term()

        # (op term)*
        while self.input_stream.current_token in ["+", "-", "*", "/", "&amp;", "|", "&gt;", "&lt;", "="]:
            op = self.input_stream.current_token
            self.input_stream.advance()
            self.compile_term()
            if op == "+":
                self.vm_writer.write_arithmetic("add")
            elif op == "-":
                self.vm_writer.write_arithmetic("sub")
            elif op == "*":
                self.vm_writer.write_call("Math.multiply", 2)
            elif op == "/":
                self.vm_writer.write_call("Math.divide", 2)
            elif op == "&amp;":
                self.vm_writer.write_arithmetic("and")
            elif op == "|":
                self.vm_writer.write_arithmetic("or")
            elif op == "&gt;":
                self.vm_writer.write_arithmetic("gt")
            elif op == "&lt;":
                self.vm_writer.write_arithmetic("lt")
            elif op == "=":
                self.vm_writer.write_arithmetic("eq")

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        next_token = self.input_stream.tokens_lst[self.input_stream.current_token_num + 1][0]

        # integerConstant
        if self.input_stream.token_type() == "integerConstant":
            self.vm_writer.write_push("constant", int(self.input_stream.current_token))
            self.input_stream.advance()

        # stringConstant
        elif self.input_stream.token_type() == "stringConstant":
            str_name = self.input_stream.current_token
            self.vm_writer.write_push("constant", len(str_name))
            self.vm_writer.write_call("String.new", 1)
            for letter in str_name:
                self.vm_writer.write_push("constant", ord(letter))
                self.vm_writer.write_call("String.appendChar", 2)
            self.input_stream.advance()

        # keywordConstant
        elif self.input_stream.current_token in ["true", "false", "null", "this"]:
            if self.input_stream.current_token == "true":
                self.vm_writer.write_push("constant", 1)
                self.vm_writer.write_arithmetic("neg")
            elif self.input_stream.current_token == "this":
                self.vm_writer.write_push("pointer", 0)
            else:
                self.vm_writer.write_push("constant", 0)
            self.input_stream.advance()

        # subroutineCall
        elif self.input_stream.token_type() == "identifier" and next_token in [".", "("]:
            self.subroutine_call()

        # varName | varName '[' expression ']'
        elif self.symboltable.kind_of(self.input_stream.current_token) is not None:  # should check after subroutineCall
            cur_kind = self.symboltable.kind_of(self.input_stream.current_token)
            cur_idx = self.symboltable.index_of(self.input_stream.current_token)
            self.vm_writer.write_push(cur_kind, cur_idx)
            if next_token != "[":
                self.input_stream.advance()
            else:
                for i in range(2):
                    self.input_stream.advance()
                self.compile_expression()
                self.vm_writer.write_arithmetic("add")
                self.vm_writer.write_pop("pointer", 1)
                self.vm_writer.write_push("that", 0)
                self.input_stream.advance()

        # '(' expression ')'
        elif self.input_stream.current_token == "(":
            self.input_stream.advance()
            self.compile_expression()
            self.input_stream.advance()

        # unaryOp term
        elif self.input_stream.current_token in ["-", "~", "^", "#"]:
            unary_op = self.input_stream.current_token
            self.input_stream.advance()
            self.compile_term()
            if unary_op == "-":
                self.vm_writer.write_arithmetic("neg")
            elif unary_op == "~":
                self.vm_writer.write_arithmetic("not")
            elif unary_op == "^":
                self.vm_writer.write_arithmetic("shiftleft")
            else:
                self.vm_writer.write_arithmetic("shiftright")


    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        self.call_subroutine_args_lst.append(0)
        if self.input_stream.current_token != ")":
            self.call_subroutine_args_lst[-1] += 1
            self.compile_expression()
            while self.input_stream.current_token == ",":
                self.call_subroutine_args_lst[-1] += 1
                self.input_stream.advance()
                self.compile_expression()

    def subroutine_call(self):
        # subroutineName | (className|varName).subroutineName
        next_token = self.input_stream.tokens_lst[self.input_stream.current_token_num + 1][0]
        method_flag = False
        if next_token == ".":
            # (className|varName).subroutineName
            cur_name = self.input_stream.current_token
            cur_kind = self.symboltable.kind_of(cur_name)
            if cur_kind is not None:
                # varName
                method_flag = True
                idx = self.symboltable.index_of(cur_name)
                self.vm_writer.write_push(cur_kind, idx)
                for i in range(2):
                    self.input_stream.advance()
                func_name = f"{self.symboltable.type_of(cur_name)}.{self.input_stream.current_token}"
                self.input_stream.advance()
            else:
                # className
                for i in range(2):
                    self.input_stream.advance()
                func_name = f"{cur_name}.{self.input_stream.current_token}"
                self.input_stream.advance()
        else:
            # subroutineName
            self.vm_writer.write_push("pointer", 0)  # void method
            method_flag = True
            func_name = f"{self.class_name}.{self.input_stream.current_token}"
            self.input_stream.advance()

        # '(' expressionList ')'
        self.input_stream.advance()
        self.compile_expression_list()
        if method_flag:
            # add 1 argument because sending this
            self.call_subroutine_args_lst[-1] += 1
        self.input_stream.advance()

        # call func_name
        self.vm_writer.write_call(func_name, self.call_subroutine_args_lst[-1])
        self.call_subroutine_args_lst.pop()
