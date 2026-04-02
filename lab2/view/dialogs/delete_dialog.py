from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLineEdit, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QGroupBox, QMessageBox, QHeaderView, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt, pyqtSlot


class DeleteDialog(QDialog):
    """Диалог удаления товаров с тремя вариантами поиска"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.found_products = []
        
        self.setWindowTitle("Удаление товаров")
        self.setGeometry(200, 200, 1000, 600)
        self.setModal(True)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Создаем вкладки для трех вариантов поиска
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
        
        # Таблица найденных записей
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(6)
        self.result_table.setHorizontalHeaderLabels(['ID', 'Название', 'Производитель', 'УНП', 'Количество', 'Адрес'])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.result_table)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.delete_btn = QPushButton(" Удалить найденные")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_products)
        self.delete_btn.setStyleSheet("QPushButton { background-color: #ff4444; color: white; }")
        
        close_btn = QPushButton(" Закрыть")
        close_btn.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
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
        search_btn = QPushButton("🔍 Найти для удаления")
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
        search_btn = QPushButton("🔍 Найти для удаления")
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
        search_btn = QPushButton(" Найти для удаления")
        search_btn.clicked.connect(self.search_tab3)
        layout.addWidget(search_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def get_criteria_tab1(self):
        """Получение критериев из первой вкладки"""
        criteria = {}
        
        if self.name_edit.text():
            criteria['name'] = self.name_edit.text()
        
        if self.quantity_spin.value() > 0:
            criteria['quantity'] = self.quantity_spin.value()
        
        return criteria
    
    def get_criteria_tab2(self):
        """Получение критериев из второй вкладки"""
        criteria = {}
        
        if self.manufacturer_edit.text():
            criteria['manufacturer'] = self.manufacturer_edit.text()
        
        if self.unp_edit.text():
            criteria['unp'] = self.unp_edit.text()
        
        return criteria
    
    def get_criteria_tab3(self):
        """Получение критериев из третьей вкладки"""
        criteria = {}
        
        if self.address_edit.text():
            criteria['address'] = self.address_edit.text()
        
        return criteria
    
    @pyqtSlot()
    def search_tab1(self):
        """Поиск по названию товара или количеству"""
        criteria = self.get_criteria_tab1()
        
        if not criteria:
            QMessageBox.warning(self, "Внимание", "Введите хотя бы один критерий поиска")
            return
        
        self.perform_search(criteria)
    
    @pyqtSlot()
    def search_tab2(self):
        """Поиск по названию производителя или УНП"""
        criteria = self.get_criteria_tab2()
        
        if not criteria:
            QMessageBox.warning(self, "Внимание", "Введите хотя бы один критерий поиска")
            return
        
        self.perform_search(criteria)
    
    @pyqtSlot()
    def search_tab3(self):
        """Поиск по адресу склада"""
        criteria = self.get_criteria_tab3()
        
        if not criteria:
            QMessageBox.warning(self, "Внимание", "Введите адрес склада")
            return
        
        self.perform_search(criteria)
    
    def perform_search(self, criteria):
        """Выполнение поиска"""
        products, total = self.controller.search_products(criteria, 0, 10000)
        self.found_products = products
        self.current_criteria = criteria
        
        # Отображаем результаты
        self.display_results(products)
        
        if total > 0:
            self.delete_btn.setEnabled(True)
            self.delete_btn.setText(f"🗑 Удалить {total} записей")
            QMessageBox.information(self, "Найдено записей", f"Найдено {total} записей для удаления")
        else:
            self.delete_btn.setEnabled(False)
            self.delete_btn.setText("🗑 Удалить найденные")
            QMessageBox.information(self, "Не найдено", "Записи по указанным критериям не найдены")
    
    def display_results(self, products):
        """Отображение найденных записей"""
        self.result_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.result_table.setItem(row, 0, QTableWidgetItem(str(product.get('id', ''))))
            self.result_table.setItem(row, 1, QTableWidgetItem(product.get('name', '')))
            self.result_table.setItem(row, 2, QTableWidgetItem(product.get('manufacturer', '')))
            self.result_table.setItem(row, 3, QTableWidgetItem(product.get('unp', '')))
            self.result_table.setItem(row, 4, QTableWidgetItem(str(product.get('quantity', 0))))
            self.result_table.setItem(row, 5, QTableWidgetItem(product.get('address', '')))
    
    @pyqtSlot()
    def delete_products(self):
        """Удаление найденных записей"""
        if not self.found_products:
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы действительно хотите удалить {len(self.found_products)} записей?\n\n"
            f"Это действие нельзя отменить!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                deleted_count = self.controller.delete_products(self.current_criteria)
                QMessageBox.information(
                    self, "Удаление завершено", 
                    f"Удалено записей: {deleted_count}\n\n"
                    f"Нажмите ОК для обновления главного окна."
                )
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")