from algorithms.bwt import  bwt_transform
from algorithms.mtf import  mtf_transform
from file_analysis import calculate_entropy

import numpy as np
from collections import defaultdict
import matplotlib
import matplotlib.pyplot as plt

# Устанавливаем бэкенд, который работает в PyCharm
matplotlib.use('TkAgg')  # Или 'Qt5Agg' если у вас установлен PyQt5


def process_file(filename: str, block_sizes: list[int]) -> dict[int, float]:
    try:
        with open(filename, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Файл {filename} не найден!")
        return {}

    results = {}

    for block_size in block_sizes:
        if block_size == 0:
            blocks = [data]
        else:
            blocks = [data[i:i + block_size] for i in range(0, len(data), block_size)]

        total_entropy = 0.0
        total_blocks = 0

        for block in blocks:
            if not block:
                continue

            try:
                bwt_data, _ = bwt_transform(block)
                mtf_data = mtf_transform(bwt_data)
                entropy = calculate_entropy(mtf_data)

                total_entropy += entropy
                total_blocks += 1
            except Exception as e:
                print(f"Ошибка при обработке блока размером {block_size}: {e}")
                continue

        if total_blocks > 0:
            avg_entropy = total_entropy / total_blocks
            results[block_size] = avg_entropy

    return results


# Основная часть программы
if __name__ == "__main__":
    # Размеры блоков для анализа (в байтах)
    block_sizes = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
    filename = 'C:/OPP/compression_project/tests/test1_enwik7'

    # Вычисляем энтропию для каждого размера блока
    results = process_file(filename, block_sizes)

    if not results:
        print("Не удалось получить результаты. Проверьте наличие файла и ошибки выше.")
    else:
        # Подготовка данных для графика
        x = list(results.keys())
        y = list(results.values())

        # Создание графика
        plt.figure(figsize=(12, 6))
        plt.plot(x, y, 'bo-', linewidth=2, markersize=8)
        plt.xscale('log')
        plt.xlabel('Размер блока (байты, логарифмическая шкала)', fontsize=12)
        plt.ylabel('Энтропия (бит/символ)', fontsize=12)
        plt.title('Зависимость энтропии после BWT+MTF от размера блока\n(файл enwik7)', fontsize=14)
        plt.grid(True, which="both", ls="-", alpha=0.5)

        # Добавляем значения точек на график
        for xi, yi in zip(x, y):
            plt.text(xi, yi, f'{yi:.2f}', ha='center', va='bottom')

        plt.tight_layout()

        # Сохраняем график в файл
        plt.savefig('C:/OPP/compression_project/results/graphs/entropy_plot.png')
        print("График сохранён в файл 'entropy_plot.png'")

        # Вывод результатов в консоль
        print("\nРезультаты анализа:")
        print("Размер блока (байт)\tЭнтропия (бит/символ)")
        print("----------------------------------------")
        for size, entropy in sorted(results.items()):
            print(f"{size:<20}\t{entropy:.4f}")