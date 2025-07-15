import asyncio
from app.api.dao import ContractorDAO


async def main():
    # Добавьте данные, которые хотите видеть в боте
    contractors_to_add = [
        {'name': 'Иван Петров', 'category': 'Фотографы', 'contact': '@ivan_photo'},
        {'name': 'Анна Смирнова', 'category': 'Фотографы', 'contact': '+79261234567'},
        {'name': 'Вкусный Праздник', 'category': 'Кейтеринг', 'contact': 'vkusno@email.com'},
        {'name': 'Food Masters', 'category': 'Кейтеринг', 'contact': '+79169876543'},
        {'name': 'Дмитрий Афанасьев', 'category': 'Ведущие', 'contact': '@haderen'},
    ]

    print("Seeding contractors...")
    for data in contractors_to_add:
        # Проверяем, есть ли уже такая запись
        exists = await ContractorDAO.find_one_or_none(name=data['name'], category=data['category'])
        if not exists:
            await ContractorDAO.add(**data)
            print(f"Added: {data['name']} ({data['category']})")
        else:
            print(f"Skipped (already exists): {data['name']}")
    print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(main())
