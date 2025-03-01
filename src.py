import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from github import Github
import json

# Configura el ChromeDriver
service = Service(ChromeDriverManager().install())
options = Options()
options.add_argument("--headless")  # Modo sin cabeza

# Inicia el navegador
driver = webdriver.Chrome(service=service, options=options)

# URL que deseas scrapear
url = "https://exchangemonitor.net/dolar-venezuela"
driver.get(url)

# Espera a que cargue la página
driver.implicitly_wait(10)

# Obtener el contenido HTML de la página
html = driver.page_source

# Usa BeautifulSoup para analizar el HTML
soup = BeautifulSoup(html, 'html.parser')

# Encuentra todos los contenedores con la clase "rate-container"
containers = driver.find_elements(By.CLASS_NAME, "rate-container")

# Guardar los datos del scraping
scraped_data = []

for container in containers:
    try:
        title = container.find_element(By.CLASS_NAME, 'text-title').text if container.find_element(By.CLASS_NAME, 'text-title') else "No encontrado"
        subtitle = container.find_element(By.CLASS_NAME, 'text-subtitle').text if container.find_element(By.CLASS_NAME, 'text-subtitle') else "No encontrado"
        rate = container.find_element(By.CLASS_NAME, 'data-rate').text if container.find_element(By.CLASS_NAME, 'data-rate') else "No encontrado"
        change = container.find_element(By.CLASS_NAME, 'data-change').text if container.find_element(By.CLASS_NAME, 'data-change') else "No encontrado"
        date = container.find_element(By.CLASS_NAME, 'rate-date').text if container.find_element(By.CLASS_NAME, 'rate-date') else "No encontrado"
        image_url = container.find_element(By.CLASS_NAME, 'logo').find_element(By.TAG_NAME, 'img').get_attribute('src') if container.find_element(By.CLASS_NAME, 'logo').find_element(By.TAG_NAME, 'img') else "No encontrado"

        scraped_data.append({
            "title": title,
            "subtitle": subtitle,
            "rate": rate,
            "change": change,
            "date": date,
            "image_url": image_url
        })
    except Exception as e:
        print(f"Error al extraer datos de un contenedor: {e}")

# Cierra el navegador
driver.quit()

# Conectar con GitHub
token = os.getenv('BARALT')  # Lee el token desde la variable de entorno
if not token:
    print("Token no encontrado. Asegúrate de establecer el secret BARALT.")
    exit(1)

repo_name = "api-v.3"  # Nombre del repositorio
file_path = "data.json"  # Ruta del archivo donde se guardarán los datos

# Autenticación y acceso al repositorio
g = Github(token)
repo = g.get_repo(repo_name)

# Intentar crear el archivo o actualizarlo
try:
    file = repo.get_contents(file_path)
    # Si el archivo existe, actualizamos
    repo.update_file(file.path, "Actualización de datos", json.dumps(scraped_data, indent=4), file.sha)
    print("Archivo actualizado con éxito.")
except Exception as e:
    print(f"Error al actualizar el archivo: {e}")
    # Si no existe, lo creamos
    try:
        repo.create_file(file_path, "Creación de archivo de datos", json.dumps(scraped_data, indent=4))
        print("Archivo creado con éxito.")
    except Exception as e:
        print(f"Error al crear el archivo: {e}")
