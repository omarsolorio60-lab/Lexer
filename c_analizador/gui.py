import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from lexer import LexicalAnalyzer
from parser import SyntaxAnalyzer, SyntaxError
from token_types import TokenType
from ast_printer import obtener_ast_como_texto

class AnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Léxico y Sintáctico de C")
        self.root.geometry("1200x750")

        self.lexer = LexicalAnalyzer()

        self._build_ui()

    def _build_ui(self):
        # Frame superior de botones
        top_frame = tk.Frame(self.root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)

        btn_open = tk.Button(top_frame, text="Abrir .c", command=self.open_file, width=15)
        btn_open.pack(side=tk.LEFT, padx=5)

        btn_lex = tk.Button(top_frame, text="Analizar Tokens", command=self.run_lexer, width=15)
        btn_lex.pack(side=tk.LEFT, padx=5)

        btn_parse = tk.Button(top_frame, text="Analizar AST", command=self.run_parser, width=15)
        btn_parse.pack(side=tk.LEFT, padx=5)

        btn_clear = tk.Button(top_frame, text="Limpiar", command=self.clear_all, width=15)
        btn_clear.pack(side=tk.LEFT, padx=5)

        # Panel principal dividido en izquierda y derecha
        main_frame = tk.Frame(self.root, padx=10, pady=5)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Editor de código
        code_label = tk.Label(left_frame, text="Código fuente C")
        code_label.pack(anchor="w")

        self.code_text = scrolledtext.ScrolledText(left_frame, wrap=tk.NONE, font=("Courier New", 11))
        self.code_text.pack(fill=tk.BOTH, expand=True)

        # Salida de tokens
        tokens_label = tk.Label(right_frame, text="Tokens")
        tokens_label.pack(anchor="w")

        self.tokens_text = scrolledtext.ScrolledText(right_frame, height=18, wrap=tk.NONE, font=("Courier New", 10))
        self.tokens_text.pack(fill=tk.BOTH, expand=True)

        # Salida de AST / errores
        ast_label = tk.Label(right_frame, text="AST / Mensajes")
        ast_label.pack(anchor="w", pady=(10, 0))

        self.ast_text = scrolledtext.ScrolledText(right_frame, height=18, wrap=tk.NONE, font=("Courier New", 10))
        self.ast_text.pack(fill=tk.BOTH, expand=True)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Selecciona un archivo C",
            filetypes=[("Archivos C", "*.c"), ("Todos los archivos", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.code_text.delete("1.0", tk.END)
            self.code_text.insert(tk.END, content)

            self.tokens_text.delete("1.0", tk.END)
            self.ast_text.delete("1.0", tk.END)

        except Exception as e:
            messagebox.showerror("Error al abrir archivo", str(e))

    def get_code(self):
        return self.code_text.get("1.0", tk.END)

    def run_lexer(self):
        code = self.get_code().strip()

        if not code:
            messagebox.showwarning("Sin código", "No hay código para analizar.")
            return

        try:
            tokens = self.lexer.tokenize(code)

            self.tokens_text.delete("1.0", tk.END)
            self.ast_text.delete("1.0", tk.END)

            for token in tokens:
                if token.type not in {TokenType.WHITESPACE, TokenType.NEWLINE}:
                    self.tokens_text.insert(tk.END, str(token) + "\n")

            self.ast_text.insert(tk.END, "Análisis léxico completado.\n")

        except Exception as e:
            self.ast_text.delete("1.0", tk.END)
            self.ast_text.insert(tk.END, f"Error léxico:\n{e}")

    def run_parser(self):
        code = self.get_code().strip()

        if not code:
            messagebox.showwarning("Sin código", "No hay código para analizar.")
            return

        try:
            tokens = self.lexer.tokenize(code)
            parser = SyntaxAnalyzer(tokens)
            ast = parser.parse()

            self.tokens_text.delete("1.0", tk.END)
            self.ast_text.delete("1.0", tk.END)

            for token in tokens:
                if token.type not in {TokenType.WHITESPACE, TokenType.NEWLINE}:
                    self.tokens_text.insert(tk.END, str(token) + "\n")

            self.ast_text.insert(tk.END, obtener_ast_como_texto(ast))

        except SyntaxError as e:
            self.ast_text.delete("1.0", tk.END)
            self.ast_text.insert(tk.END, str(e))

        except Exception as e:
            self.ast_text.delete("1.0", tk.END)
            self.ast_text.insert(tk.END, f"Error inesperado:\n{e}")

    def clear_all(self):
        self.code_text.delete("1.0", tk.END)
        self.tokens_text.delete("1.0", tk.END)
        self.ast_text.delete("1.0", tk.END)


def main():
    root = tk.Tk()
    app = AnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()