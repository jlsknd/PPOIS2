import sys
import os
from PyQt5.QtWidgets import QApplication

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controller.controller import Controller
from view.main_window import MainWindow


def create_sample_data(controller):
    """Создание образцов данных для БД - 60 записей"""
    
    manufacturers = [
        ("ООО 'Марвел-Маркет'", "192040812"),
        ("ОДО 'Атлант-Техно'", "190724512"),
        ("ООО 'Техника и Связь'", "191435678"),
        ("ЗАО 'КБС-Бел'", "101254987"),
        ("ООО 'Электронные системы'", "192345678"),
        ("ИП 'Компьютерный мир'", "191876543"),
        ("ООО 'Цифровые технологии'", "190987654"),
        ("ЗАО 'Белорусский компьютерный центр'", "100567890"),
        ("ООО 'Современная техника'", "192123456"),
        ("ИП 'ТехноСервис'", "191234567")
    ]
    
    addresses = [
        "г. Минск, ул. Тимирязева, 65Б, технопарк 'Электрон'",
        "г. Минск, ул. Ольшевского, 22, бизнес-центр 'IT-Парк'",
        "г. Минск, пр-т Партизанский, 150, техноцентр",
        "г. Минск, ул. Промышленная, 12, складской комплекс",
        "г. Минск, ул. Сурганова, 50, логистический центр",
        "г. Минск, ул. Платонова, 45, склад 'Компьютерный'",
        "г. Минск, ул. Куйбышева, 67, технопарк",
        "г. Минск, ул. Калиновского, 120, IT-хаб",
        "г. Минск, ул. Шаранговича, 7, склад 'Алгоритм'",
        "г. Минск, ул. Машиностроителей, 18, техноцентр"
    ]
    
    product_names = [
        "Ноутбук Lenovo ThinkPad E15", "Ноутбук ASUS Vivobook 15", "Ноутбук HP Pavilion 15",
        "Ноутбук Dell XPS 13", "Ноутбук Acer Aspire 7", "Ноутбук MSI Modern 14",
        "Монитор Samsung 24\" Full HD", "Монитор LG 27\" UltraGear", "Монитор Dell P2722H",
        "Монитор AOC 27\"", "Монитор ViewSonic 24\"", "Монитор BenQ 27\"",
        "Клавиатура Logitech MX Keys", "Клавиатура Razer BlackWidow", "Клавиатура Corsair K70",
        "Клавиатура HyperX Alloy", "Клавиатура A4Tech Bloody", "Клавиатура Cougar",
        "Мышь Logitech MX Master 3", "Мышь Razer DeathAdder V2", "Мышь SteelSeries Rival 3",
        "Мышь Corsair Nightsword", "Мышь HyperX Pulsefire", "Мышь A4Tech X7",
        "Принтер HP LaserJet M140", "Принтер Canon PIXMA G3410", "Принтер Brother DCP-L2500",
        "Принтер Epson L3150", "Принтер Kyocera Ecosys", "Принтер Xerox B210",
        "Сканер Canon CanoScan LiDE 400", "Сканер Epson Perfection V39", "Сканер HP ScanJet Pro",
        "Сканер Brother ADS-1200", "Сканер Plustek", "Сканер Fujitsu ScanSnap",
        "Системный блок Acer Nitro 50", "Системный блок Dell OptiPlex 3080", "Системный блок HP EliteDesk",
        "Системный блок Lenovo ThinkCentre", "Системный блок Asus Pro", "Системный блок MSI Trident",
        "Внешний SSD Samsung T7 1TB", "Внешний HDD Seagate 2TB", "Внешний диск WD My Passport 4TB",
        "Внешний SSD Kingston 500GB", "Внешний HDD Toshiba 1TB", "Внешний диск Transcend 2TB",
        "USB-хаб Anker 7-портовый", "USB-хаб Belkin 4-портовый", "USB-хаб Hama 10-портовый",
        "USB-хаб Orico 4-портовый", "USB-хаб A4Tech", "USB-хаб HyperDrive",
        "Наушники Sony WH-1000XM4", "Наушники JBL Tune 710BT", "Наушники HyperX Cloud II",
        "Наушники SteelSeries Arctis", "Наушники Logitech G Pro", "Наушники Razer BlackShark"
    ]
    
    # создаем 60 записей
    for i in range(60):
        manuf_idx = i % len(manufacturers)   
        addr_idx = i % len(addresses)
        name_idx = i % len(product_names)
        quantity = (i * 17) % 100 + 1
        
        controller.add_product(
            name=product_names[name_idx],
            manufacturer=manufacturers[manuf_idx][0],
            unp=manufacturers[manuf_idx][1],
            quantity=quantity,
            address=addresses[addr_idx]
        )


