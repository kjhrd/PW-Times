import requests
import time


def measure_load_time(url):
    start_time = time.time()
    response = requests.get(url)
    end_time = time.time()
    load_time = end_time - start_time
    return load_time


def main():
    url = input("Введите URL страницы: ")
    num_requests = int(input("Введите количество запросов для измерения среднего времени загрузки: "))

    total_load_time = 0
    for _ in range(num_requests):
        total_load_time += measure_load_time(url)

    average_load_time = total_load_time / num_requests
    print(f"Среднее время загрузки страницы {url} составляет {average_load_time:.3f} секунд.")


if __name__ == "__main__":
    main()
