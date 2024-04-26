import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time


class TransfereGovScraper:
    def __init__(self):
        self.download_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
        self.url_base = "https://discricionarias.transferegov.sistema.gov.br"
        self.driver = None
        self.file_counter = 1
        self.list_of_files = []

    def setup_driver(self):
        try:
            chrome_driver_path = '/opt/selenium-drivers/chrome/chromedriver'
            chrome_service = Service(chrome_driver_path)

            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--verbose')
            chrome_options.add_experimental_option("prefs", {
                "download.default_directory": self.download_folder,
                'directory_upgrade': True,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': True
            })

            self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        except WebDriverException as e:
            print(f"Erro ao inicializar o WebDriver: {e}")

    def scrape_download_links(self, convenio):
        try:
            setattr(self, "convenio", convenio)

            if not self.driver:
                self.setup_driver()

            url = (f"{self.url_base}/voluntarias/ConsultarProposta/ResultadoDaConsultaDeConvenioSelecionarConvenio.do"
                   f"?sequencialConvenio={convenio}&Usr=guest&Pwd=guest")

            self.driver.get(url)

            button_links = self.driver.find_elements(By.CLASS_NAME, 'buttonLink')

            links_for_download = []
            for link in button_links:
                download_link = link.get_attribute('href')
                if download_link and download_link.startswith("javascript:document.location="):
                    path = download_link.replace("javascript:document.location='", "").rstrip("'%27;")
                    links_for_download.append(path)

            return links_for_download

        except WebDriverException as e:
            print(f"Erro durante o scraping: {e}")
            return []

    def download_files(self, download_links):
        try:
            if not os.path.exists(self.download_folder):
                os.makedirs(self.download_folder)

            for link in download_links:
                full_url = f"{self.url_base}{link}"

                self.driver.get(full_url)

                time.sleep(5)

                if not os.path.exists(self.download_folder): os.makedirs(self.download_folder)

                downloaded_files = [f for f in os.listdir(self.download_folder) if os.path.isfile(os.path.join(self.download_folder, f))]

                for file in downloaded_files:
                    if not file in self.list_of_files:
                        file_name, file_extension = os.path.splitext(file)

                        original_file_path = os.path.join(self.download_folder, file)

                        new_file_name = f"arquivo_{self.convenio}_{self.file_counter}{file_extension}"

                        convenio_path = os.path.join(self.download_folder, self.convenio)

                        if not os.path.exists(convenio_path): os.makedirs(convenio_path)

                        new_file_path = os.path.join(convenio_path, new_file_name)

                        os.rename(original_file_path, new_file_path)

                        self.list_of_files.append(file)

                        self.file_counter += 1

        except WebDriverException as e:
            print(f"Erro durante o download dos arquivos: {e}")

    def close_driver(self):
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    convenio = input("Digite o número do convênio: ")

    scraper = TransfereGovScraper()

    try:
        download_links = scraper.scrape_download_links(convenio)

        if download_links:
            print("Links de Download:")
            for link in download_links:
                print(link)

        scraper.download_files(download_links)

    finally:
        scraper.close_driver()
