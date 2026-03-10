from lexer import LexicalAnalyzer
from parser import SyntaxAnalyzer, SyntaxError
from ast_printer import mostrar_ast


def leer_archivo(ruta: str) -> str:
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


def main():
    ruta = "samples/test.c"
    codigo = leer_archivo(ruta)

    print("=" * 70)
    print("CODIGO FUENTE")
    print("=" * 70)
    print(codigo)

    lexer = LexicalAnalyzer()
    tokens = lexer.tokenize(codigo)

    print("\n" + "=" * 70)
    print("TOKENS")
    print("=" * 70)
    for token in tokens:
        if token.type.value not in ["ESPACIO", "NUEVA_LINEA"]:
            print(token)

    print("\n" + "=" * 70)
    print("ANALISIS SINTACTICO")
    print("=" * 70)

    try:
        parser = SyntaxAnalyzer(tokens)
        ast = parser.parse()
        print("Analisis exitoso")
        print(ast)

        print("\nAST DETALLADO")
        mostrar_ast(ast)

    except SyntaxError as e:
        print(e)
    except Exception as e:
        print(f"Error inesperado: {e}")


if __name__ == "__main__":
    main()