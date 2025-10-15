from PySide6.QtWidgets import QApplication, QTextBrowser, QFileDialog, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QUrl
import re, sys, os


class MarkdownViewer(QWidget):
    def __init__(self, base_dir="./docs"):
        super().__init__()
        self.setWindowTitle("Markdown Wiki Viewer")
        self.resize(800, 600)

        self.base_dir = base_dir  # 存放 markdown 文件的文件夹
        os.makedirs(self.base_dir, exist_ok=True)

        self.viewer = QTextBrowser(self)
        self.viewer.setOpenExternalLinks(False)  # 不自动打开外部链接
        self.viewer.anchorClicked.connect(self.handle_link)

        self.btn_open = QPushButton("打开 Markdown 文件")
        self.btn_open.clicked.connect(self.load_markdown_file)

        layout = QVBoxLayout(self)
        layout.addWidget(self.btn_open)
        layout.addWidget(self.viewer)

    def preprocess_markdown(self, text: str) -> str:
        """把 [[Page]] 转换为 HTML 链接"""
        return re.sub(r"\[\[(.+?)\]\]", r'<a href="internal:\1">\1</a>', text)

    def load_markdown_file(self, file_path=None):
        """加载 markdown 文件"""
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择 Markdown 文件", self.base_dir, "Markdown Files (*.md);;All Files (*)"
            )
        if not file_path:
            return

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # 转换 wiki 链接后再渲染
        text = self.preprocess_markdown(text)
        self.viewer.setMarkdown(text)
        self.current_file = file_path

    def handle_link(self, url: QUrl):
        """处理点击 [[Page]] 的跳转"""
        if url.scheme() == "internal":
            page = url.path()[1:] if url.path().startswith("/") else url.path()
            file_path = os.path.join(self.base_dir, f"{page}.md")
            if os.path.exists(file_path):
                self.load_markdown_file(file_path)
            else:
                # 如果文件不存在，可以新建
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"# {page}\n")
                self.load_markdown_file(file_path)
        else:
            # 外部链接交给系统打开
            import webbrowser
            webbrowser.open(url.toString())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarkdownViewer()
    window.show()
    sys.exit(app.exec())