def create_sample_xml_file():
    """Создание XML файла с 50 записями (офисная техника и мебель)"""
    from model.product import Product
    from model.xml_handler import write_xml
    
    os.makedirs("samples", exist_ok=True)
    
    
    xml_manufacturers = [
        ("ООО 'Офисный Мир'", "193456789"),
        ("ЗАО 'Мебель-Стиль'", "102345678"),
        ("ООО 'Бумажные технологии'", "194567890"),
        ("ОДО 'Канцтовары'", "195678901"),
        ("ООО 'Оргтехника'", "196789012"),
        ("ИП 'Презентация'", "197890123"),
        ("ООО 'Склад-Офис'", "198901234"),
        ("ЗАО 'Мета-Систем'", "199012345"),
        ("ООО 'Интерьер-Плюс'", "190123456"),
        ("ИП 'Комфорт-Офис'", "191234567")
    ]
    
    xml_addresses = [
        "г. Минск, ул. Тимирязева, 120, склад 'Офис-Центр'",
        "г. Минск, ул. Притыцкого, 87, логистический хаб",
        "г. Минск, пр-т Дзержинского, 45, складской комплекс 'Офис'",
        "г. Минск, ул. Ленина, 35, бизнес-центр",
        "г. Минск, ул. Сторожевская, 12, склад №5",
        "г. Минск, ул. Мясникова, 28, технопарк",
        "г. Минск, ул. Кальварийская, 43, склад 'Канцелярия'",
        "г. Минск, ул. Богдановича, 90, офисный центр",
        "г. Минск, ул. Революционная, 15, складской корпус",
        "г. Минск, ул. Я. Коласа, 66, логистический терминал"
    ]
    
    xml_product_names = [
        "Офисное кресло Chairman", "Кресло руководителя Метта", "Стул офисный Bureaucrat",
        "Стол компьютерный IKEA", "Стол письменный Hoff", "Стол-трансформер",
        "Шкаф для документов металлический", "Сейф офисный", "Тумба подкатная",
        "Стеллаж архивный", "Полка навесная", "Шкаф для одежды",
        "Лампа настольная светодиодная", "Лампа для чтения", "Светильник офисный",
        "Бумага А4 SvetoCopy 500л", "Бумага А4 Ballet Premium", "Бумага А4 Xerox",
        "Бумага цветная A4", "Бумага для заметок", "Бумага для принтера 80г/м²",
        "Ручка шариковая Pilot", "Ручка гелевая Schneider", "Ручка перьевая",
        "Карандаш механический", "Карандаш чернографитный", "Карандаш цветной",
        "Маркер перманентный", "Маркер для доски", "Хайлайтер текстовыделитель",
        "Папка-регистратор Esselte", "Папка на кольцах", "Папка-скоросшиватель",
        "Папка с зажимом", "Конверт почтовый", "Конверт с окном",
        "Степлер офисный", "Дырокол", "Скобы для степлера",
        "Ножницы канцелярские", "Линейка металлическая", "Ластик",
        "Клей-карандаш", "Клей ПВА", "Скотч прозрачный",
        "Скрепки канцелярские", "Папка уголок", "Файл-вкладыш",
        "Ежедневник недатированный", "Блокнот А5", "Закладки самоклеящиеся"
    ]
    
    # создаём 50 записей 
    products = []
    for i in range(50):
        manuf_idx = i % len(xml_manufacturers)
        addr_idx = i % len(xml_addresses)
        name_idx = i % len(xml_product_names)
        
        product = Product(
            id=None,  # ID будет назначен при загрузке
            name=xml_product_names[name_idx],
            manufacturer=xml_manufacturers[manuf_idx][0],
            unp=xml_manufacturers[manuf_idx][1],
            quantity=(i * 19) % 100 + 1,  
            address=xml_addresses[addr_idx]
        )
        products.append(product)
    
   #сохраним в файл в проекте
    write_xml(products, "samples/sample.xml")
    print(f"Создан файл samples/sample.xml с {len(products)} записями (офисная техника и мебель)")


def main():
    app = QApplication(sys.argv)  #создает жкземпляр приложения pyqt5
    
    # создаём каталоги
    os.makedirs("data", exist_ok=True)
    os.makedirs("samples", exist_ok=True)
    
    controller = Controller() #создаем контроллер
    
    # смотрим, есть ли данные
    products, total = controller.get_products_page(0, 1)
    if total == 0:
        print("Создание образцов данных...")
        print("1. Создание 60 записей в БД (компьютерная техника)...")
        create_sample_data(controller)
        print("2. Создание XML файл с 50 записями (офисная техника и мебель)...")
        create_sample_xml_file()
        print("\nОбразцы данных созданы успешно!")
        print("\nВ базе данных: 60 записей (компьютерная техника)")
        print("В файле samples/sample.xml: 50 записей (офисная техника, мебель, канцтовары)")
       
    window = MainWindow(controller)  #создает главное окно
    window.show()  #и показывает окно
    
    sys.exit(app.exec_())  #запуск цикла событий


if __name__ == "__main__":
    main()