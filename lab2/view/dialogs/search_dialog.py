from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
    QHeaderView,
    QTabWidget,
    QWidget,
)
from PyQt5.QtCore import Qt, pyqtSlot


class SearchDialog(QDialog):
    """Диалог поиска товаров с тремя вариантами поиска"""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_offset = 0
        self.current_limit = 10
        self.current_criteria = {}
        self.total_pages = 1
        self.current_page = 1

        self.setWindowTitle("Поиск товаров")
        self.setGeometry(200, 200, 1000, 600)
        self.setModal(True)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # создаем вкладки для трех вариантов поиска
        self.tab_widget = QTabWidget()

        #  1: По названию товара или количеству
        self.tab1 = self.create_tab1()
        self.tab_widget.addTab(self.tab1, "По названию товара или количеству")

        #  2: По названию производителя или УНП
        self.tab2 = self.create_tab2()
        self.tab_widget.addTab(self.tab2, "По производителю или УНП")

        #  3: По адресу склада
        self.tab3 = self.create_tab3()
        self.tab_widget.addTab(self.tab3, "По адресу склада")

        layout.addWidget(self.tab_widget)

        # Таблица результатов
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(6)
        self.result_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Производитель", "УНП", "Количество", "Адрес"]
        )
        self.result_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.result_table)

        # Пагинация
        pagination_layout = QHBoxLayout()

        self.btn_prev = QPushButton("<< Предыдущая")
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next = QPushButton("Следующая >>")
        self.btn_next.clicked.connect(self.next_page)

        self.lbl_page = QLabel("Страница: 1 / 1")
        self.lbl_total = QLabel("Всего записей: 0")

        pagination_layout.addWidget(self.btn_prev)
        pagination_layout.addWidget(self.lbl_page)
        pagination_layout.addWidget(self.btn_next)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.lbl_total)

        layout.addLayout(pagination_layout)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def create_tab1(self):
        """Вкладка: По названию товара или количеству на складе"""
        widget = QWidget()
        layout = QVBoxLayout()

        # По названию товара
        group_name = QGroupBox("Поиск по названию товара")
        name_layout = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название товара...")
        name_layout.addWidget(self.name_edit)
        group_name.setLayout(name_layout)
        layout.addWidget(group_name)

        # По количеству
        group_quantity = QGroupBox("Поиск по количеству на складе")
        quantity_layout = QHBoxLayout()
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(0, 999999)
        self.quantity_spin.setValue(0)
        self.quantity_spin.setSpecialValueText("Не выбрано")
        quantity_layout.addWidget(self.quantity_spin)
        group_quantity.setLayout(quantity_layout)
        layout.addWidget(group_quantity)

        # Кнопка поиска
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.search_tab1)
        layout.addWidget(search_btn)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_tab2(self):
        """Вкладка: По названию производителя или УНП"""
        widget = QWidget()
        layout = QVBoxLayout()

        # По названию производителя
        group_manufacturer = QGroupBox("Поиск по названию производителя")
        manufacturer_layout = QHBoxLayout()
        self.manufacturer_edit = QLineEdit()
        self.manufacturer_edit.setPlaceholderText("Введите название производителя...")
        manufacturer_layout.addWidget(self.manufacturer_edit)
        group_manufacturer.setLayout(manufacturer_layout)
        layout.addWidget(group_manufacturer)

        # По УНП
        group_unp = QGroupBox("Поиск по УНП производителя")
        unp_layout = QHBoxLayout()
        self.unp_edit = QLineEdit()
        self.unp_edit.setPlaceholderText("Введите УНП производителя...")
        unp_layout.addWidget(self.unp_edit)
        group_unp.setLayout(unp_layout)
        layout.addWidget(group_unp)

        # Кнопка поиска
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.search_tab2)
        layout.addWidget(search_btn)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_tab3(self):
        """Вкладка: По адресу склада"""
        widget = QWidget()
        layout = QVBoxLayout()

        # По адресу
        group_address = QGroupBox("Поиск по адресу склада")
        address_layout = QHBoxLayout()
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Введите адрес склада...")
        address_layout.addWidget(self.address_edit)
        group_address.setLayout(address_layout)
        layout.addWidget(group_address)

        # Кнопка поиска
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.search_tab3)
        layout.addWidget(search_btn)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    @pyqtSlot()
    def search_tab1(self):
        """Поиск по названию товара или количеству"""
        criteria = {}

        if self.name_edit.text():
            criteria["name"] = self.name_edit.text()

        if self.quantity_spin.value() > 0:
            criteria["quantity"] = self.quantity_spin.value()

        if not criteria:
            QMessageBox.warning(
                self, "Внимание", "Введите хотя бы один критерий поиска"
            )
            return

        self.current_criteria = criteria
        self.current_offset = 0
        self.current_page = 1
        self.perform_search()

    @pyqtSlot()
    def search_tab2(self):
        """Поиск по названию производителя или УНП"""
        criteria = {}

        if self.manufacturer_edit.text():
            criteria["manufacturer"] = self.manufacturer_edit.text()

        if self.unp_edit.text():
            criteria["unp"] = self.unp_edit.text()

        if not criteria:
            QMessageBox.warning(
                self, "Внимание", "Введите хотя бы один критерий поиска"
            )
            return

        self.current_criteria = criteria
        self.current_offset = 0
        self.current_page = 1
        self.perform_search()

    @pyqtSlot()
    def search_tab3(self):
        """Поиск по адресу склада"""
        if not self.address_edit.text():
            QMessageBox.warning(self, "Внимание", "Введите адрес склада")
            return

        self.current_criteria = {"address": self.address_edit.text()}
        self.current_offset = 0
        self.current_page = 1
        self.perform_search()

    def perform_search(self):
        products, total = self.controller.search_products(
            self.current_criteria, self.current_offset, self.current_limit
        )

        self.display_results(products)
        self.update_pagination(total)

    def display_results(self, products):
        self.result_table.setRowCount(len(products))

        for row, product in enumerate(products):
            self.result_table.setItem(
                row, 0, QTableWidgetItem(str(product.get("id", "")))
            )
            self.result_table.setItem(row, 1, QTableWidgetItem(product.get("name", "")))
            self.result_table.setItem(
                row, 2, QTableWidgetItem(product.get("manufacturer", ""))
            )
            self.result_table.setItem(row, 3, QTableWidgetItem(product.get("unp", "")))
            self.result_table.setItem(
                row, 4, QTableWidgetItem(str(product.get("quantity", 0)))
            )
            self.result_table.setItem(
                row, 5, QTableWidgetItem(product.get("address", ""))
            )

    def update_pagination(self, total):
        self.total_pages = max(
            1, (total + self.current_limit - 1) // self.current_limit
        )
        self.lbl_page.setText(f"Страница: {self.current_page} / {self.total_pages}")
        self.lbl_total.setText(f"Всего записей: {total}")

        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < self.total_pages)

    @pyqtSlot()
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.current_offset -= self.current_limit
            self.perform_search()

    @pyqtSlot()
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.current_offset += self.current_limit
            self.perform_search()
