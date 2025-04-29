import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import zipfile

def get_domain_name(url):
    """Extract the domain name from a given URL."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    domain = domain.replace("www.", "")
    return domain.split('.')[0]

def extract_visible_text(soup):
    """Extract all visible text from a BeautifulSoup object."""
    # Remove script and style elements
    for element in soup(["script", "style", "noscript", "iframe", "svg"]):
        element.decompose()

    # Get text
    texts = soup.stripped_strings
    visible_text = ' '.join(texts)
    return visible_text

def count_words_segments(text):
    """Count the number of words and estimate number of segments."""
    words = re.findall(r'\w+', text)
    word_count = len(words)

    # Segments estimation based on sentence endings
    segments = re.split(r'[.!?。\n]+', text)
    segment_count = len([seg for seg in segments if seg.strip()])

    return word_count, segment_count

def detect_media(soup):
    """Detect if page has media files (images or videos)."""
    has_images = bool(soup.find_all("img"))
    has_videos = bool(soup.find_all("video"))
    return has_images or has_videos

def zip_html_folders(language_folders, output_zip_folder):
    """Create zipped folders for each language."""
    zip_paths = {}
    os.makedirs(output_zip_folder, exist_ok=True)

    for lang, path in language_folders.items():
        zip_filename = os.path.join(output_zip_folder, f"{lang}_pages.zip")
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, path)
                    zipf.write(file_path, arcname)
        zip_paths[lang] = zip_filename

    return zip_paths
