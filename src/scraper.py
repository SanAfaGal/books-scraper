import os
import time
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Configurar logs
os.makedirs('data/logs', exist_ok=True)
os.makedirs('data/output', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/logs/app.log"),
        logging.StreamHandler()
    ]
)

def get_page_with_retries(url, max_retries=3):
    """Manejo básico de fallos con reintentos."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logging.warning(f"Intento {attempt + 1} fallido para {url}: {e}")
            time.sleep(2)
    logging.error(f"Fallo al cargar la página tras {max_retries} intentos: {url}")
    return None

def get_product_details(book_url: str, fetch_details: bool = False):
    """
    Obtiene cantidad de stock y descripción desde la página del producto.

    Parámetros:
        book_url (str): URL del producto.
        fetch_details (bool): Si es False, no hace la petición y devuelve valores por defecto.

    Retorna:
        tuple -> (stock_quantity: int, description: str)
    """

    stock_quantity = 0
    description = ""

    if not fetch_details:
        return stock_quantity, description

    try:
        detail_response = get_page_with_retries(book_url)
        if not detail_response:
            return stock_quantity, description

        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

        # ---- Extraer cantidad exacta de stock ----
        stock_tag = detail_soup.find('p', class_='instock availability')
        if stock_tag:
            stock_text = stock_tag.text.strip()
            stock_match = re.search(r'\((\d+) available\)', stock_text)
            if stock_match:
                stock_quantity = int(stock_match.group(1))

        # ---- Extraer descripción ----
        desc_div = detail_soup.find('div', id='product_description')
        if desc_div:
            desc_p = desc_div.find_next_sibling('p')
            if desc_p:
                description = desc_p.text.strip()

    except Exception as e:
        # Aquí podrías usar logging en vez de print en un entorno productivo
        print(f"Error obteniendo detalles de {book_url}: {e}")

    return stock_quantity, description


def scrape_books(target_count=300, include_details=False):
    current_page_url = "page-1.html"
    
    base_url = "https://books.toscrape.com/catalogue/"
    extracted_data = {} # Usamos dict para deduplicación rápida usando product_url como llave
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    
    logging.info("Iniciando proceso de scraping...")
    
    while len(extracted_data) < target_count and current_page_url:
        url = base_url + current_page_url
        response = get_page_with_retries(url)
        
        if not response:
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        
        for book in books:
            if len(extracted_data) >= target_count:
                break
                
            # Extraer product_url para deduplicación
            book_url = base_url + book.h3.a['href']
            if book_url in extracted_data:
                continue

            stock_quantity, description = get_product_details(book_url, fetch_details=include_details)
                
            title = book.h3.a['title']
            price_text = book.find('p', class_='price_color').text
            price = float(price_text.replace('£', '').replace('Â', '')) # Limpiar moneda
            availability = book.find('p', class_='instock availability').text.strip()
            rating_class = book.p['class'][1]
            rating = rating_map.get(rating_class, 0)
            
            extracted_data[book_url] = {
                "title": title,
                "price": price,
                "availability": availability,
                "stock_quantity": stock_quantity,
                "description": description,      
                "rating": rating,
                "product_url": book_url
            }
            
        # Paginación
        next_button = soup.find('li', class_='next')
        if next_button:
            current_page_url = next_button.a['href']
        else:
            current_page_url = None

    # Guardar salidas
    df = pd.DataFrame(list(extracted_data.values()))
    df.to_csv('data/output/books.csv', index=False)
    df.to_json('data/output/books.json', orient='records')
    
    logging.info(f"Scraping completado. {len(df)} libros extraídos.")
    return df