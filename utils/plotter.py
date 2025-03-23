import matplotlib.pyplot as plt

# Данные
buffer_sizes = [2048, 4096, 8192, 16384]
compression_ratios = [0.848, 0.975, 1.109, 1.256]

# Построение графика
plt.figure(figsize=(10, 6))
plt.plot(buffer_sizes, compression_ratios, marker='o', linestyle='-', color='b')

# Подписи осей и заголовок
plt.xlabel('Размер буфера')
plt.ylabel('Коэффициент сжатия')
plt.title('Зависимость коэффициента сжатия LZ77 от размера буфера')

# Сетка
plt.grid(True)

# Сохранение графика в файл
output_path = "compression_ratio_vs_buffer_size.png"  # Укажите путь и имя файла
plt.savefig(output_path, dpi=300, bbox_inches='tight')  # Сохраняем график в PNG

print(f"График сохранен в файл: {output_path}")