import os
import requests
import xml.etree.ElementTree as ET
from src.config import HEADERS, NAMESPACES


def get_project_root():
    """Finds the project root from src/tools/utils.py"""
    current_file = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))


def download_file(url, path):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            with open(path, "wb") as f:
                f.write(resp.content)
            return resp.content
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return None


def parse_law_details(xml_bytes):
    """Extracts Title and Article count from XML."""
    try:
        root = ET.fromstring(xml_bytes)
        title_node = root.find(".//ml:htitle[@name='predpisNadpis']", NAMESPACES)
        articles = root.findall(".//ml:hcontainer[@name='clanok']", NAMESPACES)

        return {
            "title": title_node.text.strip() if title_node is not None else "Unknown",
            "article_count": len(articles)
        }
    except:
        return {"title": "Parse Error", "article_count": 0}