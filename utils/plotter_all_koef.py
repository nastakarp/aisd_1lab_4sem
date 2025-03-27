import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os

# Путь для сохранения графиков
output_dir = r'C:\OPP\compression_project\results\graphs'

# Создаем папку, если она не существует
os.makedirs(output_dir, exist_ok=True)


def save_plot(data, title, filename, color):
    """Общая функция для создания и сохранения графиков"""
    df = pd.DataFrame.from_dict(data, orient='index', columns=['Коэффициент сжатия'])
    ax = df.plot(kind='bar', figsize=(10, 6), color=color, edgecolor='black')
    plt.title(f'Коэффициенты сжатия для {title}')
    plt.ylabel('Коэффициент сжатия')
    plt.xlabel('Метод сжатия')
    plt.xticks(rotation=45)

    # Форматирование подписей в зависимости от величины значений
    for p in ax.patches:
        value = p.get_height()
        fmt = '.1f' if value > 10 else '.2f'
        ax.annotate(f"{value:{fmt}}",
                    (p.get_x() + p.get_width() / 2., value),
                    ha='center', va='center',
                    xytext=(0, 5),
                    textcoords='offset points')

    plt.tight_layout()
    full_path = os.path.join(output_dir, filename)
    plt.savefig(full_path)
    plt.close()  # Закрываем figure чтобы освободить память
    print(f"График сохранен в {full_path}")


def plot_all():
    # Данные для каждого типа
    plots = [
        {
            "data": {
                "HA": 1.559, "RLE": 0.924, "BWT + RLE": 0.80,
                "BWT + MTF + HA": 1.90, "BWT + MTF + RLE + HA": 1.67,
                "LZ77": 1.256, "LZ77 + HA": 1.273, "LZ78": 1.85, "LZ78 + HA": 2.02
            },
            "title": "enwik7",
            "filename": "enwik7_compression.png",
            "color": "skyblue"
        },
        {
            "data": {
                "HA": 1.958, "RLE": 0.962, "BWT + RLE": 1.10,
                "BWT + MTF + HA": 2.42, "BWT + MTF + RLE + HA": 2.59,
                "LZ77": 1.627, "LZ77 + HA": 1.498, "LZ78": 2.25, "LZ78 + HA": 2.38
            },
            "title": "русского текста",
            "filename": "russian_text_compression.png",
            "color": "lightgreen"
        },
        {
            "data": {
                "HA": 1.243, "RLE": 0.988, "BWT + RLE": 0.85,
                "BWT + MTF + HA": 1.62, "BWT + MTF + RLE + HA": 1.53,
                "LZ77": 0.905, "LZ77 + HA": 1.123, "LZ78": 1.30, "LZ78 + HA": 1.47
            },
            "title": "бинарного файла",
            "filename": "binary_file_compression.png",
            "color": "salmon"
        },
        {
            "data": {
                "HA": 5.510, "RLE": 96.658, "BWT + RLE": 46.08,
                "BWT + MTF + HA": 7.71, "BWT + MTF + RLE + HA": 61.41,
                "LZ77": 25.093, "LZ77 + HA": 48.779, "LZ78": 89.99, "LZ78 + HA": 93.92
            },
            "title": "ч/б изображения",
            "filename": "bw_image_compression.png",
            "color": "gray"
        },
        {
            "data": {
                "HA": 3.796, "RLE": 60.992, "BWT + RLE": 27.27,
                "BWT + MTF + HA": 7.58, "BWT + MTF + RLE + HA": 35.20,
                "LZ77": 11.616, "LZ77 + HA": 23.076, "LZ78": 35.00, "LZ78 + HA": 33.94
            },
            "title": "изображения в оттенках серого",
            "filename": "grayscale_image_compression.png",
            "color": "silver"
        },
        {
            "data": {
                "HA": 3.169, "RLE": 0.949, "BWT + RLE": 31.45,
                "BWT + MTF + HA": 7.45, "BWT + MTF + RLE + HA": 31.23,
                "LZ77": 16.244, "LZ77 + HA": 35.316, "LZ78": 58.18, "LZ78 + HA": 59.42
            },
            "title": "цветного изображения",
            "filename": "color_image_compression.png",
            "color": "lightcoral"
        }
    ]

    # Создаем все графики
    for plot in plots:
        save_plot(**plot)


if __name__ == "__main__":
    plot_all()