from PySide6.QtWidgets import QApplication, QTextBrowser, QFileDialog, QVBoxLayout, QWidget, QPushButton
import sys

class MarkdownViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown Viewer")
        self.resize(800, 600)

        # 显示 markdown 的 QTextBrowser
        self.viewer = QTextBrowser(self)
        self.viewer.setOpenExternalLinks(True)  # 允许点击外部链接

        # 打开文件按钮
        self.btn_open = QPushButton("打开 Markdown 文件")
        self.btn_open.clicked.connect(self.load_markdown_file)

        # 布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.btn_open)
        layout.addWidget(self.viewer)

    def load_markdown_file(self):
        """选择并加载 markdown 文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 Markdown 文件", "", "Markdown Files (*.md);;All Files (*)")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                markdown_text = f.read()
            self.viewer.setMarkdown(markdown_text)  # 直接渲染 markdown

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarkdownViewer()
    window.show()
    sys.exit(app.exec())