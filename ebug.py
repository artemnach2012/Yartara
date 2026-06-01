import openpyxl

wb = openpyxl.load_workbook("data/опт 01.06..xlsx", data_only=True)
sheet = wb.active

print(f"Лист: {sheet.title}")
print("Первые 10 строк, колонки A B C D E F G H I J K L M N O:\n")
for row in range(1, 11):
    values = []
    for col in range(1, 16):  # A..O
        val = sheet.cell(row=row, column=col).value
        values.append(str(val)[:20] if val else "")
    print(f"Строка {row:2}: {values}")