"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


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
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.tabs = ""

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        if self.input_stream.current_token is None:
            self.input_stream.advance()
        self.open_scope("class")

        # 'class' className '{'
        for i in range(3):
            self.write_output_and_advance_input()

        # classVarDec* subroutineDec*
        while self.input_stream.current_token in ["static", "field"]:
            self.compile_class_var_dec()
        while self.input_stream.current_token in ["constructor", "function", "method"]:
            self.compile_subroutine()

        # '}'
        self.write_output_and_advance_input()

        self.close_scope("class")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        self.open_scope("classVarDec")

        # ('static'|'field') type varName
        for i in range(3):
            self.write_output_and_advance_input()

        # (',' varname)*
        while self.input_stream.current_token != ";":
            self.write_output_and_advance_input()
            self.write_output_and_advance_input()

        # ';'
        self.write_output_and_advance_input()

        self.close_scope("classVarDec")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        self.open_scope("subroutineDec")

        # ('constructor'|'function'|'method') ('void'|type) subroutineName '('
        for i in range(4):
            self.write_output_and_advance_input()

        # parameterList
        self.compile_parameter_list()

        # ')'
        self.write_output_and_advance_input()

        # subroutineBody
        self.open_scope("subroutineBody")

        # '{'
        self.write_output_and_advance_input()

        # varDec*
        while self.input_stream.current_token not in ["let", "if", "while", "do", "return"]:
            self.compile_var_dec()

        # statements
        while self.input_stream.current_token in ["let", "if", "while", "do", "return"]:
            self.compile_statements()

        # '}'
        self.write_output_and_advance_input()

        self.close_scope("subroutineBody")

        self.close_scope("subroutineDec")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
        self.open_scope("parameterList")

        # ((type varName) (',' type varName)*)?
        while self.input_stream.current_token != ")":
            self.write_output_and_advance_input()

        self.close_scope("parameterList")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        self.open_scope("varDec")

        # var type varName
        for i in range(3):
            self.write_output_and_advance_input()

        # (',' varName)*
        while self.input_stream.current_token != ";":
            for i in range(2):
                self.write_output_and_advance_input()

        # ';'
        self.write_output_and_advance_input()

        self.close_scope("varDec")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        self.open_scope("statements")

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

        self.close_scope("statements")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        self.open_scope("doStatement")

        # 'do'
        self.write_output_and_advance_input()

        # subroutineCall
        # subroutineName | (className|varName).subroutineName
        while self.input_stream.current_token != "(":
            self.write_output_and_advance_input()

        # '(' expressionList ')'
        self.write_output_and_advance_input()
        self.compile_expression_list()
        self.write_output_and_advance_input()

        # ';'
        self.write_output_and_advance_input()

        self.close_scope("doStatement")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        self.open_scope("letStatement")

        # 'let' varName
        for i in range(2):
            self.write_output_and_advance_input()

        # ('['expression']')?
        if self.input_stream.current_token == "[":
            self.write_output_and_advance_input()
            self.compile_expression()
            self.write_output_and_advance_input()

        # '=' expression ';'
        self.write_output_and_advance_input()
        self.compile_expression()
        self.write_output_and_advance_input()

        self.close_scope("letStatement")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        self.open_scope("whileStatement")

        # 'while' '(' expression
        for i in range(2):
            self.write_output_and_advance_input()
        self.compile_expression()

        # ')' '{' statements '}'
        for i in range(2):
            self.write_output_and_advance_input()
        self.compile_statements()
        self.write_output_and_advance_input()

        self.close_scope("whileStatement")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        self.open_scope("returnStatement")

        # 'return' expression? ';'
        self.write_output_and_advance_input()
        if self.input_stream.current_token != ";":
            self.compile_expression()
        self.write_output_and_advance_input()

        self.close_scope("returnStatement")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        self.open_scope("ifStatement")

        # if '(' expression
        for i in range(2):
            self.write_output_and_advance_input()
        self.compile_expression()

        # ')' '{' statements '}'
        for i in range(2):
            self.write_output_and_advance_input()
        self.compile_statements()
        self.write_output_and_advance_input()

        # ('else' '{' statements '}')?
        if self.input_stream.current_token == "else":
            for i in range(2):
                self.write_output_and_advance_input()
            self.compile_statements()
            self.write_output_and_advance_input()

        self.close_scope("ifStatement")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!
        self.open_scope("expression")

        # term
        self.compile_term()

        # (op term)*
        while self.input_stream.current_token in ["+", "-", "*", "/", "&amp;", "|", "&gt;", "&lt;", "="]:
            self.write_output_and_advance_input()
            self.compile_term()

        self.close_scope("expression")

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
        self.open_scope("term")

        if self.input_stream.current_token in ["-", "~", "^", "#"]:
            # unaryOp term
            self.write_output_and_advance_input()
            self.compile_term()

        elif self.input_stream.current_token == "(":
            # '(' expression '')'
            self.write_output_and_advance_input()
            self.compile_expression()
            self.write_output_and_advance_input()

        elif self.input_stream.token_type() == "identifier":
            next_token = self.input_stream.tokens_lst[self.input_stream.current_token_num + 1][0]
            if next_token == "[":
                # '[' expression ']'
                for i in range(2):
                    self.write_output_and_advance_input()
                self.compile_expression()
                self.write_output_and_advance_input()

            elif next_token in [".", "("]:
                # subroutineCall
                # subroutineName | (className|varName).subroutineName
                while self.input_stream.current_token != "(":
                    self.write_output_and_advance_input()

                # '(' expressionList ')'
                self.write_output_and_advance_input()
                self.compile_expression_list()
                self.write_output_and_advance_input()

            else:
                self.write_output_and_advance_input()
        else:
            self.write_output_and_advance_input()

        self.close_scope("term")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        self.open_scope("expressionList")

        if self.input_stream.current_token != ")":
            self.compile_expression()
            while self.input_stream.current_token == ",":
                self.write_output_and_advance_input()
                self.compile_expression()

        self.close_scope("expressionList")

    def write_output_and_advance_input(self) -> None:
        self.output_stream.write(f"{self.tabs}<{self.input_stream.token_type()}> "
                                 f"{self.input_stream.current_token} "
                                 f"</{self.input_stream.token_type()}>\n")
        self.input_stream.advance()

    def open_scope(self, name: str) -> None:
        self.output_stream.write(f"{self.tabs}<{name}>\n")
        self.tabs += "  "  # adding two spaces

    def close_scope(self, name: str) -> None:
        self.tabs = self.tabs[2:]
        self.output_stream.write(f"{self.tabs}</{name}>\n")
