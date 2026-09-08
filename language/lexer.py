# ============================================================
# VIREO LEXER
# Токенізатор Vireo коду
# ============================================================

from enum import Enum
from typing import List, Optional, Any
from dataclasses import dataclass


class TokenType(Enum):
    """Типи токенів Vireo."""
    # Ключові слова
    IMPORT = "IMPORT"
    LET = "LET"
    FN = "FN"
    RETURN = "RETURN"
    PRINT = "PRINT"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
    IN = "IN"
    TRUE = "TRUE"
    FALSE = "FALSE"
    NONE = "NONE"
    
    # ML/Агенти
    MODEL = "MODEL"
    AGENT = "AGENT"
    CONTRACT = "CONTRACT"
    NEGOTIATION = "NEGOTIATION"
    LAYER = "LAYER"
    ACTIVATION = "ACTIVATION"
    LOSS = "LOSS"
    OPTIMIZER = "OPTIMIZER"
    TRAIN = "TRAIN"
    PREDICT = "PREDICT"
    EVALUATE = "EVALUATE"
    IDENTITY = "IDENTITY"
    CAPABILITY = "CAPABILITY"
    ROLE = "ROLE"
    
    # Протокол
    PROPOSE = "PROPOSE"
    COMMIT = "COMMIT"
    REJECT = "REJECT"
    EXECUTE = "EXECUTE"
    VERIFY = "VERIFY"
    ESCALATE = "ESCALATE"
    INFORM = "INFORM"
    DONE = "DONE"
    PARTY = "PARTY"
    TIMEOUT = "TIMEOUT"
    MAX_ROUNDS = "MAX_ROUNDS"
    ON = "ON"
    OFFER = "OFFER"
    ACCEPT = "ACCEPT"
    CONDITION = "CONDITION"
    INVARIANT = "INVARIANT"
    VERIFY_BLOCK = "VERIFY_BLOCK"
    ALLOWED_ACTIONS = "ALLOWED_ACTIONS"
    
    # Безпека
    SECURITY = "SECURITY"
    ENCRYPT = "ENCRYPT"
    DECRYPT = "DECRYPT"
    SIGN = "SIGN"
    
    # Літерали
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    DID = "DID"
    
    # Оператори
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    MOD = "MOD"
    POW = "POW"
    ASSIGN = "ASSIGN"
    EQ = "EQ"
    NE = "NE"
    LT = "LT"
    GT = "GT"
    LE = "LE"
    GE = "GE"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    DOT = "DOT"
    ARROW = "ARROW"
    
    # Розділювачі
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COLON = "COLON"
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    
    # Коментарі
    COMMENT = "COMMENT"
    
    # Спеціальні
    EOF = "EOF"
    ERROR = "ERROR"


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int
    
    def __repr__(self) -> str:
        return f"Token({self.type.value}, '{self.value}', {self.line}:{self.column})"


