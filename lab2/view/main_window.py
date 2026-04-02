from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableView, QHeaderView, QPushButton, QLabel, 
    QSpinBox, QMessageBox, QFileDialog, QToolBar, QAction,
    QTabWidget, QTreeWidget, QTreeWidgetItem, QApplication, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSlot, QAbstractTableModel, QModelIndex, pyqtSignal
from PyQt5.QtGui import QFont
from typing import List, Dict


class ProductsTableModel(QAbstractTableModel):
    """Модель таблицы для отображения товаров"""
    
    _headers = ['ID', 'Название', 'Производитель', 'УНП', 'Количество', 'Адрес']
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._products = []
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._products) #кол-во строк
    
    def columnCount(self, parent=QModelIndex()):
        return len(self._headers) #кол-во столбцов
    
    def data(self, index, role=Qt.DisplayRole): #возвращает данные для ячейки
        if not index.isValid(): 
            return None
        
        product = self._products[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole: #если надо отобразить текст
            if col == 0:
                return str(product.get('id', ''))
            elif col == 1:
                return product.get('name', '')
            elif col == 2:
                return product.get('manufacturer', '')  #значене о номеру столбца
            elif col == 3:
                return product.get('unp', '')
            elif col == 4:
                return str(product.get('quantity', 0))
            elif col == 5:
                return product.get('address', '')
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section] #заголовки столбцов
        return None
    
    def set_products(self, products: List[Dict]): #обновляет данные в таблице
        self.beginResetModel() #начало
        self._products = products #новые данные
        self.endResetModel() #запрос обновления


