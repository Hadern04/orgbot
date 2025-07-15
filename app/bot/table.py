import pandas as pd


def get_budget_info(gsheetkey):
    sheet_name = 'Лист1'
    url = f'https://docs.google.com/spreadsheet/ccc?key={gsheetkey}&output=xlsx'
    df = pd.read_excel(url, sheet_name=sheet_name)

    total_budget = df['Итого'].sum()
    total_paid = df['Предоплата'].sum()
    remaining_amount = total_budget - total_paid

    if total_budget > 0:
        paid_percentage = (total_paid / total_budget) * 100
    else:
        paid_percentage = 0

    result = (
        f"Текущий бюджет мероприятия: {total_budget:.0f} руб.\n"
        f"Оплачено: {paid_percentage:.0f}% ({total_paid:.0f} руб.)\n"
        f"Осталось оплатить: {remaining_amount:.0f} руб."
    )

    return result


# Пример использования
if __name__ == "__main__":
    # Тестовая ссылка (замените на свою)
    key = "1UJS5Ndx8IYD0q6uSeJbzUyGzGMGxSobSIYE1EpEFwIc"
    print(get_budget_info(key))