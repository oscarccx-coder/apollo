from __future__ import annotations

import sys

from PyQt6.QtCore import QPoint, QThread, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from apollo.intelligence.intents import parse_chat_intent
from apollo.intelligence.personality import build_prompt
from apollo.intelligence.research import completion_message, run_local_research


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
        gradient = QLinearGradient(
            QPoint(0, 0),
            QPoint(rect.width(), rect.height()),
        )
        for i, color in enumerate(self.gradient_colors):
            gradient.setColorAt(
                i / (len(self.gradient_colors) - 1),
                QColor(*color),
            )
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 12, 12)
        super().paintEvent(event)


class TypingIndicator(QLabel):
    def __init__(self):
        super().__init__("...")
        self.setFont(QFont("Arial", 11))
        self.setStyleSheet("color: #a0a0ff;")
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.dot_count = 0
        self.status_text = ""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(500)

    def set_status(self, text: str):
        self.status_text = str(text or "").strip()
        self.animate()

    def animate(self):
        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * (self.dot_count or 1)
        self.setText(
            f"{self.status_text}{dots}" if self.status_text else dots
        )


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
                stop=["### User", "### System", "### Apollo"],
            )
            self.finished_text.emit(text)
        except Exception as exc:
            self.failed.emit(str(exc))


class ResearchThread(QThread):
    progress = pyqtSignal(str)
    finished_research = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, engine, topic: str, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.topic = topic

    def run(self):
        try:
            result = run_local_research(
                self.engine,
                self.topic,
                progress=self.progress.emit,
            )
            self.finished_research.emit({
                "topic": result.topic,
                "summary": result.summary,
                "findings": result.findings,
                "method": result.method,
            })
        except Exception as exc:
            self.failed.emit(str(exc))


