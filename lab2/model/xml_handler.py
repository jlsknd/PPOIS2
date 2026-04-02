import xml.dom.minidom as minidom
from xml.sax import handler, parse
from typing import List
from .product import Product


class XMLHandler(handler.ContentHandler):
    def __init__(self):
        self.products = [] #храним прочитанные 
        self.current_product = None #текущий товар
        self.current_element = "" #имя текущего элемента
        self.current_text = "" #текст внутри элемента
    
    def startElement(self, name, attrs):
        self.current_element = name
        if name == "product":
            self.current_product = Product()   #создаем новый товар
            product_id = attrs.get("id", "") #получили атрибут
            if product_id:
                self.current_product.id = int(product_id)
        self.current_text = "" #сбрасываем текст
    
    def characters(self, content): #внутри тега
        if content.strip():  #если текст не пустой
            self.current_text += content   #добавляем к текущему
    
    def endElement(self, name): #закрытие тега
        if name == "product":   
            self.products.append(self.current_product) #сохраняем товар
        elif name == "name":
            self.current_product.name = self.current_text
        elif name == "manufacturer":
            self.current_product.manufacturer = self.current_text
        elif name == "unp":
            self.current_product.unp = self.current_text
        elif name == "quantity":
            try:
                self.current_product.quantity = int(self.current_text)
            except ValueError:
                self.current_product.quantity = 0
        elif name == "address":
            self.current_product.address = self.current_text


def write_xml(products: List[Product], filename: str):
    doc = minidom.Document()   #создали док
    root = doc.createElement("products")   #корневой элемент
    doc.appendChild(root)   #добавили корень в документ
    
    for product in products:
        product_elem = doc.createElement("product") #создаем элемент продукт
        if product.id:
            product_elem.setAttribute("id", str(product.id)) #добавляем атрибут
        
        name_elem = doc.createElement("name")  #так же  нейм и тд
        name_elem.appendChild(doc.createTextNode(product.name))
        product_elem.appendChild(name_elem)
        
        manufacturer_elem = doc.createElement("manufacturer")
        manufacturer_elem.appendChild(doc.createTextNode(product.manufacturer))
        product_elem.appendChild(manufacturer_elem)
        
        unp_elem = doc.createElement("unp")
        unp_elem.appendChild(doc.createTextNode(product.unp))
        product_elem.appendChild(unp_elem)
        
        quantity_elem = doc.createElement("quantity")
        quantity_elem.appendChild(doc.createTextNode(str(product.quantity)))
        product_elem.appendChild(quantity_elem)
        
        address_elem = doc.createElement("address")
        address_elem.appendChild(doc.createTextNode(product.address))
        product_elem.appendChild(address_elem)
        
        root.appendChild(product_elem)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(doc.toprettyxml(indent="  ")) #сохраняем со всеми отступами


def read_xml(filename: str) -> List[Product]:
    handler = XMLHandler() #создаем обработчик
    parse(filename, handler)  #парсим файл методами обработчика
    return handler.products   #возвращаем список товаров
    