# gui/apollo_gui.py
from __future__ import annotations

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QFrame, QScrollArea
)
from PyQt6.QtGui import QColor, QFont, QPainter, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QPoint, QTimer, QThread, pyqtSignal
import sys

from core.personality import build_prompt


# ------------------------------
# Gradient Bubble for AI messages
# ------------------------------
class GradientBubble(QLabel):
    def __init__(self, text, gradient_colors):
        super().__init__(text)
        self.gradient_colors = gradient_colors
        self.setFont(QFont("Arial", 12))
        self.setStyleSheet("color: white; padding: 10px; border-radius: 12px;")
        self.setWordWrap(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        gradient = QLinearGradient(QPoint(0, 0), QPoint(rect.width(), rect.height()))
        for i, color in enumerate(self.gradient_colors):
            gradient.setColorAt(i / (len(self.gradient_colors) - 1), QColor(*color))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 12, 12)
        super().paintEvent(event)


# ------------------------------
# Typing indicator (three dots)
# ------------------------------
class TypingIndicator(QLabel):
    def __init__(self):
        super().__init__("...")
        self.setFont(QFont("Arial", 16))
        self.setStyleSheet("color: #a0a0ff;")
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.dot_count = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(500)

    def animate(self):
        self.dot_count = (self.dot_count + 1) % 4
        self.setText("." * self.dot_count)


# ------------------------------
# Dedicated LLM thread (SAFE)
# ------------------------------
class LLMThread(QThread):
    finished_text = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, engine, prompt: str, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.prompt = prompt

    def run(self):
        try:
            text = self.engine.generate(
                self.prompt,
                stop=["### User", "### System", "### Apollo"]
            )
            self.finished_text.emit(text)
        except Exception as e:
            self.failed.emit(str(e))


# ------------------------------
# Main Apollo GUI
# ------------------------------
class ApolloGUI(QWidget):
    def __init__(self, engine, memory, max_turns_in_context: int = 10, title: str = "Apollo"):
        super().__init__()
        self.engine = engine
        self.memory = memory
        self.max_turns_in_context = max_turns_in_context
        self.llm_thread: LLMThread | None = None

        self.setWindowTitle(title)
        self.resize(800, 600)

        # Main layout
        main_layout = QHBoxLayout(self)

        # --------------------------
        # Sidebar
        # --------------------------
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(20)
        sidebar.setStyleSheet("background-color: #0d0d1a; border-right: 1px solid #222;")

        # Logo
        logo = QLabel("APOLLO")
        logo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        logo.setStyleSheet(
            "color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, "
            "stop:0 #00f, stop:0.5 #a0f, stop:1 #ff9800);"
        )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo)

        # Sidebar buttons
        self.buttons = {}
        for btn_text in ["Chat", "Explore", "Mission", "Settings"]:
            btn = QPushButton(btn_text)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    border: 2px solid transparent;
                    border-radius: 8px;
                    background-color: #111;
                }
                QPushButton:hover {
                    border: 2px solid qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #00f, stop:0.5 #a0f, stop:1 #ff9800);
                }
            """)
            sidebar_layout.addWidget(btn)
            self.buttons[btn_text] = btn

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # --------------------------
        # Chat area with scroll
        # --------------------------
        self.chat_area_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_area_widget)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.chat_area_widget)
        scroll_area.setStyleSheet("background-color: #0d0d1a; border: none;")
        self.scroll_area = scroll_area

        # --------------------------
        # Input bar
        # --------------------------
        input_bar = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Message Apollo...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #111;
                color: white;
                border-radius: 12px;
                padding: 10px;
            }
        """)

        send_button = QPushButton("➤")
        send_button.setFixedSize(50, 40)
        send_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #00f, stop:0.5 #a0f, stop:1 #ff9800);
                border-radius: 12px;
                font-size: 18px;
            }
        """)
        send_button.clicked.connect(self.handle_send_message)
        self.input_field.returnPressed.connect(self.handle_send_message)

        input_bar.addWidget(self.input_field)
        input_bar.addWidget(send_button)

        # --------------------------
        # Combine chat area + input
        # --------------------------
        right_layout = QVBoxLayout()
        right_layout.addWidget(scroll_area)
        right_layout.addLayout(input_bar)
        main_layout.addLayout(right_layout)

        # --------------------------
        # Initial AI message
        # --------------------------
        self.add_ai_message("Welcome! I'm Apollo. How can I assist you today?")

    # --------------------------
    # Send message handler
    # --------------------------
    def handle_send_message(self):
        user_text = self.input_field.text().strip()
        if not user_text:
            return

        # Prevent multiple concurrent generations (also helps stability)
        if self.llm_thread is not None and self.llm_thread.isRunning():
            return

        # Display user message
        user_bubble = QLabel(user_text)
        user_bubble.setStyleSheet("color: white; background-color: #1a1a2e; padding: 10px; border-radius: 12px;")
        user_bubble.setWordWrap(True)
        user_bubble.setMaximumWidth(500)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, user_bubble, alignment=Qt.AlignmentFlag.AlignRight)

        self.input_field.clear()
        self.auto_scroll()

        # Store user turn
        self.memory.add_turn("user", user_text)

        # Show typing indicator
        self.typing = TypingIndicator()
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.typing, alignment=Qt.AlignmentFlag.AlignLeft)
        self.auto_scroll()

        # Build prompt with last N turns
        recent = self.memory.get_last_turns(self.max_turns_in_context)
        prompt = build_prompt(user_text=user_text, recent_turns=recent)

        # Run model safely in a dedicated QThread
        self.llm_thread = LLMThread(self.engine, prompt, parent=self)
        self.llm_thread.finished_text.connect(self.on_llm_finished)
        self.llm_thread.failed.connect(self.on_llm_error)
        self.llm_thread.start()

    def on_llm_finished(self, text: str):
        # Remove typing indicator
        if hasattr(self, "typing") and self.typing is not None:
            self.typing.deleteLater()
            self.typing = None

        self.memory.add_turn("assistant", text)
        self.add_ai_message(text)

        # Clean up thread reference
        self.llm_thread = None

    def on_llm_error(self, err: str):
        if hasattr(self, "typing") and self.typing is not None:
            self.typing.deleteLater()
            self.typing = None

        self.add_ai_message(f"[Error] {err}")
        self.llm_thread = None

    def add_ai_message(self, text):
        ai_bubble = GradientBubble(text, [(0, 0, 255), (160, 0, 255), (255, 152, 0)])
        ai_bubble.setMaximumWidth(500)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, ai_bubble, alignment=Qt.AlignmentFlag.AlignLeft)
        self.auto_scroll()

    # Auto-scroll chat
    def auto_scroll(self):
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())


def run_gui(engine, memory, app_title: str = "Apollo", max_turns_in_context: int = 10):
    app = QApplication(sys.argv)
    window = ApolloGUI(engine=engine, memory=memory, max_turns_in_context=max_turns_in_context, title=app_title)
    window.show()
    sys.exit(app.exec())
