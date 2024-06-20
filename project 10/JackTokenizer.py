"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the lines end.

    - xxx: quotes are used for tokens that appear verbatim (terminals).
    - xxx: regular typeface is used for names of language constructs 
           (non-terminals).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        self.input_lines_array = input_stream.read().splitlines()
        self.current_line_num = 0
        self.current_token_num = -1
        self.current_token = None
        self.tokens_lst = []
        self.keyword_dict = {"class", "method", "function", "constructor", "int", "boolean",
                             "char", "void", "var", "static", "field", "let", "do", "if",
                             "else", "while", "return", "true", "false", "null", "this"}
        self.symbol_dict = {"{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&",
                            "|", "<", ">", "=", "~", "^", "#"}
        self.create_tokens_lst()

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        if self.current_token_num < len(self.tokens_lst) - 1:
            return True
        return False

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # Your code goes here!
        if self.current_token_num == len(self.tokens_lst) - 1:
            return
        self.current_token_num += 1
        self.current_token = self.tokens_lst[self.current_token_num][0]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        return self.tokens_lst[self.current_token_num][1]

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        return self.current_token

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        # Your code goes here!
        return self.current_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        # Your code goes here!
        return self.current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        # Your code goes here!
        return int(self.current_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        # Your code goes here!
        return self.current_token

    def remove_comments(self) -> None:
        end_of_comment = True
        clean_lines = []

        for line in self.input_lines_array:
            if "//" in line:
                idx = line.index("//")
                line = line[:idx]

            if end_of_comment is False:
                if "*/" in line:
                    comment_end = line.index("*/") + 2
                    line = line[comment_end:]
                    end_of_comment = True
                else:
                    line = ""

            while "/*" in line:
                comment_start = line.index("/*")
                if "*/" in line[comment_start:]:
                    comment_end = line.index("*/", comment_start) + 2
                    line = line[:comment_start] + line[comment_end:]
                else:
                    end_of_comment = False
                    line = line[:comment_start]
                    break

            clean_lines.append(line)
        self.input_lines_array = clean_lines

    def create_tokens_lst(self) -> None:
        self.remove_comments()
        while self.current_line_num < len(self.input_lines_array):
            line = self.input_lines_array[self.current_line_num].strip().replace("\t", " ")
            # line = self.remove_comments(line).replace("\t", " ")
            if line == "":
                self.current_line_num += 1
                continue
            i = 0
            while i < len(line):
                c = line[i]
                if c == " ":
                    i += 1
                    continue
                if c in self.symbol_dict:  # symbol
                    self.symbol_to_tokens_lst(c)
                    i += 1
                    continue
                if c.isdigit():  # int_const
                    i = self.int_to_tokens_lst(line, i)
                    continue
                if c == '"' and line[i + 1] != '"' and '"' in line[i + 1:]:  # string_const
                    i += self.str_to_tokens_lst(line[i + 1:])  # the func returns the length of the string + 2
                    continue
                if c.isalpha() or c == '_':  # identifier or keyword
                    i = self.identifier_or_keyword(line, i)
                    continue
                i += 1  # shouldn't get here by the Jack grammar. avoids entering an infinite loop.
            self.current_line_num += 1

    def symbol_to_tokens_lst(self, c: str) -> None:
        if c == "<":
            curr_token = "&lt;"
        elif c == ">":
            curr_token = "&gt;"
        elif c == "&":
            curr_token = "&amp;"
        else:
            curr_token = c
        self.tokens_lst.append((curr_token, "symbol"))

    def int_to_tokens_lst(self, line: str, j: int) -> int:
        token = line[j]
        j += 1
        while line[j].isdigit():
            token += line[j]
            j += 1
        self.tokens_lst.append((token, "integerConstant"))
        return j

    def str_to_tokens_lst(self, line: str) -> int:
        idx = line.index('"')
        str_token = line[:idx]
        self.tokens_lst.append((str_token, "stringConstant"))
        return len(str_token) + 2

    def identifier_or_keyword(self, line: str, j: int) -> int:
        token = line[j]
        j += 1
        while j < len(line):
            if line[j].isalpha() or line[j].isdigit() or line[j] == '_':
                token += line[j]
                j += 1
            else:
                break
        if token in self.keyword_dict:
            self.tokens_lst.append((token, "keyword"))
        else:
            self.tokens_lst.append((token, "identifier"))
        return j
