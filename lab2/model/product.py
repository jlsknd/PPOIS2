from dataclasses import dataclass   #для сокращения объема кода ипортируем декоратор
from typing import Optional


@dataclass  
class Product:
    """Сущность товара"""
    id: Optional[int] = None
    name: str = "" #название товара
    manufacturer: str = "" #название производителя
    unp: str = "" #его унп
    quantity: int = 0  #количество
    address: str = "" #адрес
    
    def to_dict(self) -> dict:   #преобразовываем объект в словарь для передачи в view
        return {                 #чтоб view не знала об этом классе
            'id': self.id,
            'name': self.name,
            'manufacturer': self.manufacturer,
            'unp': self.unp,
            'quantity': self.quantity,
            'address': self.address
        }
    
    @classmethod
    def from_dict(cls, data: dict):    #создает объект класса продуктов из словаря и используется при загрузке из хмл или бд
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            manufacturer=data.get('manufacturer', ''),
            unp=data.get('unp', ''),
            quantity=data.get('quantity', 0),
            address=data.get('address', '')
        )