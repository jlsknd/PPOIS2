from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QPushButton, QMessageBox, QLabel
)
from PyQt5.QtCore import Qt


class AddDialog(QDialog):
    """Диалог добавления товара"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.setWindowTitle("Добавление товара")
        self.setMinimumWidth(500) #минимальная ширина
        self.setModal(True) #модальное окно
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit() #поле для названия
        self.manufacturer_edit = QLineEdit() #производитель
        self.unp_edit = QLineEdit()    #унп
        self.quantity_spin = QSpinBox() #количество
        self.quantity_spin.setRange(0, 999999)   #диапазон допутстимый
        self.quantity_spin.setValue(0)
        self.address_edit = QLineEdit() #адрес
        
        form_layout.addRow("Название товара:*", self.name_edit)
        form_layout.addRow("Название производителя:*", self.manufacturer_edit)
        form_layout.addRow("УНП производителя:*", self.unp_edit)
        form_layout.addRow("Количество на складе:*", self.quantity_spin)
        form_layout.addRow("Адрес склада:*", self.address_edit)
        
        layout.addLayout(form_layout)
        
        # информация об обязательных полях
        info_label = QLabel("* - обязательные поля")
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info_label)
        
        # кнопки
        button_layout = QHBoxLayout() #они горизонтальные 
        button_layout.addStretch()
        
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_product) #сигнал
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def add_product(self):
        # Проверка полей
        if not self.name_edit.text():
            QMessageBox.warning(self, "Ошибка", "Введите название товара")
            return
        
        if not self.manufacturer_edit.text():
            QMessageBox.warning(self, "Ошибка", "Введите название производителя")
            return
        
        if not self.unp_edit.text():
            QMessageBox.warning(self, "Ошибка", "Введите УНП производителя")
            return
        
        if not self.address_edit.text():
            QMessageBox.warning(self, "Ошибка", "Введите адрес склада")
            return
        
        # вызов контроллера
        self.controller.add_product(
            name=self.name_edit.text(),
            manufacturer=self.manufacturer_edit.text(),
            unp=self.unp_edit.text(),
            quantity=self.quantity_spin.value(),
            address=self.address_edit.text()
        )
        
        self.accept()