import openpyxl
import json
import re

wb = openpyxl.load_workbook("data/опт 01.06..xlsx", data_only=True)
sheet = wb.active

products = []
pid = 1

for row in range(8, sheet.max_row + 1):
    name = sheet.cell(row, 5).value     # колонка E
    price = sheet.cell(row, 14).value   # колонка N
    stock = sheet.cell(row, 15).value   # колонка O

    if not name:
        continue

    name = str(name).strip()
    if len(name) < 3:
        continue

    # Преобразуем цену (может быть число или строка типа "735" или "1 210")
    try:
        if isinstance(price, str):
            # Убираем пробелы и заменяем запятую на точку
            price = float(price.replace(' ', '').replace(',', '.'))
        else:
            price = float(price)
    except:
        continue

    # Преобразуем остаток
    try:
        if isinstance(stock, str):
            stock = float(stock.replace(' ', '').replace(',', ''))
        else:
            stock = float(stock)
    except:
        continue

    # Определяем объём (например, "3,8 л")
    vol_match = re.search(r'(\d+[.,]?\d*)\s*(л|мл|литр)', name, re.IGNORECASE)
    volume = f"{vol_match.group(1).replace(',', '.')} {vol_match.group(2).lower()}" if vol_match else ''

    # Определяем диаметр (например, d43)
    diam_match = re.search(r'd(\d+)', name)
    diameter = f"d{diam_match.group(1)}" if diam_match else ''

    # Простая категория
    name_low = name.lower()
    if 'банк' in name_low and 'бутыл' not in name_low:
        category = 'Стеклянные банки'
    elif 'бутылк' in name_low or 'бутыль' in name_low:
        category = 'Бутылки и бутыли'
    elif 'крышк' in name_low or 'колпач' in name_low:
        category = 'Крышки и колпачки'
    else:
        category = 'Разное'

    description = f"✨ {name} ✨\n\n💰 Цена: {price:.2f} руб. (опт, с НДС)\n📦 В наличии: {stock:.0f} шт.\n"
    if volume:
        description += f"📏 Объём: {volume}\n"
    if diameter:
        description += f"🔘 Диаметр горла: {diameter}\n"
    description += "🚚 Отгрузка от 1 шт. При заказе от 5000 руб — бесплатная доставка по Новосибирску."

    products.append({
        "id": pid,
        "name": name,
        "price": price,
        "stock": stock,
        "volume": volume,
        "diameter": diameter,
        "category": category,
        "description": description,
        "images": [f"https://via.placeholder.com/400x300?text={name[:30]}"]
    })
    pid += 1

with open("data/products.json", "w", encoding="utf-8") as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"✅ Сохранено товаров: {len(products)}")
if products:
    print("\nПервые 5 товаров:")
    for p in products[:5]:
        print(f"  - {p['name']} | {p['price']} ₽ | остаток {p['stock']:.0f}")