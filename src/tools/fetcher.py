import os
import datetime
import xml.etree.ElementTree as ET
from src.config import BASE_XML_URL, BASE_STATIC_PDF_URL, NAMESPACES
from src.tools.utils import get_project_root, download_file, parse_law_details


def fetch_specific_law(year: int, law_id: int) -> str:
    """Downloads XML and attempts to find the PDF for a specific law."""
    print(f"\n[Tool] Fetching Slov-Lex Law: {year}/{law_id}...")

    base_dir = os.path.join(get_project_root(), "downloads", str(year), str(law_id))
    os.makedirs(base_dir, exist_ok=True)

    xml_url = f"{BASE_XML_URL}/{year}/{law_id}/vyhlasene_znenie.xml"
    xml_path = os.path.join(base_dir, f"law_{year}_{law_id}.xml")

    xml_content = download_file(xml_url, xml_path)
    if not xml_content:
        return f"Failed to find XML for Law {year}/{law_id}."

    pdf_name = _guess_and_download_pdf(xml_content, year, law_id, base_dir)
    law_info = parse_law_details(xml_content)

    return (
        f"SUCCESS. Law {year}/{law_id} downloaded.\n"
        f"Title: {law_info['title']}\n"
        f"Articles: {law_info['article_count']}\n"
        f"PDF: {pdf_name}\n"
        f"Path: {base_dir}"
    )


def _guess_and_download_pdf(xml_content, year, law_id, save_dir):
    """Internal helper to guess PDF date."""
    candidate_dates = _extract_dates(xml_content)

    attempts = set()
    for date_obj in candidate_dates:
        for offset in range(-2, 3):
            attempts.add((date_obj + datetime.timedelta(days=offset)).strftime("%Y%m%d"))

    for date_str in sorted(attempts):
        filename = f"ZZ_{year}_{law_id}_{date_str}.pdf"
        url = f"{BASE_STATIC_PDF_URL}/{year}/{law_id}/{filename}"
        path = os.path.join(save_dir, filename)

        if download_file(url, path):
            print(f"✅ PDF Found: {filename}")
            return filename

    print(f"❌ No valid PDF found (tried {len(attempts)} dates)")
    return "Not Found"


def _extract_dates(xml_bytes):
    try:
        root = ET.fromstring(xml_bytes)
        dates = set()
        for meta in root.findall(".//ml:meta", NAMESPACES):
            prop = meta.get("property")
            content = meta.get("content")
            if prop in ["slovlex-owl:platny", "slovlex-owl:ucinny", "slovlex-owl:vyhlaseny"]:
                clean_date = content.split("zaciatok=")[-1].split(";")[0].strip() if "zaciatok=" in content else content
                try:
                    dates.add(datetime.datetime.strptime(clean_date.strip(), "%Y-%m-%d"))
                except ValueError:
                    pass
        return list(dates)
    except Exception:
        return []