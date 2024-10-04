import pandas as pd

# Путь к таблицам
table_a_path = 'C:/Users/vovka/Desktop/готовые таблицы/тестовый вариант.xlsx'
table_b_path = 'C:/Users/vovka/Downloads/Таблица Б.xlsx'

# Загрузка таблицы Б
table_b = pd.read_excel(table_b_path)

# Определение колонки uptime
uptime_column = [col for col in table_b.columns if '_hashing_uptime' in col]
if not uptime_column:
    raise ValueError("Колонка '_hashing_uptime' не найдена в таблице Б")
uptime_column = uptime_column[0]

# Преобразование и очистка значений в колонке uptime
table_b[uptime_column] = (
    table_b[uptime_column]
    .astype(str)
    .str.replace(r'[^\d.]', '', regex=True)  # Удаляем все, кроме цифр и точек
    .str.strip()
    .replace('', '0')  # Заменяем пустые строки на '0'
    .astype(float)
    .round(2)
)

# Проверка значений после обработки
print("Значения uptime после обработки:")
print(table_b[uptime_column])

# Создание пустого DataFrame для итоговых данных
sorted_data = pd.DataFrame()

# Загрузка всех листов из таблицы А
table_a_sheets = pd.read_excel(table_a_path, sheet_name=None)

# Обработка каждого листа из таблицы А
for sheet_name, table_a in table_a_sheets.items():
    # Фильтруем таблицу Б по текущему воркеру (клиенту)
    worker_data = table_b[table_b['miner_worker'] == sheet_name]

    # Если нет данных по воркеру, используем фильтрацию по MAC-адресу
    if worker_data.empty:
        worker_data = table_b[table_b['miner_mac'].isin(table_a['miner_mac'])]

    # Слияние с таблицей А для сохранения порядка и удаления NaN
    worker_data = pd.merge(table_a[['miner_type', 'miner_mac']], worker_data, on=['miner_type', 'miner_mac'], how='left')

    # Функция для расчета работы и простоя
    def calculate_uptime(row):
        uptime_percentage = row[uptime_column]
        print(f"Текущее uptime_percentage: {uptime_percentage}")

        if pd.isna(uptime_percentage):
            uptime_percentage = 0.0

        # Расчет времени работы и простоя
        worked_hours_total = (uptime_percentage / 100) * 24
        downtime_hours_total = 24 - worked_hours_total

        # Разделение на часы и минуты
        worked_hours = int(worked_hours_total)
        worked_minutes = int((worked_hours_total - worked_hours) * 60)
        downtime_hours = int(downtime_hours_total)
        downtime_minutes = int((downtime_hours_total - downtime_hours) * 60)

        return f"{worked_hours}h {worked_minutes}m ({downtime_hours}h {downtime_minutes}m downtime)"

    worker_data['Worked / Downtime'] = worker_data.apply(calculate_uptime, axis=1)

    # Объединение данных
    sorted_data = pd.concat([sorted_data, worker_data])

# Сохранение итоговой таблицы
output_path = 'C:/Users/vovka/Desktop/готовые таблицы/sort_table.xlsx'
sorted_data.to_excel(output_path, index=False)

print(f"Таблица успешно сохранена как {output_path}")
