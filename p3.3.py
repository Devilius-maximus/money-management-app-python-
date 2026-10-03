
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys



def format_money(amount):
    return f"${amount:,.2f}"

class PieChart(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.slices = []

    def set_slices(self, slices):
        self.slices = slices
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        side = min(self.width(), self.height())
        rect = QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)

        if not self.slices:
            painter.setBrush(QColor("#8ad9ef"))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(rect)
            return

        total = sum(v for v, _, _ in self.slices) or 1
        start_angle = 0
        
        for value, color, _ in self.slices:

            span = 360 * value / total
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawPie(rect, int(start_angle * 16), int(span * 16))
            start_angle += span

class rectangular_side(QFrame):
    def __init__(self, title="History", parent=None, on_add_clicked=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet("""
            QFrame#card {
                border: 1px solid #bbb;
                border-radius: 10px;
                background: #fff;
            }
            QLabel {
                background: transparent;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        header = QHBoxLayout()
        dot = QLabel()
        dot.setFixedSize(10, 10)
        dot.setStyleSheet("background:#6aa9ff; border-radius:5px;")
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))

        header.addWidget(dot)
        header.addSpacing(5)
        header.addWidget(title_label)
        header.addStretch()

        add_btn = QPushButton("+")
        add_btn.setFixedSize(26, 26)
        add_btn.setStyleSheet("""
            QPushButton {
                border-radius: 13px;
                background: #3aa76d;
                color: white;
            }
        """)
        if on_add_clicked:
            add_btn.clicked.connect(on_add_clicked)
        header.addWidget(add_btn)
        layout.addLayout(header)

        self.entries_layout = QVBoxLayout()
        self.entries_layout.setSpacing(6)
        self.placeholder = QLabel("No entries yet")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("color: #777; font-style: italic; background: transparent;")
        self.entries_layout.addWidget(self.placeholder)
        layout.addLayout(self.entries_layout)
        layout.addStretch()

    def add_entry(self, text: str):
        if self.placeholder is not None:
            self.entries_layout.removeWidget(self.placeholder)
            self.placeholder.deleteLater()
            self.placeholder = None
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 11))
        label.setStyleSheet("background: transparent;")
        self.entries_layout.addWidget(label)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("")
        self.resize(950, 580)

        # Shared style for input boxes
        self.lineedit_style = """
            QLineEdit {
                padding: 6px 10px;
                border: 1px solid #aaa;
                border-radius: 6px;
                background: #fff;
            }
            QLineEdit:focus {
                border: 1px solid #2d88ff;
                background: #fdfdfd;
            }
        """

        self.stacked = QStackedLayout()
        self.setLayout(self.stacked)

        self.page_dashboard = QWidget()
        self.page_income_form = QWidget()
        self.page_spend_form = QWidget()

        self.incomes = []
        self.spendings = []
        self.total_money = 0.0

        self.init_dashboard_ui()
        self.init_income_form_ui()
        self.init_spend_form_ui()

        self.stacked.addWidget(self.page_dashboard)
        self.stacked.addWidget(self.page_income_form)
        self.stacked.addWidget(self.page_spend_form)
        self.stacked.setCurrentIndex(0)

        self._animations = []

    def animate_to_page(self, target_widget):
        target_index = self.stacked.indexOf(target_widget)
        current = self.stacked.currentWidget()

        if current is None:
            self.stacked.setCurrentIndex(target_index)
            return

        effect_out = QGraphicsOpacityEffect(current)
        current.setGraphicsEffect(effect_out)
        anim_out = QPropertyAnimation(effect_out, b"opacity")
        anim_out.setDuration(300)
        anim_out.setStartValue(1)
        anim_out.setEndValue(0)
        anim_out.setEasingCurve(QEasingCurve.InOutQuad)

        def switch_page():
            self.stacked.setCurrentIndex(target_index)
            new_page = self.stacked.currentWidget()
            effect_in = QGraphicsOpacityEffect(new_page)
            new_page.setGraphicsEffect(effect_in)
            anim_in = QPropertyAnimation(effect_in, b"opacity")
            anim_in.setDuration(300)
            anim_in.setStartValue(0)
            anim_in.setEndValue(1)
            anim_in.setEasingCurve(QEasingCurve.InOutQuad)
            anim_in.start()
            self._animations.append(anim_in)

        anim_out.finished.connect(switch_page)
        anim_out.start()
        self._animations.append(anim_out)

    def init_dashboard_ui(self):
        self.page_dashboard.setStyleSheet("background-color: #e6e6e6;")
        root = QHBoxLayout(self.page_dashboard)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(18)

        left_col = QVBoxLayout()
        left_col.setSpacing(15)

        money_layout = QHBoxLayout()
        money_label = QLabel("Money:")
        money_label.setFont(QFont("Segoe UI", 17, QFont.Bold))
        self.money_value = QLabel(format_money(self.total_money))
        self.money_value.setFont(QFont("Segoe UI", 16))
        self.money_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.money_value.setStyleSheet("""
            QLabel {
                background: #f9f6f1;
                border-radius: 6px;
                padding: 3px 9px;
                color: #003366;
            }
        """)
        money_layout.addWidget(money_label)
        money_layout.addWidget(self.money_value, stretch=1)
        money_layout.addStretch()
        left_col.addLayout(money_layout)

        self.chartWidget = PieChart()
        left_col.addWidget(self.chartWidget, stretch=1)

        root.addLayout(left_col, 2)

        right_col = QVBoxLayout()
        right_col.setSpacing(11)

        self.income_card = rectangular_side(
            "Income history",
            on_add_clicked=lambda: self.animate_to_page(self.page_income_form)
        )
        right_col.addWidget(self.income_card)

        self.spend_card = rectangular_side(
            "Spend history",
            on_add_clicked=lambda: self.animate_to_page(self.page_spend_form)
        )
        right_col.addWidget(self.spend_card)

        root.addLayout(right_col, 1)

    def init_income_form_ui(self):
        self.page_income_form.setStyleSheet("background-color: #e6e6e6;")
        layout = QVBoxLayout(self.page_income_form)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Income")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))

        amount_label = QLabel("Income Amount:")
        amount_label.setFont(QFont("Segoe UI", 14))
        self.income_amount_input = QLineEdit()
        self.income_amount_input.setFont(QFont("Segoe UI", 14))
        self.income_amount_input.setPlaceholderText("Enter amount...")
        self.income_amount_input.setStyleSheet(self.lineedit_style)

        source_label = QLabel("Source of Income:")
        source_label.setFont(QFont("Segoe UI", 14))
        self.income_source_input = QLineEdit()
        self.income_source_input.setFont(QFont("Segoe UI", 14))
        self.income_source_input.setPlaceholderText("Where did it come from?")
        self.income_source_input.setStyleSheet(self.lineedit_style)

        submit_btn = QPushButton("Submit")
        submit_btn.setFixedHeight(40)
        submit_btn.setStyleSheet("""
            QPushButton {
                background: #2d88ff;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px;
            }
        """)
        submit_btn.clicked.connect(self.handle_income_submit)

        submit_btn.setStyleSheet("""
    QPushButton {
        background: #2d88ff;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        padding: 8px;
    }
    QPushButton:hover {
        background: #1a6fe0;   /* darker blue on hover */
    }
""")


        back_btn = QPushButton("Back")
        back_btn.setFixedHeight(38)
        back_btn.setStyleSheet("""
            QPushButton {
                 background: transparent;
                color: #333;
                border: 2px solid #aaa;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                border: 2px solid #2d88ff;
                color: #2d88ff;
            }
        """)
        back_btn.clicked.connect(lambda: self.animate_to_page(self.page_dashboard))

        layout.addWidget(title)
        layout.addWidget(amount_label)
        layout.addWidget(self.income_amount_input)
        layout.addWidget(source_label)
        layout.addWidget(self.income_source_input)
        layout.addWidget(submit_btn)
        layout.addWidget(back_btn)

    def init_spend_form_ui(self):
        self.page_spend_form.setStyleSheet("background-color: #e6e6e6;")
        layout = QVBoxLayout(self.page_spend_form)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Spending")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))

        amount_label = QLabel("Amount Spent:")
        amount_label.setFont(QFont("Segoe UI", 14))
        self.spend_amount_input = QLineEdit()
        self.spend_amount_input.setFont(QFont("Segoe UI", 14))
        self.spend_amount_input.setPlaceholderText("Enter amount...")
        self.spend_amount_input.setStyleSheet(self.lineedit_style)

        reason_label = QLabel("Reason:")
        reason_label.setFont(QFont("Segoe UI", 14))
        self.spend_reason_input = QLineEdit()
        self.spend_reason_input.setFont(QFont("Segoe UI", 14))
        self.spend_reason_input.setPlaceholderText("What did you spend it on?")
        self.spend_reason_input.setStyleSheet(self.lineedit_style)

        submit_btn = QPushButton("Submit")
        submit_btn.setFixedHeight(40)
        submit_btn.setStyleSheet("""
            QPushButton {
                background: #ff4d4d;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px;
            }
        """)
        submit_btn.clicked.connect(self.handle_spend_submit)

        submit_btn.setStyleSheet("""
    QPushButton {
        background: #ff4d4d;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        padding: 8px;
    }
    QPushButton:hover {
        background: #e63b3b;   /* darker red on hover */
    }
""")

        back_btn = QPushButton("Back")
        back_btn.setFixedHeight(38)
        back_btn.setStyleSheet("""
            QPushButton {
                 background: transparent;
                color: #333;
                border: 2px solid #aaa;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                border: 2px solid #ff4d4d;
                color: #ff4d4d;
            }
        """)
        back_btn.clicked.connect(lambda: self.animate_to_page(self.page_dashboard))

        layout.addWidget(title)
        layout.addWidget(amount_label)
        layout.addWidget(self.spend_amount_input)
        layout.addWidget(reason_label)
        layout.addWidget(self.spend_reason_input)
        layout.addWidget(submit_btn)
        layout.addWidget(back_btn)

    def handle_income_submit(self):
        raw = self.income_amount_input.text().strip()
        if not raw:
            self.income_amount_input.setFocus()
            return
        try:
            normalized = raw.replace(",", "").replace("$", "")
            amount = float(normalized)
        except Exception:
            self.income_amount_input.setFocus()
            return

        source = self.income_source_input.text().strip() or "Unknown"

        self.incomes.append((amount, source))
        self.total_money += amount
        self.money_value.setText(format_money(self.total_money))
        self.income_card.add_entry(f"{format_money(amount)} — {source}")

        self.income_amount_input.clear()
        self.income_source_input.clear()
        self.animate_to_page(self.page_dashboard)

    def handle_spend_submit(self):

    
        raw = self.spend_amount_input.text().strip()
        if not raw:
            self.spend_amount_input.setFocus()
            return
        try:
            normalized = raw.replace(",", "").replace("$", "")
            amount = float(normalized)
        except Exception:
            self.spend_amount_input.setFocus()
            return

        reason = self.spend_reason_input.text().strip() or "Unknown"

        self.spendings.append((amount, reason))
        self.total_money -= amount
        self.money_value.setText(format_money(self.total_money))
        self.spend_card.add_entry(f"{format_money(amount)} — {reason}")

        self.spend_amount_input.clear()
        self.spend_reason_input.clear()
        self.animate_to_page(self.page_dashboard)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