class Lexer:
    """Лексер Vireo мови."""
    
    KEYWORDS = {
        'import': TokenType.IMPORT,
        'let': TokenType.LET,
        'fn': TokenType.FN,
        'return': TokenType.RETURN,
        'print': TokenType.PRINT,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'in': TokenType.IN,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'none': TokenType.NONE,
        'model': TokenType.MODEL,
        'agent': TokenType.AGENT,
        'contract': TokenType.CONTRACT,
        'negotiation': TokenType.NEGOTIATION,
        'layer': TokenType.LAYER,
        'activation': TokenType.ACTIVATION,
        'loss': TokenType.LOSS,
        'optimizer': TokenType.OPTIMIZER,
        'train': TokenType.TRAIN,
        'predict': TokenType.PREDICT,
        'evaluate': TokenType.EVALUATE,
        'identity': TokenType.IDENTITY,
        'capability': TokenType.CAPABILITY,
        'role': TokenType.ROLE,
        'propose': TokenType.PROPOSE,
        'commit': TokenType.COMMIT,
        'reject': TokenType.REJECT,
        'execute': TokenType.EXECUTE,
        'verify': TokenType.VERIFY,
        'escalate': TokenType.ESCALATE,
        'inform': TokenType.INFORM,
        'done': TokenType.DONE,
        'party': TokenType.PARTY,
        'timeout': TokenType.TIMEOUT,
        'max_rounds': TokenType.MAX_ROUNDS,
        'on': TokenType.ON,
        'offer': TokenType.OFFER,
        'accept': TokenType.ACCEPT,
        'condition': TokenType.CONDITION,
        'invariant': TokenType.INVARIANT,
        'verify_block': TokenType.VERIFY_BLOCK,
        'allowed_actions': TokenType.ALLOWED_ACTIONS,
        'security': TokenType.SECURITY,
        'encrypt': TokenType.ENCRYPT,
        'decrypt': TokenType.DECRYPT,
        'sign': TokenType.SIGN,
    }
    
    OPERATORS = {
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '*': TokenType.STAR,
        '/': TokenType.SLASH,
        '%': TokenType.MOD,
        '**': TokenType.POW,
        '=': TokenType.ASSIGN,
        '==': TokenType.EQ,
        '!=': TokenType.NE,
        '<': TokenType.LT,
        '>': TokenType.GT,
        '<=': TokenType.LE,
        '>=': TokenType.GE,
        '&&': TokenType.AND,
        '||': TokenType.OR,
        '!': TokenType.NOT,
        '.': TokenType.DOT,
        '->': TokenType.ARROW,
    }
    
    DELIMITERS = {
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        '{': TokenType.LBRACE,
        '}': TokenType.RBRACE,
        '[': TokenType.LBRACKET,
        ']': TokenType.RBRACKET,
        ':': TokenType.COLON,
        ';': TokenType.SEMICOLON,
        ',': TokenType.COMMA,
    }
    
    def __init__(self):
        self.code: str = ""
        self.pos: int = 0
        self.line: int = 1
        self.column: int = 1
        self.tokens: List[Token] = []
        self.current_char: Optional[str] = None
    
    def tokenize(self, code: str) -> List[Token]:
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self._advance()
        
        while self.current_char is not None:
            if self.current_char.isspace():
                self._skip_whitespace()
            elif self.current_char == '/':
                self._handle_comment()
            elif self.current_char == '"' or self.current_char == "'":
                self._read_string()
            elif self.current_char.isdigit() or (self.current_char == '-' and self._peek().isdigit()):
                self._read_number()
            elif self.current_char.isalpha() or self.current_char == '_':
                self._read_identifier()
            elif self.current_char in self.OPERATORS:
                self._read_operator()
            elif self.current_char in self.DELIMITERS:
                self._read_delimiter()
            else:
                self._add_token(TokenType.ERROR, self.current_char)
                self._advance()
        
        self._add_token(TokenType.EOF, None)
        return self.tokens
    
    def _advance(self) -> None:
        if self.pos >= len(self.code):
            self.current_char = None
            return
        self.current_char = self.code[self.pos]
        self.pos += 1
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
    
    def _peek(self, offset: int = 0) -> Optional[str]:
        pos = self.pos + offset
        if pos >= len(self.code):
            return None
        return self.code[pos]
    
    def _skip_whitespace(self) -> None:
        while self.current_char is not None and self.current_char.isspace():
            self._advance()
    
    def _handle_comment(self) -> None:
        if self._peek() == '/':
            self._advance()
            self._advance()
            comment = ""
            while self.current_char is not None and self.current_char != '\n':
                comment += self.current_char
                self._advance()
            self._add_token(TokenType.COMMENT, comment.strip())
        elif self._peek() == '*':
            self._advance()
            self._advance()
            comment = ""
            while self.current_char is not None:
                if self.current_char == '*' and self._peek() == '/':
                    self._advance()
                    self._advance()
                    break
                comment += self.current_char
                self._advance()
            self._add_token(TokenType.COMMENT, comment.strip())
        else:
            self._add_token(TokenType.SLASH, '/')
            self._advance()
    
    def _read_string(self) -> None:
        quote = self.current_char
        self._advance()
        string = ""
        while self.current_char is not None and self.current_char != quote:
            if self.current_char == '\\':
                self._advance()
                if self.current_char == 'n':
                    string += '\n'
                elif self.current_char == 't':
                    string += '\t'
                elif self.current_char == '"':
                    string += '"'
                elif self.current_char == "'":
                    string += "'"
                elif self.current_char == '\\':
                    string += '\\'
                else:
                    string += self.current_char
                self._advance()
            else:
                string += self.current_char
                self._advance()
        if self.current_char == quote:
            self._advance()
        self._add_token(TokenType.STRING, string)
    
    def _read_number(self) -> None:
        number = ""
        is_float = False
        if self.current_char == '-':
            number += '-'
            self._advance()
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                is_float = True
            number += self.current_char
            self._advance()
        if is_float:
            self._add_token(TokenType.FLOAT, float(number))
        else:
            self._add_token(TokenType.NUMBER, int(number))
    
    def _read_identifier(self) -> None:
        identifier = ""
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            identifier += self.current_char
            self._advance()
        if identifier == 'did' and self.current_char == ':':
            self._read_did(identifier)
            return
        token_type = self.KEYWORDS.get(identifier.lower())
        if token_type:
            self._add_token(token_type, identifier)
        else:
            self._add_token(TokenType.IDENTIFIER, identifier)
    
    def _read_did(self, prefix: str) -> None:
        did = prefix
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char in ':-_'):
            did += self.current_char
            self._advance()
        self._add_token(TokenType.DID, did)
    
    def _read_operator(self) -> None:
        two_char = self.current_char + (self._peek() or '')
        if two_char in self.OPERATORS:
            self._add_token(self.OPERATORS[two_char], two_char)
            self._advance()
            self._advance()
            return
        if self.current_char in self.OPERATORS:
            self._add_token(self.OPERATORS[self.current_char], self.current_char)
            self._advance()
    
    def _read_delimiter(self) -> None:
        if self.current_char in self.DELIMITERS:
            self._add_token(self.DELIMITERS[self.current_char], self.current_char)
            self._advance()
    
    def _add_token(self, token_type: TokenType, value: Any) -> None:
        self.tokens.append(Token(token_type, value, self.line, self.column))
    
    def get_tokens(self) -> List[Token]:
        return self.tokens


def tokenize(code: str) -> List[Token]:
    lexer = Lexer()
    return lexer.tokenize(code)