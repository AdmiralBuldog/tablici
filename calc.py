import pandas as pd

# Путь к таблицам
table_a_path = 'C:/Users/vovka/Desktop/готовые таблицы/тестовый вариант.xlsx'
table_b_path = 'C:/Users/vovka/Downloads/Таблица Б.xlsx'

# Загрузка таблицы Б
table_b = pd.read_excel(table_b_path)

# Находим колонку с '_hashing_uptime' (она может изменяться в зависимости от даты)
uptime_column = [col for col in table_b.columns if '_hashing_uptime' in col]
if not uptime_column:
    raise ValueError("Колонка '_hashing_uptime' не найдена в таблице Б")
uptime_column = uptime_column[0]  # используем первую найденную колонку

# Преобразуем в текст, убираем пробелы и переводим в числовой тип с округлением до двух знаков
table_b[uptime_column] = pd.to_numeric(table_b[uptime_column].astype(str).str.strip(), errors='coerce').round(2)

# Проверка значений после преобразования
print("Значения uptime после обработки:")
print(table_b[uptime_column])

# Создаем пустой DataFrame для хранения итоговых данных
sorted_data = pd.DataFrame()

# Загрузка таблицы А со всеми вкладками
table_a_sheets = pd.read_excel(table_a_path, sheet_name=None)

# Проходим по каждой вкладке таблицы А
for sheet_name, table_a in table_a_sheets.items():
    # Фильтруем таблицу Б по текущему воркеру (клиенту)
    worker_data = table_b[table_b['miner_worker'] == sheet_name]

    # Если нет miner_worker, используем miner_mac
    if worker_data.empty:
        worker_data = table_b[table_b['miner_mac'].isin(table_a['miner_mac'])]

    # Сортировка worker_data на основе порядка в таблице А
    worker_data.set_index(['miner_type', 'miner_mac'], inplace=True)
    worker_data = worker_data.reindex(table_a.set_index(['miner_type', 'miner_mac']).index).reset_index()

    # Расчет времени работы и простоя
    def calculate_uptime(row):
        uptime_percentage = row[uptime_column]
        print(f"Обрабатываемое uptime_percentage: {uptime_percentage}")

        # Если значение NaN, устанавливаем 0% (полный простой)
        if pd.isna(uptime_percentage):
            uptime_percentage = 0.0

        # Рассчитываем время работы и простоя
        worked_hours_total = (uptime_percentage / 100) * 24
        downtime_hours_total = 24 - worked_hours_total

        # Разбиваем на часы и минуты
        worked_hours = int(worked_hours_total)
        worked_minutes = int((worked_hours_total - worked_hours) * 60)

        downtime_hours = int(downtime_hours_total)
        downtime_minutes = int((downtime_hours_total - downtime_hours) * 60)

        return f"{worked_hours}h {worked_minutes}m ({downtime_hours}h {downtime_minutes}m downtime)"

    worker_data['Worked / Downtime'] = worker_data.apply(calculate_uptime, axis=1)

    # Добавляем обработанные данные в общий DataFrame
    sorted_data = pd.concat([sorted_data, worker_data])

# Сохраняем отсортированные данные в новый Excel-файл
output_path = 'C:/Users/vovka/Desktop/готовые таблицы/sort_table.xlsx'
sorted_data.to_excel(output_path, index=False)

print(f"Таблица отсортирована и сохранена как {output_path}")
