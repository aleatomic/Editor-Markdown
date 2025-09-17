# pip install PyQt6 PyQt6-WebEngine markdown2 
import sys
import markdown2
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTextEdit, QFileDialog, QSplitter, QMenuBar, QMessageBox, QToolBar
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence, QFont

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file_path = None
        self.initUI()

    def initUI(self):
        # Configuración de la ventana principal
        self.setWindowTitle("Editor Markdown estilo StackEdit")
        self.setGeometry(100, 100, 1200, 800)

        # Creación del editor de texto y la vista previa
        self.editor = QTextEdit()
        self.editor.setStyleSheet("font-size: 14pt; font-family: 'Courier New';")

        self.preview = QWebEngineView()
        self.editor.textChanged.connect(self.update_preview)

        # Divisor (Splitter) para organizar los paneles
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)
        splitter.setSizes([600, 600])

        # Creación de la barra de menú y la barra de herramientas
        self.create_menu_bar()
        self.create_tool_bar()

        # Establecer el layout principal
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)
        
        self.setCentralWidget(central_widget)

    def create_menu_bar(self):
        """Crea la barra de menú con las acciones de Archivo."""
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&Archivo")
        
        open_action = QAction("Abrir Archivo", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Guardar", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Guardar Como...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def create_tool_bar(self):
        """Crea la barra de herramientas con acciones de formato Markdown."""
        toolbar = QToolBar("Herramientas de Formato")
        self.addToolBar(toolbar)
        
        # Acciones de formato
        h1_action = QAction("H1", self); h1_action.triggered.connect(lambda: self.apply_style("# ")); toolbar.addAction(h1_action)
        h2_action = QAction("H2", self); h2_action.triggered.connect(lambda: self.apply_style("## ")); toolbar.addAction(h2_action)
        h3_action = QAction("H3", self); h3_action.triggered.connect(lambda: self.apply_style("### ")); toolbar.addAction(h3_action)
        toolbar.addSeparator()

        bold_action = QAction("Bold", self); bold_action.setFont(QFont("Times", weight=QFont.Weight.Bold)); bold_action.triggered.connect(lambda: self.apply_style("**", "**")); toolbar.addAction(bold_action)
        italic_action = QAction("Italic", self); italic_action.setFont(QFont("Times", italic=True)); italic_action.triggered.connect(lambda: self.apply_style("*", "*")); toolbar.addAction(italic_action)
        strike_action = QAction("Tachado", self); font = QFont(); font.setStrikeOut(True); strike_action.setFont(font); strike_action.triggered.connect(lambda: self.apply_style("~~", "~~")); toolbar.addAction(strike_action)
        toolbar.addSeparator()

        list_ul_action = QAction("Lista", self); list_ul_action.triggered.connect(lambda: self.apply_style("\n- ")); toolbar.addAction(list_ul_action)
        list_ol_action = QAction("Lista Num.", self); list_ol_action.triggered.connect(lambda: self.apply_style("\n1. ")); toolbar.addAction(list_ol_action)
        quote_action = QAction("Cita", self); quote_action.triggered.connect(lambda: self.apply_style("\n> ")); toolbar.addAction(quote_action)
        code_action = QAction("Código", self); code_action.triggered.connect(lambda: self.apply_style("```\n", "\n```")); toolbar.addAction(code_action)

        # --- AÑADIDO: Botón para exportar a PDF ---
        toolbar.addSeparator()
        pdf_action = QAction("Exportar PDF", self)
        pdf_action.triggered.connect(self.export_as_pdf)
        toolbar.addAction(pdf_action)


    def apply_style(self, prefix, suffix=None):
        """Aplica formato Markdown al texto seleccionado o inserta los cursores."""
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()
        if suffix is None: suffix = prefix
            
        if selected_text:
            cursor.insertText(f"{prefix}{selected_text}{suffix}")
        else:
            cursor.insertText(f"{prefix}{suffix}")
            cursor.movePosition(cursor.MoveOperation.Left, n=len(suffix))
        
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def update_preview(self):
        """Convierte el texto Markdown a HTML y lo muestra en la vista previa."""
        markdown_text = self.editor.toPlainText()
        html = markdown2.markdown(markdown_text, extras=["fenced-code-blocks", "tables", "strike"])
        
        css = """
        <style>
            body { font-family: sans-serif; line-height: 1.6; padding: 20px; color: #333; }
            pre, code { font-family: monospace; }
            pre { background-color: #f6f8fa; border-radius: 5px; padding: 16px; overflow: auto; }
            table { border-collapse: collapse; width: 100%; margin-top: 1em; margin-bottom: 1em; }
            td, th { border: 1px solid #ddd; padding: 8px; }
            th { background-color: #f2f2f2; font-weight: bold; }
            s, strike { text-decoration: line-through; }
            blockquote { border-left: 4px solid #dfe2e5; color: #6a737d; padding: 0 1em; }
        </style>
        """
        self.preview.setHtml(css + html)

    def open_file(self):
        """Abre un diálogo para seleccionar y leer un archivo .md."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo Markdown", "", "Archivos Markdown (*.md);;Todos los archivos (*.*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.editor.setPlainText(f.read())
                    self.current_file_path = file_path
                    self.setWindowTitle(f"Editor Markdown - {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{e}")

    def save_file(self):
        """Guarda el archivo actual. Si es nuevo, pregunta dónde guardarlo."""
        if self.current_file_path:
            try:
                with open(self.current_file_path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        """Abre un diálogo para guardar el contenido en un nuevo archivo."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo Como", "", "Archivos Markdown (*.md);;Todos los archivos (*.*)")
        if file_path:
            if not file_path.endswith('.md'): file_path += '.md'
            self.current_file_path = file_path
            self.setWindowTitle(f"Editor Markdown - {file_path}")
            self.save_file()

    def export_as_pdf(self):
        """Abre un diálogo para guardar la vista previa como un archivo PDF."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar como PDF", "", "Archivos PDF (*.pdf)")

        if file_path:
            # La función printToPdf del QWebEngineView hace todo el trabajo
            self.preview.page().printToPdf(file_path)
            QMessageBox.information(self, "Éxito", f"El archivo se ha guardado correctamente en:\n{file_path}")

# --- Función principal para ejecutar la aplicación ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = MarkdownEditor()
    editor.show()
    sys.exit(app.exec())