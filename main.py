from compressors.compressor_ha import compress_ha, decompress_ha
from compressors.compressor_rle import compress_rle, decompress_rle
from compressors.compressor_bwt_rle import compress_bwt_rle, decompress_bwt_rle
from compressors.compressor_bwt_mtf_ha import compress_bwt_mtf_ha, decompress_bwt_mtf_ha
from compressors.compressor_lz77 import compress_lz77, decompress_lz77
from compressors.compressor_lz77_ha import compress_lz77_ha, decompress_lz77_ha
from compressors.compressor_lz78 import compress_lz78, decompress_lz78
from compressors.compressor_lz78_ha import compress_lz78_ha, decompress_lz78_ha

from utils.file_utils import read_file, write_file, process_file
from utils.entropy_calculator import calculate_entropy
from utils.plotter import plot_compression_ratios, plot_compression_ratio_vs_buffer_size, plot_entropy_vs_block_size, analyze_compression

def compress_file(input_path, output_path, compressor):
    """
    Сжимает файл с использованием указанного компрессора.
    """
    data = read_file(input_path)
    compressed_data = compressor.compress(data)
    write_file(output_path, compressed_data)
    print(f"Файл {input_path} сжат и сохранен в {output_path}")

def decompress_file(input_path, output_path, compressor):
    """
    Восстанавливает файл с использованием указанного компрессора.
    """
    compressed_data = read_file(input_path)
    decompressed_data = compressor.decompress(compressed_data)
    write_file(output_path, decompressed_data)
    print(f"Файл {input_path} восстановлен и сохранен в {output_path}")


def test_compression(compress_func, decompress_func, input_file, output_file):
    """
    Тестирует сжатие и восстановление файла с использованием указанных функций.
    """
    # Чтение исходного файла
    data = read_file(input_file)

    # Сжатие
    compressed_data = compress_func(data)
    write_file(output_file, compressed_data)

    # Восстановление
    decompressed_data = decompress_func(compressed_data)
    decompressed_file = output_file.replace(".compressed", ".decompressed")
    write_file(decompressed_file, decompressed_data)

    # Проверка целостности данных
    if data == decompressed_data:
        print("Тест пройден: данные восстановлены корректно.")
    else:
        print("Тест не пройден: данные восстановлены с ошибками.")

    # Вычисление коэффициента сжатия
    original_size = len(data)
    compressed_size = len(compressed_data)
    compression_ratio = original_size / compressed_size
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")

    # Вычисление энтропии
    entropy = calculate_entropy(data)
    print(f"Энтропия исходного файла: {entropy:.2f}")

    return compression_ratio, entropy


if __name__ == "__main__":
    # Пути к тестовым файлам
    input_file = "tests/test1_enwik3.txt"
    compressed_file = "results/compressed/enwik3_compressed.bin"

    # Список компрессоров для тестирования
    compressors = {
        "HA": (compress_ha, decompress_ha),
        "RLE": (compress_rle, decompress_rle),
        "BWT + RLE": (compress_bwt_rle, decompress_bwt_rle),
        "BWT + MTF + HA": (compress_bwt_mtf_ha, decompress_bwt_mtf_ha),
        "LZ77": (compress_lz77, decompress_lz77),
        "LZ77 + HA": (compress_lz77_ha, decompress_lz77_ha),
        "LZ78": (compress_lz78, decompress_lz78),
        "LZ78 + HA": (compress_lz78_ha, decompress_lz78_ha),
    }

    # Результаты тестов
    results = {}

    # Тестирование каждого компрессора
    for name, (compress_func, decompress_func) in compressors.items():
        print(f"\nТестирование компрессора: {name}")
        compressed_file_path = compressed_file.replace(".bin", f"_{name.lower()}.bin")
        compression_ratio, entropy = test_compression(compress_func, decompress_func, input_file, compressed_file_path)
        results[name] = {
            "compression_ratio": compression_ratio,
            "entropy": entropy,
        }

    # Построение графиков
    plot_compression_ratios(results)
    plot_compression_ratio_vs_buffer_size(results)
    plot_entropy_vs_block_size(results)

    # Анализ результатов
    analyze_compression(results)

    # Сохранение результатов в таблицу
    with open("results/tables/results.csv", "w") as f:
        f.write("Compressor,Compression Ratio,Entropy\n")
        for name, data in results.items():
            f.write(f"{name},{data['compression_ratio']:.2f},{data['entropy']:.2f}\n")

    print("\nВсе тесты завершены. Результаты сохранены в папке results.")