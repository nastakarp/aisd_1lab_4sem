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
                "HA": 1.559, "RLE": 0.924, "BWT + RLE": 0.978,
                "BWT + MTF + HA": 1.897, "BWT + MTF + RLE + HA": 1.452,
                "LZ77": 1.109, "LZ77 + HA": 1.109, "LZ78": 1.849, "LZ78 + HA": 2.019
            },
            "title": "enwik7",
            "filename": "enwik7_compression.png",
            "color": "skyblue"
        },
        {
            "data": {
                "HA": 1.958, "RLE": 0.962, "BWT + RLE": 1.510,
                "BWT + MTF + HA": 2.419, "BWT + MTF + RLE + HA": 2.160,
                "LZ77": 1.462, "LZ77 + HA": 1.462, "LZ78": 2.249, "LZ78 + HA": 2.384
            },
            "title": "русского текста",
            "filename": "russian_text_compression.png",
            "color": "lightgreen"
        },
        {
            "data": {
                "HA": 1.243, "RLE": 0.988, "BWT + RLE": 1.093,
                "BWT + MTF + HA": 1.621, "BWT + MTF + RLE + HA": 1.379,
                "LZ77": 0.829, "LZ77 + HA": 0.829, "LZ78": 1.297, "LZ78 + HA": 1.471
            },
            "title": "бинарного файла",
            "filename": "binary_file_compression.png",
            "color": "salmon"
        },
        {
            "data": {
                "HA": 5.510, "RLE": 96.658, "BWT + RLE": 43.329,
                "BWT + MTF + HA": 7.705, "BWT + MTF + RLE + HA": 62.142,
                "LZ77": 63.339, "LZ77 + HA": 63.339, "LZ78": 89.989, "LZ78 + HA": 93.916
            },
            "title": "ч/б изображения",
            "filename": "bw_image_compression.png",
            "color": "gray"
        },
        {
            "data": {
                "HA": 3.796, "RLE": 60.992, "BWT + RLE": 24.417,
                "BWT + MTF + HA": 7.580, "BWT + MTF + RLE + HA": 30.302,
                "LZ77": 60.861, "LZ77 + HA": 60.861, "LZ78": 35.004, "LZ78 + HA": 33.940
            },
            "title": "изображения в оттенках серого",
            "filename": "grayscale_image_compression.png",
            "color": "silver"
        },
        {
            "data": {
                "HA": 3.169, "RLE": 0.949, "BWT + RLE": 29.208,
                "BWT + MTF + HA": 7.447, "BWT + MTF + RLE + HA": 35.776,
                "LZ77": 58.790, "LZ77 + HA": 58.790, "LZ78": 58.175, "LZ78 + HA": 59.416
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