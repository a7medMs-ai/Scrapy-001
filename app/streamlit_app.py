import streamlit as st
import os
import shutil
from crawler.spider import run_spider
from analyzer.content_analyzer import analyze_pages
from report.report_generator import generate_excel_report
from utils.helpers import get_domain_name, zip_html_folders
import time
from datetime import datetime
from pathlib import Path
import base64

# Set page configuration
st.set_page_config(page_title="Web Scrapy Tool", layout="wide")

# Sidebar Navigation
menu = st.sidebar.radio("Navigation", ["🕸️ App", "ℹ️ About"])

# Constants
OUTPUT_DIR = "output"
HTML_DIR = os.path.join(OUTPUT_DIR, "html_pages")
ZIP_DIR = os.path.join(OUTPUT_DIR, "zips")
EXCEL_DIR = os.path.join(OUTPUT_DIR, "reports")
AUDIO_FILE = "static/audio/finish_sound.mp3"

if menu == "🕸️ App":
    st.title("🌐 Website Localization Analysis Tool")
    st.markdown("Use this tool to crawl a website and generate a translation quote report.")

    url = st.text_input("Enter Website URL", placeholder="https://www.example.com")
    crawl_depth = st.radio("Crawl Mode", ["Full website", "Limit depth to 3 levels"], index=0)

    if st.button("Start Analysis"):
        if url:
            with st.spinner("Crawling and analyzing website... please wait."):
                # Create fresh folders
                for folder in [HTML_DIR, ZIP_DIR, EXCEL_DIR]:
                    shutil.rmtree(folder, ignore_errors=True)
                    os.makedirs(folder, exist_ok=True)

                domain = get_domain_name(url)

                # Crawl site
                run_spider(start_url=url, depth_limit=3 if crawl_depth == "Limit depth to 3 levels" else None)

                # Analyze downloaded pages
                report_data, language_folders = analyze_pages(HTML_DIR)

                # Generate Excel report
                excel_path = os.path.join(EXCEL_DIR, f"website_{domain}_Scrapy.xlsx")
                generate_excel_report(report_data, excel_path)

                # Zip folders by language
                zip_paths = zip_html_folders(language_folders, ZIP_DIR)

                # Play sound notification
                audio_file = open(AUDIO_FILE, 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')

                # Download options
                st.success("✅ Website processed successfully!")
                st.markdown("### Download Files")
                with open(excel_path, "rb") as f:
                    st.download_button("📊 Download Excel Report", f, file_name=os.path.basename(excel_path), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                for lang, path in zip_paths.items():
                    with open(path, "rb") as zf:
                        st.download_button(f"📦 Download {lang.upper()} ZIP", zf, file_name=os.path.basename(path), mime="application/zip")

        else:
            st.warning("Please enter a valid URL.")

elif menu == "ℹ️ About":
    st.title("ℹ️ About Web Scrapy Tool")
    st.markdown("""
### What is this tool?
This tool allows localization engineers to estimate the effort required to translate a website, by crawling it and producing detailed word/segment/media reports.

### Key Features
- Full HTML crawl of any website.
- Language-based file grouping.
- Word count and segment analysis.
- Export as Excel + ZIP (per language).
- Built for compatibility with CAT tools.

### Technical Details
- Built with Python, Scrapy, Streamlit.
- Word counting via Alfaaz + fallback methods.
- Static + dynamic (optional JS-rendered) pages support.

### Developer Info
**Ahmed Mostafa Saad**  
Localization Engineering & TMS Support Team Lead  
📧 [ahmed.mostafa@future-group.com](mailto:ahmed.mostafa@future-group.com)  
🌍 Future Group Translation Services
    """)