class ProductsTreeWidget(QTreeWidget):
    """Древовидное представление товаров"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Структура товаров")
        self.setColumnCount(2)
        self.setHeaderLabels(["Поле", "Значение"])
        self.header().setStretchLastSection(True)
    
    def set_products(self, products: List[Dict]):
        self.clear() #очищаем дерево
        
        for product in products: #создаем корневой элемент
            product_id = f"Товар #{product.get('id', 'новый')}"
            product_item = QTreeWidgetItem([product_id, ""])
            product_item.setFont(0, QFont("Arial", 10, QFont.Bold))
            self.addTopLevelItem(product_item)
            
            #далее поля - дочерние элементы
            QTreeWidgetItem(product_item, ["Название товара", product.get('name', '')])
            QTreeWidgetItem(product_item, ["Производитель", product.get('manufacturer', '')])
            QTreeWidgetItem(product_item, ["УНП производителя", product.get('unp', '')])
            QTreeWidgetItem(product_item, ["Количество на складе", str(product.get('quantity', 0))])
            QTreeWidgetItem(product_item, ["Адрес склада", product.get('address', '')])
            
            product_item.setExpanded(False) #свернуто по умолчанию


class PaginationWidget(QWidget):
    """Виджет пагинации"""
    
    page_changed = pyqtSignal() #сигнал при смене страницы
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 1
        self.total_pages = 1
        self.total_items = 0
        self.items_per_page = 10
        
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        #кнопки
        self.btn_first = QPushButton("<<")
        self.btn_prev = QPushButton("<")
        self.btn_next = QPushButton(">")
        self.btn_last = QPushButton(">>")
        #подключение сигналов
        self.btn_first.clicked.connect(self.first_page)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_last.clicked.connect(self.last_page)
        
        self.lbl_page = QLabel("Страница: 1 / 1")
        
        layout.addWidget(self.btn_first)
        layout.addWidget(self.btn_prev)
        layout.addWidget(self.lbl_page)
        layout.addWidget(self.btn_next)
        layout.addWidget(self.btn_last)
        layout.addStretch()
        
        layout.addWidget(QLabel("Записей на странице:"))
        #выбор количества записей
        self.spin_items = QSpinBox()
        self.spin_items.setMinimum(1)
        self.spin_items.setMaximum(10000)
        self.spin_items.setValue(10)
        self.spin_items.setSingleStep(1)
        self.spin_items.setToolTip("Введите любое количество записей от 1 до 10000")
        self.spin_items.valueChanged.connect(self.on_items_per_page_changed)
        
        layout.addWidget(self.spin_items)
        
        self.lbl_total = QLabel("Всего: 0 записей")
        layout.addWidget(self.lbl_total)
        
        self.setLayout(layout)
    
    #устанавливает общее количество записей, пересчитывает кол-во страниц
    def set_total(self, total: int):
        self.total_items = total
        self.total_pages = max(1, (total + self.items_per_page - 1) // self.items_per_page)
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        self.update_display()
    
    #обновили текст меток и состояние кнопок
    def update_display(self):
        self.lbl_page.setText(f"Страница: {self.current_page} / {self.total_pages}")
        self.lbl_total.setText(f"Всего: {self.total_items} записей")
        
        self.btn_first.setEnabled(self.current_page > 1)
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < self.total_pages)
        self.btn_last.setEnabled(self.current_page < self.total_pages)
    
    def first_page(self):
        if self.current_page != 1:
            self.current_page = 1
            self.page_changed.emit() #сигнал - главное окно загружает 1ю стр
    
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.page_changed.emit()
    
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.page_changed.emit()
    
    def last_page(self):
        if self.current_page != self.total_pages:
            self.current_page = self.total_pages
            self.page_changed.emit()
    
    def on_items_per_page_changed(self, value): #изменение количества записей на странице
        if value > 0:
            self.items_per_page = value
            self.total_pages = max(1, (self.total_items + self.items_per_page - 1) // self.items_per_page)
            self.current_page = 1
            self.page_changed.emit()
    
    def get_offset(self): #возврат смещения для запроса
        return (self.current_page - 1) * self.items_per_page
    
    def get_limit(self): #возврат количества записей на странице
        return self.items_per_page


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.controller.data_changed.connect(self.on_data_changed)
        
        self.init_ui()
        self.load_page()
    
    def init_ui(self):
        self.setWindowTitle("Складской учёт")  #заголовок приложения
        self.setGeometry(100, 100, 1200, 700)
        
        self.create_menu() #меню
        self.create_toolbar() #панель инструментов
        
        central_widget = QWidget()  
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        self.tab_widget = QTabWidget() #вкладки
        
        self.table_view = QTableView()  #таблица
        self.table_model = ProductsTableModel()
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.tab_widget.addTab(self.table_view, "Табличный вид")
        
        self.tree_widget = ProductsTreeWidget()  #дерево
        self.tab_widget.addTab(self.tree_widget, "Древовидный вид")
        
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tab_widget)
        
        self.pagination = PaginationWidget() #пагинация
        self.pagination.page_changed.connect(self.load_page)
        main_layout.addWidget(self.pagination)
        
        self.statusbar = self.statusBar() #статусбар
        self.statusbar.showMessage("Готов")
    
    def create_menu(self):
        menubar = self.menuBar()
        
        # файл
        file_menu = menubar.addMenu("Файл")
        
        load_xml_action = QAction("Загрузить из XML", self)
        load_xml_action.triggered.connect(self.load_xml)
        file_menu.addAction(load_xml_action)
        
        save_xml_action = QAction("Сохранить в XML", self)
        save_xml_action.triggered.connect(self.save_xml)
        file_menu.addAction(save_xml_action)
        
        file_menu.addSeparator()
        
        load_db_action = QAction("Загрузить из БД", self)
        load_db_action.triggered.connect(self.load_db)
        file_menu.addAction(load_db_action)
        
        save_db_action = QAction("Сохранить в БД", self)
        save_db_action.triggered.connect(self.save_db)
        file_menu.addAction(save_db_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # редактирование
        edit_menu = menubar.addMenu("Редактирование")
        
        add_action = QAction("Добавить запись", self)
        add_action.triggered.connect(self.show_add_dialog)
        edit_menu.addAction(add_action)
        
        search_action = QAction("Поиск", self)
        search_action.triggered.connect(self.show_search_dialog)
        edit_menu.addAction(search_action)
        
        delete_action = QAction("Удалить", self)
        delete_action.triggered.connect(self.show_delete_dialog)
        edit_menu.addAction(delete_action)
        
        # помощь(типо для справки)
        help_menu = menubar.addMenu("Помощь")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        #  операции
        add_action = QAction("Добавить", self)
        add_action.triggered.connect(self.show_add_dialog)
        toolbar.addAction(add_action)
        
        search_action = QAction(" Поиск", self)
        search_action.triggered.connect(self.show_search_dialog)
        toolbar.addAction(search_action)
        
        delete_action = QAction(" Удалить", self)
        delete_action.triggered.connect(self.show_delete_dialog)
        toolbar.addAction(delete_action)
        
        refresh_action = QAction("Сохранить изменения в БД", self)
        refresh_action.triggered.connect(self.load_page)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # работа с XML
        load_xml_action = QAction(" Загрузить XML", self)
        load_xml_action.triggered.connect(self.load_xml)
        toolbar.addAction(load_xml_action)
        
        save_xml_action = QAction(" Сохранить XML", self)
        save_xml_action.triggered.connect(self.save_xml)
        toolbar.addAction(save_xml_action)
        
        toolbar.addSeparator()
        
        # работа с БД
        load_db_action = QAction("Загрузить БД", self)
        load_db_action.triggered.connect(self.load_db)
        toolbar.addAction(load_db_action)
        
        save_db_action = QAction("Сохранить БД", self)
        save_db_action.triggered.connect(self.save_db)
        toolbar.addAction(save_db_action)
    
    def load_page(self):
        offset = self.pagination.get_offset()  #с какой записи начать
        limit = self.pagination.get_limit()  #сколько взять
        
        products, total = self.controller.get_products_page(offset, limit) #получим данные из контроллера
        
        if self.tab_widget.currentIndex() == 0: #отображаем в зависимости от выбранной вкладки
            self.table_model.set_products(products)
        else:
            self.tree_widget.set_products(products)
        
        self.pagination.set_total(total) #обновили пагинацию
        self.statusbar.showMessage(f"Загружено {len(products)} записей. Всего: {total}")
    
    def on_tab_changed(self, index):
        self.load_page() #перезагружает данные для новой вкладки
    
    def on_data_changed(self):   #обновляет отображение при изменении данных
        self.load_page()
    
    @pyqtSlot()
    def show_add_dialog(self):
        from view.dialogs.add_dialog import AddDialog
        dialog = AddDialog(self, self.controller)
        dialog.exec_() #открывает модальное окно и так везле в след слотах
    
    @pyqtSlot()
    def show_search_dialog(self):
        from view.dialogs.search_dialog import SearchDialog
        dialog = SearchDialog(self, self.controller)
        dialog.exec_()
    
    @pyqtSlot()
    def show_delete_dialog(self):
        from view.dialogs.delete_dialog import DeleteDialog
        dialog = DeleteDialog(self, self.controller)
        dialog.exec_()
    
    @pyqtSlot()
    def load_xml(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите XML файл", "", "XML files (*.xml)"
        )
        if filename:
            try:
                count = self.controller.load_from_xml(filename)
                QMessageBox.information(self, "Загрузка", f"Загружено {count} записей из XML")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки: {str(e)}")
    
    @pyqtSlot()
    def save_xml(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить XML файл", "", "XML files (*.xml)"
        )
        if filename:
            try:
                count = self.controller.save_to_xml(filename)
                QMessageBox.information(self, "Сохранение", f"Сохранено {count} записей в XML")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")
    
    @pyqtSlot()
    def load_db(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл базы данных", "", "Database files (*.db *.sqlite)"
        )
        if filename:
            try:
                count = self.controller.load_from_db(filename)
                QMessageBox.information(self, "Загрузка", f"Загружено {count} записей из БД")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки: {str(e)}")
    
    @pyqtSlot()
    def save_db(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить базу данных", "", "Database files (*.db)"
        )
        if filename:
            try:
                count = self.controller.backup_to_db(filename)
                QMessageBox.information(self, "Сохранение", f"Сохранено {count} записей в БД")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")
    
    @pyqtSlot()
    def show_about(self):
        QMessageBox.about(self, "О программе",
                         "Складской учёт\n"
                         "Лабораторная работа №2\n"
                         "ППОИС 4 семестр\n\n"
                         "Функции:\n"
                         "- Добавление, поиск, удаление записей\n"
                         "- Поиск по трем вариантам\n"
                         "- Пагинация с произвольным количеством записей\n"
                         "- Два вида отображения: таблица и дерево\n"
                         "- Импорт/экспорт XML (DOM/SAX)\n"
                         "- Импорт/экспорт SQLite базы данных\n\n"
                         "Разработано с использованием PyQt5")