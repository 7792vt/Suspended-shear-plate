import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QPushButton, QScrollArea, QLabel, QFrame,
                           QHBoxLayout, QMessageBox, QLineEdit, QMenu,
                           QInputDialog, QDialog, QPlainTextEdit)
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import (QPalette, QColor, QScreen, QPainter, QLinearGradient, 
                        QPen, QBrush, QPainterPath, QCursor)
import pyperclip

class CustomMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 5px;
                margin: 2px 5px;
                color: #334155;
                font-size: 13px;
            }
            QMenu::item:selected {
                background: #f0f9ff;
                color: #3b82f6;
            }
        """)

class CustomMessageBox(QDialog):
    def __init__(self, parent=None, text=""):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui(text)
        
    def setup_ui(self, text):
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 主容器
        container = QWidget()
        container.setFixedSize(320, 160)
        container.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 #ffffff,
                    stop: 1 #f8fafc
                );
                border: 1px solid #e2e8f0;
                border-radius: 15px;
            }
        """)
        
        # 容器布局
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(25, 25, 25, 25)
        container_layout.setSpacing(20)
        
        # 图标和消息容器
        message_container = QWidget()
        message_container.setStyleSheet("background: transparent; border: none;")
        message_layout = QHBoxLayout(message_container)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(15)
        
        # 警告图标
        icon_label = QLabel("⚠")
        icon_label.setStyleSheet("""
            QLabel {
                color: #eab308;
                font-size: 24px;
                background: transparent;
            }
        """)
        message_layout.addWidget(icon_label)
        
        # 消息文本
        message = QLabel(text)
        message.setStyleSheet("""
            QLabel {
                color: #334155;
                font-size: 14px;
                background: transparent;
            }
        """)
        message_layout.addWidget(message, 1)
        container_layout.addWidget(message_container)
        
        # 按钮容器
        button_container = QWidget()
        button_container.setStyleSheet("background: transparent; border: none;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(15)
        
        # 创建按钮
        self.no_button = QPushButton("取消")
        self.yes_button = QPushButton("确定")
        
        # 取消按钮样式
        self.no_button.setFixedSize(100, 36)
        self.no_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.no_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 #60a5fa,
                    stop: 1 #3b82f6
                );
                color: white;
                border: none;
                border-radius: 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 #3b82f6,
                    stop: 1 #2563eb
                );
            }
        """)
        
        # 确定按钮样式
        self.yes_button.setFixedSize(100, 36)
        self.yes_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.yes_button.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #64748b;
                border: 1px solid #cbd5e1;
                border-radius: 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e2e8f0;
                color: #475569;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.yes_button)  # 确定按钮在左边
        button_layout.addWidget(self.no_button)   # 取消按钮在右边
        button_layout.addStretch()
        
        container_layout.addWidget(button_container)
        
        layout.addWidget(container, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 连接按钮信号
        self.yes_button.clicked.connect(self.accept)
        self.no_button.clicked.connect(self.reject)
        
        # 设置默认焦点为取消按钮
        self.no_button.setFocus()
        
    def showEvent(self, event):
        # 居中显示
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)
        super().showEvent(event)

class CustomInputDialog(QDialog):
    def __init__(self, parent=None, text=""):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.text = text
        self.result_text = text
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 主容器
        container = QWidget(self)
        container.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 #f5f7fa,
                    stop: 1 #e4e7eb
                );
                border-radius: 15px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)
        
        # 标题
        title = QLabel("编辑内容")
        title.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 15px;
                font-weight: bold;
                background: transparent;
            }
        """)
        container_layout.addWidget(title)
        
        # 文本编辑框
        self.text_edit = QPlainTextEdit(self.text)
        self.text_edit.setMinimumHeight(120)
        self.text_edit.setStyleSheet("""
            QPlainTextEdit {
                padding: 10px;
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 10px;
                font-size: 13px;
                color: #334155;
                selection-background-color: #93c5fd;
            }
            QPlainTextEdit:focus {
                border: 1px solid #60a5fa;
                background: #f8fafc;
            }
        """)
        container_layout.addWidget(self.text_edit)
        
        # 按钮容器
        button_container = QWidget()
        button_container.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 按钮
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        for button in [ok_button, cancel_button]:
            button.setFixedSize(80, 32)
            button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(
                        x1: 0, y1: 0,
                        x2: 0, y2: 1,
                        stop: 0 #60a5fa,
                        stop: 1 #3b82f6
                    );
                    color: white;
                    border: none;
                    border-radius: 16px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: qlineargradient(
                        x1: 0, y1: 0,
                        x2: 0, y2: 1,
                        stop: 0 #3b82f6,
                        stop: 1 #2563eb
                    );
                }
            """)
            
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        container_layout.addWidget(button_container)
        layout.addWidget(container)
        
    def get_text(self):
        return self.text_edit.toPlainText()
        
    def accept(self):
        self.result_text = self.text_edit.toPlainText()
        super().accept()

class ClipItem(QFrame):
    def __init__(self, text, parent=None, manager=None):
        super().__init__(parent)
        self.text = text
        self.manager = manager
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        
        # 文本标签 - 只显示第一行，限制40个字符
        first_line = self.text.split('\n')[0]
        display_text = first_line[:40] + "..." if len(first_line) > 40 else first_line
        self.label = QLabel(display_text)
        self.label.setFixedHeight(25)
        self.label.setStyleSheet("""
            QLabel {
                color: #334155;
                font-size: 13px;
            }
        """)
        
        # 删除按钮
        delete_button = QPushButton("×")
        delete_button.setFixedSize(20, 20)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ef4444;
            }
        """)
        delete_button.clicked.connect(self.confirm_delete)
        
        layout.addWidget(self.label, stretch=1)
        layout.addWidget(delete_button)
        
        self.setStyleSheet("""
            ClipItem {
                background: white;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }
            ClipItem:hover {
                background: #f8fafc;
                border: 1px solid #60a5fa;
            }
        """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pyperclip.copy(self.text)
            self.flash_feedback()
        elif event.button() == Qt.MouseButton.RightButton and self.manager:
            self.show_context_menu(event.pos())
            
    def show_context_menu(self, pos):
        menu = CustomMenu(self)
        edit_action = menu.addAction("编辑")
        edit_action.triggered.connect(self.edit_content)
        menu.exec(self.mapToGlobal(pos))
        
    def edit_content(self):
        if self.manager:
            dialog = CustomInputDialog(self, self.text)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_text = dialog.get_text()
                if new_text:
                    self.manager.edit_clip(self.text, new_text)
        
    def flash_feedback(self):
        original_style = self.styleSheet()
        self.setStyleSheet("""
            ClipItem {
                background: #dbeafe;
                border-radius: 10px;
                border: 1px solid #60a5fa;
            }
        """)
        QTimer.singleShot(200, lambda: self.setStyleSheet(original_style))
        
    def confirm_delete(self):
        if self.manager:
            dialog = CustomMessageBox(self.window(), "确定要删除这条记录吗？")
            
            # 获取主窗口的中心点
            main_window = self.window()
            center = main_window.geometry().center()
            
            # 移动对话框到主窗口中心
            dialog.move(center.x() - dialog.width() // 2,
                       center.y() - dialog.height() // 2)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.manager.delete_clip(self.text)

class EmptyClipItem(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(41)  # 调整高度以匹配新的ClipItem高度
        self.setStyleSheet("""
            QFrame {
                background: rgba(241, 245, 249, 0.6);
                border-radius: 10px;
                border: 1px dashed #cbd5e1;
            }
        """)

class ClipboardManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 初始化界面状态
        self.clips = []
        self.filtered_clips = []
        self.current_page = 0
        self.items_per_page = 7
        self.dragging = False
        self.drag_position = None
        
        # 根据屏幕分辨率设置窗口大小
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        
        # 设置窗口大小为屏幕宽度的20%和高度的50%
        self.window_width = int(screen_size.width() * 0.2)
        self.window_height = int(screen_size.height() * 0.5)
        
        # 确保窗口大小在合理范围内
        self.window_width = max(300, min(self.window_width, 500))
        self.window_height = max(400, min(self.window_height, 800))
        
        self.setFixedSize(self.window_width, self.window_height)
        
        # 初始化UI
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 设置渐变背景
        self.setStyleSheet("""
            QMainWindow {
                background: transparent;
            }
        """)
        
        self.central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 #f5f7fa,
                    stop: 1 #e4e7eb
                );
                border-radius: 15px;
            }
        """)
        
        # 主布局
        self.layout = QVBoxLayout(self.central_widget)
        margin_h = int(self.window_width * 0.05)   # 水平边距为窗口宽度的5%
        margin_v = int(self.window_height * 0.025) # 垂直边距为窗口高度的2.5%
        self.layout.setContentsMargins(margin_h, margin_v, margin_h, margin_v)
        self.layout.setSpacing(int(self.window_height * 0.02))
        
        # 标题栏
        self.create_title_bar()
        
        # 搜索框
        self.create_search_bar()
        
        # 内容区域
        self.create_content_area()
        
        # 分页控制
        self.create_pagination_controls()
        
        # 添加按钮
        self.add_button = QPushButton("+ 添加剪贴板内容")
        self.add_button.setFixedHeight(40)
        self.add_button.clicked.connect(self.add_clip)
        self.add_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 #60a5fa,
                    stop: 1 #3b82f6
                );
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 #3b82f6,
                    stop: 1 #2563eb
                );
            }
        """)
        self.layout.addWidget(self.add_button)
        
        # 设置窗口初始位置
        screen = QApplication.primaryScreen()
        self.move(
            screen.availableGeometry().width() - self.width() - 20,
            (screen.availableGeometry().height() - self.height()) // 2
        )
        
    def create_search_bar(self):
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索剪贴板内容...")
        self.search_input.textChanged.connect(self.search_clips)
        self.search_input.setFixedHeight(36)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 15px;
                border: 1px solid #d1d5db;
                border-radius: 18px;
                background: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #60a5fa;
                background: #f8fafc;
            }
        """)
        
        search_layout.addWidget(self.search_input)
        self.layout.addWidget(search_container)
        
    def create_pagination_controls(self):
        pagination = QWidget()
        pagination_layout = QHBoxLayout(pagination)
        
        self.prev_button = QPushButton("上一页")
        self.next_button = QPushButton("下一页")
        self.page_label = QLabel("1/1")
        
        for button in [self.prev_button, self.next_button]:
            button.setFixedHeight(30)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    color: #2c3e50;
                }
                QPushButton:hover {
                    background-color: #bdc3c7;
                }
                QPushButton:disabled {
                    background-color: #f5f6f7;
                    color: #95a5a6;
                }
            """)
            
        self.page_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 0 10px;
            }
        """)
        
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)
        
        self.layout.addWidget(pagination)
        
    def search_clips(self, text):
        self.current_page = 0
        if text:
            self.filtered_clips = [clip for clip in self.clips if text.lower() in clip.lower()]
        else:
            self.filtered_clips = self.clips.copy()
        self.update_clips_display()
        
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_clips_display()
            
    def next_page(self):
        max_pages = (len(self.filtered_clips) - 1) // self.items_per_page
        if self.current_page < max_pages:
            self.current_page += 1
            self.update_clips_display()
            
    def update_pagination_buttons(self):
        total_pages = max(1, (len(self.filtered_clips) - 1) // self.items_per_page + 1)
        self.page_label.setText(f"{self.current_page + 1}/{total_pages}")
        
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(
            self.current_page < (len(self.filtered_clips) - 1) // self.items_per_page
        )
        
    def create_title_bar(self):
        self.title_bar = QWidget()
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 5)
        
        # 标题
        title_label = QLabel("悬浮剪切板")
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 15px;
                font-weight: bold;
            }
        """)
        
        # 关闭按钮
        close_button = QPushButton("×")
        close_button.setFixedSize(24, 24)
        close_button.clicked.connect(self.close_application)  # 修改为新的关闭方法
        close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #64748b;
                border: none;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ef4444;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(close_button)
        self.layout.addWidget(self.title_bar)
        
        # 设置标题栏可拖动
        self.title_bar.mousePressEvent = self.title_bar_mouse_press
        self.title_bar.mouseMoveEvent = self.title_bar_mouse_move
        self.title_bar.mouseReleaseEvent = self.title_bar_mouse_release
        
    def title_bar_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.position().toPoint()
            event.accept()
            
    def title_bar_mouse_move(self, event):
        if self.dragging:
            self.move(self.pos() + event.position().toPoint() - self.drag_position)
            event.accept()
            
    def title_bar_mouse_release(self, event):
        self.dragging = False

    def create_content_area(self):
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(8)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.content_widget)
        
    def add_clip(self):
        content = pyperclip.paste()
        if content and content not in self.clips:
            self.clips.append(content)
            if len(self.clips) > 100:  # 增加最大存储量
                self.clips.pop(0)
            self.search_clips(self.search_input.text())
            
    def delete_clip(self, text):
        if text in self.clips:
            self.clips.remove(text)
            self.search_clips(self.search_input.text())
            
    def update_clips_display(self):
        # 清除现有内容
        for i in reversed(range(self.content_layout.count())): 
            self.content_layout.itemAt(i).widget().setParent(None)
            
        # 计算当前页的内容
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        current_page_clips = self.filtered_clips[start_idx:end_idx]
        
        # 添加内容，如果不足7个则添加空白项
        for i in range(self.items_per_page):
            if i < len(current_page_clips):
                clip_item = ClipItem(current_page_clips[i], self.content_widget, self)
                self.content_layout.addWidget(clip_item)
            else:
                empty_item = EmptyClipItem(self.content_widget)
                self.content_layout.addWidget(empty_item)
            
        # 更新分页按钮状态
        self.update_pagination_buttons()
        
    def edit_clip(self, old_text, new_text):
        if old_text in self.clips:
            index = self.clips.index(old_text)
            self.clips[index] = new_text
            self.search_clips(self.search_input.text())
            
    def mousePressEvent(self, event):
        pass  # 移除主窗口的鼠标事件处理
            
    def mouseMoveEvent(self, event):
        pass
            
    def mouseReleaseEvent(self, event):
        pass
        
    def save_settings(self):
        settings = {
            'geometry': {
                'x': self.x(),
                'y': self.y(),
                'width': self.width(),
                'height': self.height()
            },
            'clips': self.clips
        }
        
        config_dir = Path.home() / '.clipboard_manager'
        config_dir.mkdir(exist_ok=True)
        
        with open(config_dir / 'settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f)
            
    def load_settings(self):
        config_file = Path.home() / '.clipboard_manager' / 'settings.json'
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                geom = settings.get('geometry', {})
                self.setGeometry(
                    geom.get('x', self.x()),
                    geom.get('y', self.y()),
                    geom.get('width', self.width()),
                    geom.get('height', self.height())
                )
                
                self.clips = settings.get('clips', [])
                self.filtered_clips = self.clips.copy()
                self.update_clips_display()
            except:
                pass
                
    def close_application(self):
        # 保存设置
        self.save_settings()
        # 退出应用
        QApplication.quit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制主窗口背景
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 245))
        gradient.setColorAt(1, QColor(236, 240, 241, 245))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(self.rect(), 15, 15)
        
        # 绘制边框
        painter.setPen(QPen(QColor(189, 195, 199, 100), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 15, 15)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ClipboardManager()
    window.show()
    sys.exit(app.exec()) 