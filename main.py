import pandas as pd

# Путь к таблицам
table_a_path = 'C:/Users/vovka/Desktop/готовые таблицы/тестовый вариант.xlsx'
table_b_path = 'C:/Users/vovka/Downloads/Таблица Б.xlsx'

# Загрузка таблицы Б
table_b = pd.read_excel(table_b_path)

# Находим колонку с '_hashing_uptime' (эта колонка имеет переменную дату)
uptime_column = [col for col in table_b.columns if '_hashing_uptime' in col]
if not uptime_column:
    raise ValueError("Колонка '_hashing_uptime' не найдена в таблице Б")
uptime_column = uptime_column[0]  # берем первую найденную колонку

# Округляем до двух знаков и проверяем числовой тип
table_b[uptime_column] = pd.to_numeric(table_b[uptime_column].round(2), errors='coerce')

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
        # Получаем округленное до двух знаков процентное значение
        uptime_percentage = row[uptime_column]

        if pd.isnull(uptime_percentage):
            uptime_percentage = 0.0  # Обработка отсутствующих значений

        # Вычисляем время работы и простоя
        worked_hours_total = (uptime_percentage / 100) * 24
        downtime_hours_total = 24 - worked_hours_total

        worked_hours = int(worked_hours_total)
        worked_minutes = int((worked_hours_total % 1) * 60)

        downtime_hours = int(downtime_hours_total)
        downtime_minutes = int((downtime_hours_total % 1) * 60)

        return f"{worked_hours}h {worked_minutes}m ({downtime_hours}h {downtime_minutes}m downtime)"


    worker_data['Worked / Downtime'] = worker_data.apply(calculate_uptime, axis=1)

    # Добавляем результаты в общий DataFrame
    sorted_data = pd.concat([sorted_data, worker_data])

# Сохраняем отсортированные данные в новый Excel-файл
output_path = 'C:/Users/vovka/Desktop/готовые таблицы/sort_table.xlsx'
sorted_data.to_excel(output_path, index=False)

print(f"Таблица отсортирована и сохранена как {output_path}")
