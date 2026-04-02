from typing import List, Tuple, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal
from model.product import Product
from model.database import Database


class Controller(QObject):
    """Контроллер с сигналами для уведомления View"""
    
    data_changed = pyqtSignal()   #сигнал об изменении данных
    products_loaded = pyqtSignal(list, int)  
    
    def __init__(self):
        super().__init__()
        self.db = Database() #создаем экземпляр базы данных
    
    def add_product(self, name: str, manufacturer: str, unp: str, 
                    quantity: int, address: str) -> int:
        product = Product(  #создание объекта
            name=name,
            manufacturer=manufacturer,
            unp=unp,
            quantity=quantity,
            address=address
        )
        result = self.db.add_product(product) #сохранение в бд
        self.data_changed.emit() #уведомление интерфейса об изменениях
        return result
    
    def get_products_page(self, offset: int = 0, limit: int = 10) -> Tuple[List[Dict], int]:
        products, total = self.db.get_all_products(offset, limit) #получаем обхекты из бд
        products_dict = [p.to_dict() for p in products] #преобразуем в словари
        return products_dict, total
    
    def search_products(self, criteria: Dict[str, Any], offset: int = 0,  
                        limit: int = 10) -> Tuple[List[Dict], int]:
        products, total = self.db.search_products(criteria, offset, limit) #вызываем модель
        products_dict = [p.to_dict() for p in products] #преобразовываем объекты в словари
        return products_dict, total  #вовзвращаем в интерфейс только словари
    
    def delete_products(self, criteria: Dict[str, Any]) -> int:
        result = self.db.delete_products(criteria) #вызов модели
        self.data_changed.emit() #уведомление об изменении
        return result
    
    def clear_all(self):
        """Очистка всех записей"""
        self.db.clear_all()  #просто очищаем бд
        self.data_changed.emit()
    
    def add_multiple(self, products_data: List[Dict]):
        """Добавление нескольких товаров (добавляет к существующим)"""
        products = [Product.from_dict(data) for data in products_data] #объекты в словари
        self.db.add_multiple(products) #вствляет все товары в бд сохраняя уже имеющиеся
        self.data_changed.emit() #уведомление об изменении
    
    def replace_all(self, products_data: List[Dict]):
        """Замена всех товаров (очищает и добавляет новые с ID начиная с 1)"""
        products = [Product.from_dict(data) for data in products_data] #словари -> объекты
        # сброс ID, чтобы БД назначила новые
        for product in products:
            product.id = None
        self.db.replace_all(products) #замена
        self.data_changed.emit() #увдеомление
    
    def get_all_products_for_export(self) -> List[Dict]:
        products, _ = self.db.get_all_products(0, 10000)
        return [p.to_dict() for p in products] #товары в словари
    
    # XML методы
    def load_from_xml(self, filename: str) -> int:
        """Загрузка из XML файла (заменяет текущие данные)"""
        from model.xml_handler import read_xml
        products = read_xml(filename) #читаем
        products_data = [p.to_dict() for p in products] #объекты в словари
        self.replace_all(products_data) #замена 
        return len(products_data) #вернули кол-во записей
    
    def save_to_xml(self, filename: str) -> int:
        """Сохранение в XML файл"""
        from model.xml_handler import write_xml
        from model.product import Product
        products_data = self.get_all_products_for_export()  #берем все данные 
        products = [Product.from_dict(data) for data in products_data] #словари в объекты
        write_xml(products, filename) #файл с форматированием
        return len(products_data) #возврат кол-ва сохраненных записей
    
    # Методы для работы с БД файлом
    def backup_to_db(self, filename: str) -> int:
        """Сохранить текущие данные в указанный файл БД"""
        import sqlite3
        
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                manufacturer TEXT NOT NULL,
                unp TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                address TEXT NOT NULL
            )
        ''')
        
        products_data = self.get_all_products_for_export()
        #вставка данных в новый файл
        for product in products_data:
            cursor.execute('''
                INSERT INTO products (name, manufacturer, unp, quantity, address)
                VALUES (?, ?, ?, ?, ?)
            ''', (product['name'], product['manufacturer'], product['unp'],
                  product['quantity'], product['address']))
        
        conn.commit()
        conn.close()
        return len(products_data) #кол-во созхраненных записей
    
    def load_from_db(self, filename: str) -> int:
        """Загрузить данные из указанного файла БД (заменяет текущие данные)"""
        import sqlite3
        from model.product import Product
        
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        
        # проверяем существование таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        if not cursor.fetchone():
            conn.close()
            return 0
        
        cursor.execute('''
            SELECT name, manufacturer, unp, quantity, address
            FROM products
        ''')
        #создаем объекты
        products = []
        for row in cursor.fetchall():
            product = Product(
                name=row[0],
                manufacturer=row[1],
                unp=row[2],
                quantity=row[3],
                address=row[4]
            )
            products.append(product)
        
        conn.close()
        #замена текущих данных
        products_data = [p.to_dict() for p in products]  
        self.replace_all(products_data)
        return len(products_data)
    
    def append_from_xml(self, filename: str) -> int:
        """Добавить данные из XML файла к существующим"""
        from model.xml_handler import read_xml
        products = read_xml(filename) #читаем хмл
        products_data = [p.to_dict() for p in products] #в словари
        self.add_multiple(products_data) #добавление к имеющимся данным
        return len(products_data)
    
    def append_from_db(self, filename: str) -> int:
        """Добавить данные из БД файла к существующим"""
        import sqlite3
        from model.product import Product
        
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        if not cursor.fetchone():
            conn.close()
            return 0
        
        cursor.execute('''
            SELECT name, manufacturer, unp, quantity, address
            FROM products
        ''')
        
        products = []
        for row in cursor.fetchall():
            product = Product(
                name=row[0],
                manufacturer=row[1],
                unp=row[2],
                quantity=row[3],
                address=row[4]
            )
            products.append(product)
        
        conn.close()
        
        products_data = [p.to_dict() for p in products]
        self.add_multiple(products_data) #добавляем без удаления имеющихся
        return len(products_data)