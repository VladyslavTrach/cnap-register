import logging
from scraper import scrape  # імпортуємо функцію scrape з файлу scraper.py

def main():
    logging.info("Запуск процесу скрейпінгу")
    scrape()  # виклик функції, яка автоматизує роботу браузера

if __name__ == '__main__':
    main()
