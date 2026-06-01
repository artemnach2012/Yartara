import openpyxl
import re
import json
import os
import datetime
from pathlib import Path

EXCEL_FILE = "data/опт 01.06..xlsx"
JSON_FILE = "data/products.json"
OLD_JSON = "data/products_old.json"   # для сравнения

if not Path(EXCEL_FILE).exists():
    print(f"❌ Файл не найден: {EXCEL_FILE}")
    exit(1)

wb = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
sheet = wb.active

START_ROW = 8
NAME_COL = 5
PRICE_COL = 14
STOCK_COL = 15

# ---- Загрузка старой версии (если есть) ----
old_products = {}
if os.path.exists(OLD_JSON):
    with open(OLD_JSON, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
        # Может быть два формата: просто список или словарь с ключом "items"
        if isinstance(old_data, list):
            old_list = old_data
        elif isinstance(old_data, dict) and "items" in old_data:
            old_list = old_data["items"]
        else:
            old_list = []
        for p in old_list:
            old_products[p['id']] = p

products = []
pid = 1

for row_idx in range(START_ROW, sheet.max_row + 1):
    name = sheet.cell(row=row_idx, column=NAME_COL).value
    price_cell = sheet.cell(row=row_idx, column=PRICE_COL).value
    stock_cell = sheet.cell(row=row_idx, column=STOCK_COL).value

    if not name or not isinstance(name, str):
        continue
    name = name.strip()
    if len(name) < 3:
        continue
    if any(x in name for x in ['Итого', 'Всего', 'Прайс-лист']):
        continue

    try:
        if price_cell is None or stock_cell is None:
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
    elif 'пленк' in name_low or 'агро' in name_low or 'теплич' in name_low:
        category = 'Сад и огород'
    else:
        category = 'Разное'

    # Объём
    vol_match = re.search(r'(\d+[.,]?\d*)\s*(л|мл|литр)', name, re.IGNORECASE)
    volume = f"{vol_match.group(1).replace(',', '.')} {vol_match.group(2).lower()}" if vol_match else ''

    # Диаметр горла
    diam_match = re.search(r'd(\d+)', name)
    diameter = f"d{diam_match.group(1)}" if diam_match else ''

    # Описание
    description = f"✨ {name} ✨\n\n💰 Цена: {price_val:.2f} руб. (опт, с НДС)\n📦 В наличии: {stock_val} шт.\n"
    if volume:
        description += f"📏 Объём: {volume}\n"
    if diameter:
        description += f"🔘 Диаметр горла: {diameter}\n"
    description += "🚚 Отгрузка от 1 шт. При заказе от 5000 руб — бесплатная доставка по Новосибирску.\n⭐ Идеально для консервации, виноделия и домашнего хозяйства."

    # Заглушки изображений (можно позже заменить на реальные фото)
    images = [f"https://via.placeholder.com/400x300?text={name[:30]}" for _ in range(3)]

    # Проверка изменений
    old = old_products.get(pid)
    changed = False
    if old:
        if old.get('price') != price_val or old.get('stock') != stock_val:
            changed = True
    # Первый запуск – ничего не помечаем как изменённое (или можно пометить все как новые? – лучше не надо)

    products.append({
        "id": pid,
        "name": name,
        "price": price_val,
        "stock": stock_val,
        "volume": volume,
        "diameter": diameter,
        "category": category,
        "description": description,
        "images": images,
        "is_changed_today": changed   # флаг для подсветки
    })
    pid += 1

# Добавляем дату последнего обновления и оборачиваем в объект
now_iso = datetime.datetime.now().isoformat()
output_data = {
    "last_updated": now_iso,
    "last_updated_human": datetime.datetime.now().strftime("%d.%m.%Y в %H:%M"),
    "total_items": len(products),
    "items": products
}

# Сохраняем новый JSON
Path("data").mkdir(exist_ok=True)
with open(JSON_FILE, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

# Сохраняем копию как старую версию для будущих сравнений
with open(OLD_JSON, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"✅ Обработано товаров: {len(products)}")
print(f"📅 Дата обновления: {output_data['last_updated_human']}")
if products:
    print("Пример первых трёх товаров с флагом изменений:")
    for p in products[:3]:
        print(f"  - {p['name']} | цена {p['price']} ₽ | изменён сегодня: {p['is_changed_today']}")