class ApolloGUI(QWidget):
    def __init__(
        self,
        engine,
        memory,
        max_turns_in_context: int = 10,
        title: str = "Apollo",
    ):
        super().__init__()
        self.engine = engine
        self.memory = memory
        self.max_turns_in_context = max_turns_in_context
        self.llm_thread: LLMThread | None = None
        self.research_thread: ResearchThread | None = None
        self.typing: TypingIndicator | None = None

        self.setWindowTitle(title)
        self.resize(800, 600)

        main_layout = QHBoxLayout(self)
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(20)
        sidebar.setStyleSheet(
            "background-color: #0d0d1a; border-right: 1px solid #222;"
        )

        logo = QLabel("APOLLO")
        logo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        logo.setStyleSheet("color: #9f8cff;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo)

        self.buttons = {}
        for btn_text in ["Chat", "Explore", "Mission", "Settings"]:
            btn = QPushButton(btn_text)
            btn.setFixedHeight(40)
            btn.setStyleSheet(
                "QPushButton{color:white;border:2px solid transparent;"
                "border-radius:8px;background-color:#111;}"
                "QPushButton:hover{border:2px solid #6040ff;}"
            )
            sidebar_layout.addWidget(btn)
            self.buttons[btn_text] = btn

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        self.chat_area_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_area_widget)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.chat_area_widget)
        self.scroll_area.setStyleSheet(
            "background-color:#0d0d1a;border:none;"
        )

        input_bar = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(
            "Message Apollo… try: research quantum computing"
        )
        self.input_field.setStyleSheet(
            "QLineEdit{background-color:#111;color:white;"
            "border-radius:12px;padding:10px;}"
        )

        send_button = QPushButton("➤")
        send_button.setFixedSize(50, 40)
        send_button.setStyleSheet(
            "QPushButton{color:white;background-color:#6236ff;"
            "border-radius:12px;font-size:18px;}"
        )
        send_button.clicked.connect(self.handle_send_message)
        self.input_field.returnPressed.connect(self.handle_send_message)
        input_bar.addWidget(self.input_field)
        input_bar.addWidget(send_button)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.scroll_area)
        right_layout.addLayout(input_bar)
        main_layout.addLayout(right_layout)

        self.add_ai_message(
            "Apollo online. Ask normally, or tell me to research a topic "
            "and I'll work through it without dumping a textbook on your head."
        )

    def _busy(self) -> bool:
        return bool(
            (self.llm_thread is not None and self.llm_thread.isRunning())
            or (
                self.research_thread is not None
                and self.research_thread.isRunning()
            )
        )

    def _show_user_message(self, text: str) -> None:
        bubble = QLabel(text)
        bubble.setStyleSheet(
            "color:white;background-color:#1a1a2e;"
            "padding:10px;border-radius:12px;"
        )
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(500)
        self.chat_layout.insertWidget(
            self.chat_layout.count() - 1,
            bubble,
            alignment=Qt.AlignmentFlag.AlignRight,
        )

    def _start_typing(self, status: str = "") -> None:
        self._remove_typing()
        self.typing = TypingIndicator()
        if status:
            self.typing.set_status(status)
        self.chat_layout.insertWidget(
            self.chat_layout.count() - 1,
            self.typing,
            alignment=Qt.AlignmentFlag.AlignLeft,
        )
        self.auto_scroll()

    def _remove_typing(self) -> None:
        if self.typing is not None:
            self.typing.deleteLater()
            self.typing = None

    def handle_send_message(self) -> None:
        user_text = self.input_field.text().strip()
        if not user_text or self._busy():
            return

        self._show_user_message(user_text)
        self.input_field.clear()
        self.auto_scroll()

        recent = self.memory.get_last_turns(
            self.max_turns_in_context
        )
        self.memory.add_turn("user", user_text)

        intent = parse_chat_intent(user_text)
        if intent.kind == "research":
            self._start_research(intent.target)
            return

        knowledge = self.memory.get_relevant_research(
            user_text,
            limit=3,
        )
        prompt = build_prompt(
            user_text=user_text,
            recent_turns=recent,
            knowledge_notes=knowledge,
        )

        self._start_typing()
        self.llm_thread = LLMThread(
            self.engine,
            prompt,
            parent=self,
        )
        self.llm_thread.finished_text.connect(
            self.on_llm_finished
        )
        self.llm_thread.failed.connect(self.on_llm_error)
        self.llm_thread.finished.connect(
            self._clear_llm_thread
        )
        self.llm_thread.start()

    def _start_research(self, topic: str) -> None:
        self._start_typing(f"Researching {topic} — ")
        self.research_thread = ResearchThread(
            self.engine,
            topic,
            parent=self,
        )
        self.research_thread.progress.connect(
            self.on_research_progress
        )
        self.research_thread.finished_research.connect(
            self.on_research_finished
        )
        self.research_thread.failed.connect(
            self.on_research_error
        )
        self.research_thread.finished.connect(
            self._clear_research_thread
        )
        self.research_thread.start()

    def _clear_llm_thread(self) -> None:
        thread = self.llm_thread
        self.llm_thread = None
        if thread is not None:
            thread.deleteLater()

    def _clear_research_thread(self) -> None:
        thread = self.research_thread
        self.research_thread = None
        if thread is not None:
            thread.deleteLater()

    def on_research_progress(self, message: str) -> None:
        if self.typing is not None:
            self.typing.set_status(f"{message} — ")

    def on_research_finished(self, result) -> None:
        self._remove_typing()
        self.memory.add_research(
            result["topic"],
            result["summary"],
            method=result.get(
                "method",
                "local_multi_pass",
            ),
        )
        message = completion_message(result["topic"])
        self.memory.add_turn("assistant", message)
        self.add_ai_message(message)

    def on_research_error(self, err: str) -> None:
        self._remove_typing()
        message = f"Research stopped: {err}"
        self.memory.add_turn("assistant", message)
        self.add_ai_message(message)

    def on_llm_finished(self, text: str) -> None:
        self._remove_typing()
        self.memory.add_turn("assistant", text)
        self.add_ai_message(text)

    def on_llm_error(self, err: str) -> None:
        self._remove_typing()
        self.add_ai_message(f"[Error] {err}")

    def add_ai_message(self, text) -> None:
        bubble = GradientBubble(
            text,
            [(0, 0, 255), (160, 0, 255), (255, 152, 0)],
        )
        bubble.setMaximumWidth(500)
        self.chat_layout.insertWidget(
            self.chat_layout.count() - 1,
            bubble,
            alignment=Qt.AlignmentFlag.AlignLeft,
        )
        self.auto_scroll()

    def auto_scroll(self) -> None:
        QTimer.singleShot(
            0,
            lambda: self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            ),
        )

    def closeEvent(self, event) -> None:
        try:
            self.engine.close()
        except Exception:
            pass
        super().closeEvent(event)


def run_gui(
    engine,
    memory,
    app_title: str = "Apollo",
    max_turns_in_context: int = 10,
) -> None:
    app = QApplication(sys.argv)
    window = ApolloGUI(
        engine=engine,
        memory=memory,
        max_turns_in_context=max_turns_in_context,
        title=app_title,
    )
    window.show()
    sys.exit(app.exec())
