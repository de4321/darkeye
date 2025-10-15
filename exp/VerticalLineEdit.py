# vertical_line_edit.py

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QFont, QColor, QKeyEvent, QGuiApplication, QClipboard
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF,QSize

class VerticalLineEdit(QWidget):
    def __init__(self, parent=None, font=None, line_spacing=4, placeholder=""):
        super().__init__(parent)
        self._font = font or QFont("Microsoft YaHei", 16)
        self._line_spacing = line_spacing
        self._placeholder = placeholder

        self._chars = []            # 已提交字符列表
        self._cursor_index = 0      # 插入位置（0..len）
        self._preedit = ""          # IME 预编辑字符串
        self._has_focus = False

        # 光标闪烁
        self._cursor_visible = True
        self._cursor_timer = QTimer(self)
        self._cursor_timer.timeout.connect(self._blink_cursor)
        self._cursor_timer.start(500)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setAttribute(Qt.WA_InputMethodEnabled, True)  # 启用输入法事件
        self.setMinimumWidth(50)
        self.setMinimumHeight(60)

    def _blink_cursor(self):
        if self._has_focus:
            self._cursor_visible = not self._cursor_visible
            self.update()

    # API
    def text(self):
        return "".join(self._chars)

    def setText(self, s: str):
        self._chars = list(s)
        self._cursor_index = len(self._chars)
        self._preedit = ""
        self.update()

    # 焦点事件
    def focusInEvent(self, event):
        self._has_focus = True
        self._cursor_visible = True
        self._cursor_timer.start(500)
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self._has_focus = False
        self._preedit = ""
        self._cursor_visible = False
        self.update()
        super().focusOutEvent(event)

    # 支持 IME 的 preedit 和 commit
    def inputMethodEvent(self, event):
        # commitString 属于已经确认的文本（直接插入）
        commit = event.commitString()
        if commit:
            for ch in commit:
                self._chars.insert(self._cursor_index, ch)
                self._cursor_index += 1

        # preeditString 是 IME 组合态，暂存但不入最终文本
        self._preedit = event.preeditString()
        self.update()
        event.accept()

    def inputMethodQuery(self, query):
        # 让输入法知道控件的位置（可改）
        if query == Qt.ImCursorRectangle:
            # 计算当前插入位置纵坐标，返回矩形
            fm = self.fontMetrics()
            line_h = fm.height() + self._line_spacing
            y = fm.ascent() + (self._cursor_index) * line_h
            x = 0
            return QRectF(self.width() // 4, y - fm.ascent(), self.width() // 2, line_h)
        return super().inputMethodQuery(query)

    # 键盘处理（普通字符 / 控制键）
    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        # 复制粘贴（Ctrl+C / Ctrl+V）
        if modifiers & Qt.ControlModifier:
            if key == Qt.Key_C:
                clipboard: QClipboard = QGuiApplication.clipboard()
                clipboard.setText(self.text())
                return
            if key == Qt.Key_V:
                clipboard: QClipboard = QGuiApplication.clipboard()
                txt = clipboard.text()
                for ch in txt:
                    self._chars.insert(self._cursor_index, ch)
                    self._cursor_index += 1
                self.update()
                return

        # 退格
        if key == Qt.Key_Backspace:
            if self._preedit:
                # 如果正在 preedit，通常不处理退格（IME 处理），但我们也清除 preedit
                self._preedit = ""
            elif self._cursor_index > 0:
                self._cursor_index -= 1
                self._chars.pop(self._cursor_index)
            self.update()
            return

        # Delete
        if key == Qt.Key_Delete:
            if self._cursor_index < len(self._chars):
                self._chars.pop(self._cursor_index)
            self.update()
            return

        # 光标移动（上/下 对应 left/right）
        if key == Qt.Key_Up:
            if self._cursor_index > 0:
                self._cursor_index -= 1
            self.update()
            return
        if key == Qt.Key_Down:
            if self._cursor_index < len(self._chars):
                self._cursor_index += 1
            self.update()
            return

        # 可输入字符（不处理复杂 IME，这里允许直接输入 ASCII）
        text = event.text()
        if text:
            # 如果正在 preedit，则让输入法处理（通常 inputMethodEvent 会触发）
            # 但对于直接键入字符（无 IME），我们直接插入
            if not self._preedit:
                for ch in text:
                    self._chars.insert(self._cursor_index, ch)
                    self._cursor_index += 1
                self.update()
            # 若有 preedit，让 IME 处理并等待 commit
            return

        super().keyPressEvent(event)

    # 鼠标点击设置光标位置（按 Y 坐标）
    def mousePressEvent(self, event):
        y = event.position().y()
        fm = self.fontMetrics()
        line_h = fm.height() + self._line_spacing
        idx = int((y) // line_h + 0.5)
        idx = max(0, min(len(self._chars), idx))
        self._cursor_index = idx
        self.setFocus()
        self.update()
        super().mousePressEvent(event)

    # 绘制竖向字符与光标、preedit
    def paintEvent(self, event):
        with QPainter(self) as p:
            p.setRenderHint(QPainter.Antialiasing)
            p.fillRect(self.rect(), QColor(255, 255, 255))  # 背景
            p.setFont(self._font)
            fm = p.fontMetrics()
            line_h = fm.height() + self._line_spacing
            x_center = self.width() / 2.0

            y = fm.ascent()

            # placeholder
            if not self._chars and not self._preedit and not self._has_focus:
                p.setPen(QColor(160, 160, 160))
                p.drawText(QPointF(x_center - fm.horizontalAdvance(self._placeholder) / 2, y), self._placeholder)

            p.setPen(QColor(30, 30, 30))

            for i, ch in enumerate(self._chars):
                # 光标在当前字符前

                # 判断是否是英文/数字/半角符号
                if ch.isascii() and ch.strip() != "":
                    # 旋转绘制英文字符
                    p.save()
                    ch_w = fm.horizontalAdvance(ch)
                    ch_h = fm.height()
                    
                    # 平移到字符绘制中心，再旋转
                    p.translate(x_center, y)
                    p.rotate(90)
                    # 因为旋转后坐标轴变了，这里绘制时 y=0, x 左移半宽
                    p.drawText(QPointF(-ch_w / 2, fm.ascent() / 2), ch)
                    p.restore()
                    y += line_h-10
                else:
                    # 中文等直接竖排绘制
                    
                    ch_w = fm.horizontalAdvance(ch)
                    p.drawText(QPointF(x_center - ch_w / 2, y), ch)
                    y += line_h
                if self._cursor_visible and self._has_focus and self._cursor_index == i:
                    self._draw_cursor(p, x_center, y - fm.ascent(), line_h)

            # 光标在末尾
            if self._cursor_visible and self._has_focus and self._cursor_index == len(self._chars):
                self._draw_cursor(p, x_center, y - fm.ascent(), line_h)

            # 预编辑字符串
            if self._preedit:
                p.setPen(QColor(0, 80, 200))
                pe_w = fm.horizontalAdvance(self._preedit)
                p.drawText(QPointF(x_center - pe_w / 2, y), self._preedit)
                p.drawLine(x_center - pe_w / 2, y + 2, x_center + pe_w / 2, y + 2)

    def _draw_cursor(self, painter: QPainter, x_center: float, y_top: float, line_h: float):
        """绘制横向插入光标（短横线）"""
        fm = painter.fontMetrics()
        cursor_w = fm.horizontalAdvance("M") * 0.8  # 横线宽度，0.8 表示稍短于字符宽
        # 横线放在字符底部，也可以放在中间
        cx_left = x_center - cursor_w / 2
        cy = y_top +  - 2  # 离底部 2px
        
        if self._cursor_visible:
            painter.setPen(QColor(20, 20, 20))
            painter.drawLine(QPointF(cx_left, cy), QPointF(cx_left + cursor_w, cy))

    # 推荐实现 sizeHint
    def sizeHint(self):
        fm = self.fontMetrics()
        # 宽度可以按字体最大字符宽 + padding
        w = fm.horizontalAdvance('W')
        # 高度按当前字符数（或最小高度）
        h = max(60, int((fm.height() + self._line_spacing) * max(1, len(self._chars)) + 8))
        return QSize(w, h)
