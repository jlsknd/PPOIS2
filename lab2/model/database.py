import sqlite3          #нужно для работы с sql
from typing import List, Tuple
from .product import Product


class Database:
    def __init__(self, db_path: str = "data/warehouse.db"):
        self.db_path = db_path     #путь к бд
        self._init_db()            #создание при отсутствии таблицы
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)  #подключаемся к бд
        cursor = conn.cursor()        #создаем курсор для выполнения скьюэль
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
        conn.commit()  #сохранили соединение и закрыли
        conn.close()
    
    def add_product(self, product: Product) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, manufacturer, unp, quantity, address)
            VALUES (?, ?, ?, ?, ?)
        ''', (product.name, product.manufacturer, product.unp, 
              product.quantity, product.address))
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id   #вставляем новый товар и получаем сгенерированный айди
    
    def get_all_products(self, offset: int = 0, limit: int = 10) -> Tuple[List[Product], int]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        #общее количество записей
        cursor.execute("SELECT COUNT(*) FROM products")
        total_count = cursor.fetchone()[0]
        #записи с текущей страницы: офсет - с какой записи начать, лимит - сколько взять
        cursor.execute('''
            SELECT id, name, manufacturer, unp, quantity, address
            FROM products
            ORDER BY id
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        products = []
        for row in cursor.fetchall():  #список всех строк
            products.append(Product(
                id=row[0], name=row[1], manufacturer=row[2],
                unp=row[3], quantity=row[4], address=row[5]
            ))
        
        conn.close()
        return products, total_count  #список и кол-во
    
    def search_products(self, criteria: dict, offset: int = 0, limit: int = 10) -> Tuple[List[Product], int]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if 'name' in criteria and criteria['name']:
            conditions.append("name LIKE ?") #лайк это поиск по части
            params.append(f"%{criteria['name']}%") #а это поиск в любом месте
        if 'manufacturer' in criteria and criteria['manufacturer']:
            conditions.append("manufacturer LIKE ?")
            params.append(f"%{criteria['manufacturer']}%")
        if 'unp' in criteria and criteria['unp']:
            conditions.append("unp LIKE ?")
            params.append(f"%{criteria['unp']}%")
        if 'quantity' in criteria and criteria['quantity'] is not None:
            conditions.append("quantity = ?")
            params.append(criteria['quantity'])
        if 'address' in criteria and criteria['address']:
            conditions.append("address LIKE ?")
            params.append(f"%{criteria['address']}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1" #собирает запрос
        
        cursor.execute(f"SELECT COUNT(*) FROM products WHERE {where_clause}", params)
        total_count = cursor.fetchone()[0]
        
        cursor.execute(f'''
            SELECT id, name, manufacturer, unp, quantity, address
            FROM products
            WHERE {where_clause}
            ORDER BY id
            LIMIT ? OFFSET ?
        ''', params + [limit, offset])
        
        products = []
        for row in cursor.fetchall():
            products.append(Product(             #каждая строка это кортеж
                id=row[0], 
                name=row[1],
                manufacturer=row[2],
                unp=row[3],
                quantity=row[4], 
                address=row[5]
            ))
        
        conn.close()
        return products, total_count
    
    def delete_products(self, criteria: dict) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        conditions = []    #список для условий
        params = []        #список для значений
        
        if 'name' in criteria and criteria['name']:
            conditions.append("name LIKE ?")
            params.append(f"%{criteria['name']}%")
        if 'manufacturer' in criteria and criteria['manufacturer']:
            conditions.append("manufacturer LIKE ?")
            params.append(f"%{criteria['manufacturer']}%")
        if 'unp' in criteria and criteria['unp']:
            conditions.append("unp LIKE ?")
            params.append(f"%{criteria['unp']}%")
        if 'quantity' in criteria and criteria['quantity'] is not None:
            conditions.append("quantity = ?")
            params.append(criteria['quantity'])
        if 'address' in criteria and criteria['address']:
            conditions.append("address LIKE ?")
            params.append(f"%{criteria['address']}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=0"  #чтоб случайно не удалить все 
        
        cursor.execute(f"DELETE FROM products WHERE {where_clause}", params)  #собрали запрос
        deleted_count = cursor.rowcount #сколько записей было удалено
        conn.commit()
        conn.close()
        
        return deleted_count 
    
    def clear_all(self):
        """Очистка всех записей"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products")
        conn.commit()
        conn.close()
    
    def reset_sequence(self):
        """Сброс автоинкремента"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='products'")
        conn.commit()
        conn.close()
    
    def add_multiple(self, products: List[Product]):
        """Добавление нескольких товаров (сохраняет существующие ID)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for product in products:
            # Если есть ID, вставляем с указанным ID
            if product.id:
                cursor.execute('''
                    INSERT INTO products (id, name, manufacturer, unp, quantity, address)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (product.id, product.name, product.manufacturer, product.unp, 
                      product.quantity, product.address))
            else:
                cursor.execute('''
                    INSERT INTO products (name, manufacturer, unp, quantity, address)
                    VALUES (?, ?, ?, ?, ?)
                ''', (product.name, product.manufacturer, product.unp, 
                      product.quantity, product.address))
        
        conn.commit()
        conn.close()
    
    def replace_all(self, products: List[Product]):
        """Замена всех записей (очищает и добавляет новые с ID начиная с 1)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Очищаем таблицу
        cursor.execute("DELETE FROM products")
        # Сбрасываем автоинкремент
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='products'")
        
        # Добавляем новые записи (без ID, пусть БД сама назначает)
        for product in products:
            cursor.execute('''
                INSERT INTO products (name, manufacturer, unp, quantity, address)
                VALUES (?, ?, ?, ?, ?)
            ''', (product.name, product.manufacturer, product.unp, 
                  product.quantity, product.address))
        
        conn.commit()
        conn.close()