!pip install selenium
!apt-get update 
!apt-get install -y chromium-chromedriver 

import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def save_pages_to_file(base_urls, pages, output_file):
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)

    try:
        with open(output_file, "w", encoding="utf-8") as file:
            for base_url in base_urls:
                for page in range(pages):
                    url = f"{base_url}&s={30 * page}"
                    print(f"Загружается страница: {url}")
                    driver.get(url)
                    time.sleep(5)  

                    # Запись в промежуточный HTML файл
                    file.write(driver.page_source)
                    file.write("\n<!-- PAGE BREAK -->\n")
    except Exception as ex:
        print(f"Ошибка при сборе страниц: {ex}")
    finally:
        driver.quit()


def parse_file_and_save_to_csv(input_file, output_csv):
    with open(input_file, "r", encoding="utf-8") as file:
        src = file.read()
    pages = src.split("<!-- PAGE BREAK -->")
    all_hotels = []

    for page_number, page_content in enumerate(pages, start=1):
        soup = BeautifulSoup(page_content, "lxml")

        hotel_items = soup.find_all("span", class_="search-filter-item__option")

        if not hotel_items:
            print(f"На странице {page_number} не найдено отелей.")
            continue

        for hotel_item in hotel_items:
            name_tag = hotel_item.find("span", class_="search-filter-item__option_strong")
            city_tag = hotel_item.find_all("span", class_="search-filter-item__option_mr5")

            hotel_name = name_tag.get_text(strip=True) if name_tag else "Не указано"
            city_name = city_tag[-1].get_text(strip=True) if city_tag else "Не указано"

            all_hotels.append({"Name": hotel_name, "City": city_name})

    # Сохраняем в CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Name", "City"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for hotel in all_hotels:
            writer.writerow({"Name": hotel["Name"], "City": hotel["City"]})

    print(f"Данные успешно сохранены в '{output_csv}'.")


def main():
    base_urls = [
        "https://tury.ru/hotel/?cn=0&ct=464&ht=0&ad=2&ch=0&dt_f=2025-02-08&dt_t=2025-04-10",
        "https://tury.ru/hotel/?cn=0&ct=332855&ht=0&ad=2&ch=0&dt_f=2025-02-08&dt_t=2025-04-10",
        "https://tury.ru/hotel/?cn=0&ct=112465&ht=0&ad=2&ch=0&dt_f=2025-02-08&dt_t=2025-04-10"
    ]
    html_file = "hotels_pages.html"
    csv_file = "hotels_data.csv"
    save_pages_to_file(base_urls, pages=16, output_file=html_file)

    parse_file_and_save_to_csv(input_file=html_file, output_csv=csv_file)


if __name__ == '__main__':
    main()
