from scrapegraphai.graphs import SmartScraperGraph
import PyPDF2
from scrapegraphai.graphs import JSONScraperGraph

# model_name = 'http://ollama:11434/'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY
model_name = 'llama3'  # REPLACE IT TO llama3 IF YOU RUN LOCALLY

# machine = 'ollama'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY
machine = 'localhost'  # REPLACE IT TO LOCALHOST IF YOU RUN LOCALLY


def sample_json(file_path):
    """
    Read the sample JSON file
    """
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text


def sample_pdf(pdf_file):
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text


class Scraper(object):
    def __init__(self):
        # Scraper configurations
        self.graph_config = {
            "llm": {
                "model": f"ollama/{model_name}",
                "temperature": 0,
                "format": "json",
                "base_url": f"http://{machine}:11434",
            },
            "embeddings": {
                "model": "ollama/nomic-embed-text",
                "base_url": f"http://{machine}:11434",
            },
            "verbose": True,
        }
        self.scraper = None

    def scrape_json(self, path_to_json):
        json_text = sample_json(path_to_json)
        self.scraper = JSONScraperGraph(
            prompt="List me all the titles",
            source=json_text,
            config=graph_config
        )
        result = self.scraper.run()
        return result

    def scrape_from_pdf(self, pdf_path, prompt):
        plain_text = sample_pdf(pdf_path)
        return self.scrape_from_plain_text(sample_text=plain_text, prompt=prompt)

    def scrape_from_plain_text(self, sample_text, prompt):
        self.scraper = smart_scraper_graph = SmartScraperGraph(
            prompt=prompt,
            source=sample_text,
            config=graph_config
        )
        result = self.scraper.run()
        return result

    def scrape_from_url(self, url, prompt):
        self.scraper = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=self.graph_config
        )
        result = self.scraper.run()
        print(result)
        return result
