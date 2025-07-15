from collections import defaultdict


def substract_lots(db_stats, reserved_lots):
    # Преобразуем в структуру для удобного вычитания
    stats_dict = defaultdict(list)
    for lot_type, price, count in db_stats:
        stats_dict[lot_type].append([price, count])

    # Сортируем для предсказуемости
    for lot_type in stats_dict:
        stats_dict[lot_type].sort()

    # Вычитаем каждый зарезервированный лот
    for lot in reserved_lots:
        # Берем первый ключ, который не 'filename'
        lot_type = next(k for k in lot.keys() if k != 'filename')
        if lot_type not in stats_dict:
            continue
        for entry in stats_dict[lot_type]:
            if entry[1] > 0:
                entry[1] -= 1
                break

    # Преобразуем обратно в список кортежей
    result_stats = []
    for lot_type, entries in stats_dict.items():
        for price, count in entries:
            result_stats.append((lot_type, price, count))

    return result_stats
