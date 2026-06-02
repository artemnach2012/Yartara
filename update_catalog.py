import openpyxl
import re
import json
from pathlib import Path

EXCEL_FILE = "data/опт 01.06..xlsx"
JSON_FILE = "data/products.json"

if not Path(EXCEL_FILE).exists():
    print(f"❌ Файл не найден: {EXCEL_FILE}")
    exit(1)

wb = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
sheet = wb.active

START_ROW = 8
NAME_COL = 5
PRICE_COL = 14
STOCK_COL = 15

products = []
pid = 1
skipped_empty = 0
skipped_short = 0
skipped_stopword = 0
skipped_no_price = 0

for row_idx in range(START_ROW, sheet.max_row + 1):
    name = sheet.cell(row=row_idx, column=NAME_COL).value
    price_cell = sheet.cell(row=row_idx, column=PRICE_COL).value
    stock_cell = sheet.cell(row=row_idx, column=STOCK_COL).value

    if not name or not isinstance(name, str):
        skipped_empty += 1
        continue
    name = name.strip()
    if len(name) < 2:   # теперь 2 символа минимум
        skipped_short += 1
        continue
    if any(x in name for x in ['Итого', 'Всего', 'Прайс-лист']):
        skipped_stopword += 1
        continue

    try:
        if price_cell is None or stock_cell is None:
            skipped_no_price += 1
            continue
        if isinstance(price_cell, (int, float)):
            price_val = float(price_cell)
        else:
            price_val = float(str(price_cell).replace(',', '.').replace(' ', ''))
        if isinstance(stock_cell, (int, float)):
            stock_val = float(stock_cell)
        else:
            stock_val = float(str(stock_cell).replace(',', '').replace(' ', ''))
    except:
        continue

    # Категория
    name_low = name.lower()
    if 'банк' in name_low and 'бутыл' not in name_low:
        category = 'Стеклянные банки'
    elif 'бутылк' in name_low or 'бутыль' in name_low:
        category = 'Бутылки и бутыли'
    elif 'крышк' in name_low or 'колпач' in name_low:
        category = 'Крышки и колпачки'
    else:
        category = 'Разное'

    vol_match = re.search(r'(\d+[.,]?\d*)\s*(л|мл|литр)', name, re.IGNORECASE)
    volume = f"{vol_match.group(1).replace(',', '.')} {vol_match.group(2).lower()}" if vol_match else ''
    diam_match = re.search(r'd(\d+)', name)
    diameter = f"d{diam_match.group(1)}" if diam_match else ''

    description = f"✨ {name} ✨\n\n💰 Цена: {price_val:.2f} руб. (опт, с НДС)\n📦 В наличии: {stock_val:.0f} шт.\n"
    if volume:
        description += f"📏 Объём: {volume}\n"
    if diameter:
        description += f"🔘 Диаметр горла: {diameter}\n"
    description += "🚚 Отгрузка от 1 шт. При заказе от 5000 руб — бесплатная доставка по Новосибирску."

    images = [f"https://via.placeholder.com/400x300?text={name[:30]}" for _ in range(3)]

    products.append({
        "id": pid,
        "name": name,
        "price": price_val,
        "stock": stock_val,
        "volume": volume,
        "diameter": diameter,
        "category": category,
        "description": description,
        "images": images
    })
    pid += 1

Path("data").mkdir(exist_ok=True)
with open(JSON_FILE, 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"\n✅ Обработано товаров: {len(products)}")
print(f"Пропущено (пустое имя): {skipped_empty}")
print(f"Пропущено (имя короче 2): {skipped_short}")
print(f"Пропущено (стоп-слова): {skipped_stopword}")
print(f"Пропущено (нет цены или остатка): {skipped_no_price}")

if products:
    print("\nПервые 3 товара:")
    for p in products[:3]:
        print(f"  - {p['name']} | {p['price']} ₽ | остаток {p['stock']:.0f}")
    print("\nПоследние 3 товара:")
    for p in products[-3:]:
        print(f"  - {p['name']} | {p['price']} ₽ | остаток {p['stock']:.0f}")
else:
    print("⚠️ Товаров не найдено. Проверьте Excel и параметры.")