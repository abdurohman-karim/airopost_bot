"""Встроенный каталог основных вершин Узбекистана и соседних стран — виден всем пользователям.

Координаты и высоты — из OpenStreetMap (natural=peak, тег ele). При запуске бот обновляет
эти записи в базе по ключу slug, поэтому правки здесь применяются автоматически.
Вершины, которые предлагают пользователи, попадают в тот же каталог после одобрения админа.
"""

REGIONS = ("tashkent", "jizzakh", "surkhandarya", "fann", "pamir", "kyrgyz", "kazakhstan", "community")

# slug, регион, название ru / uz / en, широта, долгота, высота
PEAKS = [
    ("big-chimgan", "tashkent", "Большой Чимган", "Katta Chimyon", "Big Chimgan", 41.49519, 70.05867, 3309),
    ("small-chimgan", "tashkent", "Малый Чимган", "Kichik Chimyon", "Lesser Chimgan", 41.55250, 70.04056, 2098),
    ("kyzylnura", "tashkent", "Кызылнура", "Qizilnura", "Kyzylnura", 41.26336, 69.97375, 3268),
    ("babaytag", "tashkent", "Бабайтаг", "Boboytogʻ", "Babaytag", 41.15496, 70.22327, 3556),
    ("aktash-parkent", "tashkent", "Акташ (Паркент)", "Oqtosh (Parkent)", "Aktash (Parkent)",
     41.24837, 69.86760, 2510),
    ("aktash-bostanlyk", "tashkent", "Акташ (Бостанлык)", "Oqtosh (Boʻstonliq)", "Aktash (Bostanlyk)",
     41.72234, 70.47584, 3462),
    ("beshtor", "tashkent", "Бештор", "Beshtor", "Beshtor", 42.05413, 70.86517, 4292),
    ("adelung", "tashkent", "Аделунга", "Adelunga togʻi", "Adelung Peak", 42.12356, 70.96892, 4302),
    ("kumbel", "tashkent", "Кумбель", "Qumbel", "Kumbel", 41.47610, 69.97813, 2307),
    ("pulatkhan", "tashkent", "Пулатхан", "Poʻlatxon", "Pulatkhan", 41.43381, 70.17186, 2823),
    ("karakush", "tashkent", "Каракуш", "Qoraqush", "Karakush", 41.24779, 70.33915, 3864),
    ("aktash-zaamin", "jizzakh", "Акташ (Заамин)", "Oqtosh (Zomin)", "Aktash (Zaamin)", 39.56581, 68.43816, 3145),
    ("hayatbashi", "jizzakh", "Хаятбаши", "Hayotboshi", "Hayatbashi", 40.49510, 66.72046, 2169),
    ("khazret-sultan", "surkhandarya", "Хазрет Султан", "Hazrati Sulton", "Khazret Sultan",
     38.94778, 68.17247, 4643),
    # Соседние страны: популярные цели походов и восхождений из Узбекистана
    ("chimtarga", "fann", "Чимтарга", "Chimtarg‘a", "Chimtarga", 39.19788, 68.19559, 5489),
    ("bodkhona", "fann", "Бодхона", "Bodxona", "Bodkhona", 39.18986, 68.29361, 5152),
    ("mirali", "fann", "Мирали", "Mirali", "Mirali", 39.21084, 68.20083, 5106),
    ("somoni", "pamir", "Пик Исмоила Сомони", "Ismoil Somoniy choʻqqisi", "Ismoil Somoni Peak", 38.94301, 72.01559, 7495),
    ("lenin", "pamir", "Пик Ленина", "Lenin choʻqqisi", "Lenin Peak", 39.34698, 72.87918, 7134),
    ("korzhenevskaya", "pamir", "Пик Корженевской", "Korjenevskaya choʻqqisi", "Korzhenevskaya Peak",
     39.05688, 72.00968, 7105),
    ("uchitel", "kyrgyz", "Учитель (Ала-Арча)", "Uchitel (Ala-Archa)", "Uchitel (Ala-Archa)", 42.53802, 74.55306, 4530),
    ("talgar", "kazakhstan", "Талгар", "Talgar", "Talgar Peak", 43.11863, 77.33988, 4979),
    ("sayram", "kazakhstan", "Сайрам", "Sayram", "Sayram Peak", 42.13781, 70.48066, 4238),
    ("big-almaty", "kazakhstan", "Большой Алматинский пик", "Katta Olmaota choʻqqisi", "Big Almaty Peak",
     43.05529, 76.93359, 3680),
    ("aksay", "kazakhstan", "Пик Аксай", "Aqsoy choʻqqisi", "Aksay Peak", 43.03621, 76.82032, 3640),
    ("furmanov", "kazakhstan", "Пик Фурманова", "Furmanov choʻqqisi", "Furmanov Peak", 43.14990, 77.11567, 3053),
]

# Перевалы на автодорогах: ключ, название ru / uz / en, дорога ru / uz / en, широта, долгота, высота (OpenStreetMap)
PASSES = [
    ("kamchik", "Камчик", "Qamchiq", "Kamchik", "Ташкент — Фергана (A373)", "Toshkent — Fargʻona (A373)",
     "Tashkent — Fergana (A373)", 41.09637, 70.51982, 2268),
    ("takhtakaracha", "Тахтакарача", "Taxtaqoracha", "Takhtakaracha", "Самарканд — Шахрисабз",
     "Samarqand — Shahrisabz", "Samarkand — Shahrisabz", 39.28598, 66.94098, 1680),
]

# Горнолыжные курорты: ключ, название ru / uz / en, широта, долгота (низ), высота низа и верха трасс.
# Низ — по модели рельефа в точке курорта, верх — примерная отметка верхней станции подъёмника.
RESORTS = [
    ("amirsoy", "Амирсой", "Amirsoy", "Amirsoy", 41.48749, 69.94215, 1600, 2290),
    ("beldersay", "Бельдерсай", "Beldersoy", "Beldersay", 41.50227, 69.97736, 1550, 2300),
    ("chimgan", "Чимган", "Chimyon", "Chimgan", 41.54350, 70.01580, 1600, 2100),
]
