import sys
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QComboBox, QCheckBox
)
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt
from kite_api import get_login_url, generate_session, place_order, get_position_pnl


class OrderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zerodha Order App")
        self.setMinimumWidth(300)

        self.layout = QVBoxLayout()

        self.dark_mode_checkbox = QCheckBox("Dark Mode")
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        self.layout.addWidget(self.dark_mode_checkbox)

        self.token_label = QLabel("Request Token:")
        self.token_input = QLineEdit()
        self.login_button = QPushButton("1. Open Login Page")
        self.session_button = QPushButton("2. Generate Session")

        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Symbol (e.g., INFY)")
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Quantity")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price (for LIMIT orders)")

        self.exchange_label = QLabel("Exchange:")
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItems(["NSE", "NFO"])

        self.order_type_label = QLabel("Order Type:")
        self.order_type = QComboBox()
        self.order_type.addItems(["LIMIT", "MARKET", "SL", "SL-M"])

        self.transaction_type_label = QLabel("Transaction Type:")
        self.transaction_type = QComboBox()
        self.transaction_type.addItems(["BUY", "SELL"])

        self.pl_label = QLabel("Profit / Loss:")
        self.pl_value = QLabel("0")
        self.pl_value.setAlignment(Qt.AlignCenter)

        self.place_button = QPushButton("Place Order")
        self.pl_check_button = QPushButton("Check Existing P&L")

        for widget in [
            self.login_button,
            self.token_label, self.token_input,
            self.session_button,
            self.symbol_input, self.qty_input, self.price_input,
            self.exchange_label, self.exchange_combo,
            self.order_type_label, self.order_type,
            self.transaction_type_label, self.transaction_type,
            self.place_button, self.pl_check_button,
            self.pl_label, self.pl_value
        ]:
            self.layout.addWidget(widget)

        self.setLayout(self.layout)

        self.login_button.clicked.connect(self.open_login)
        self.session_button.clicked.connect(self.create_session)
        self.place_button.clicked.connect(self.place_order)
        self.pl_check_button.clicked.connect(self.check_existing_pnl)

    def toggle_dark_mode(self):
        if self.dark_mode_checkbox.isChecked():
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            self.setPalette(palette)
        else:
            self.setPalette(self.style().standardPalette())

    def open_login(self):
        url = get_login_url()
        webbrowser.open(url)

    def create_session(self):
        token = self.token_input.text()
        try:
            access = generate_session(token)
            QMessageBox.information(self, "Success", f"Access Token Set:\n{access}")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def place_order(self):
        symbol = self.symbol_input.text().upper()
        quantity = self.qty_input.text()
        price = self.price_input.text()
        exchange = self.exchange_combo.currentText()
        order_type = self.order_type.currentText()
        transaction_type = self.transaction_type.currentText()

        if not symbol or not quantity:
            QMessageBox.warning(self, "Input Error", "Symbol and Quantity are required.")
            return

        if order_type == "LIMIT" and not price:
            QMessageBox.warning(self, "Input Error", "Price is required for LIMIT orders.")
            return

        try:
            order_id, pl = place_order(
                symbol=symbol,
                quantity=quantity,
                price=price,
                exchange=exchange,
                order_type=order_type,
                transaction_type=transaction_type
            )
            self.show_profit_loss(pl)
            QMessageBox.information(self, "Order Placed", f"Order ID: {order_id}")
        except Exception as e:
            QMessageBox.critical(self, "Order Failed", str(e))

    def show_profit_loss(self, pl):
        try:
            pl = float(pl)
            if pl >= 0:
                self.pl_value.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.pl_value.setStyleSheet("color: red; font-weight: bold;")
            self.pl_value.setText(f"{pl:.2f}")
        except:
            self.pl_value.setText("0")
            self.pl_value.setStyleSheet("color: black;")

    def check_existing_pnl(self):
        symbol = self.symbol_input.text().upper()
        exchange = self.exchange_combo.currentText()
        try:
            pnl = get_position_pnl(symbol, exchange)
            self.show_profit_loss(pnl)
            QMessageBox.information(self, "P&L Info", f"{symbol} Unrealized P&L: {pnl:.2f}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not fetch P&L: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OrderApp()
    window.show()
    sys.exit(app.exec_())
