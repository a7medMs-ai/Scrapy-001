import streamlit as st
import os
import shutil
from crawler.spider import run_spider
from analyzer.content_analyzer import analyze_pages
from report.report_generator import generate_excel_report
from utils.helpers import get_domain_name, zip_html_folders
from datetime import datetime

# Streamlit page config
st.set_page_config(page_title="Web Scrapy Tool", layout="wide")

# Sidebar Navigation
menu = st.sidebar.radio("Navigation", ["🕸️ App", "ℹ️ About"])

# Paths
OUTPUT_DIR = "output"
HTML_DIR = os.path.join(OUTPUT_DIR, "html_pages")
ZIP_DIR = os.path.join(OUTPUT_DIR, "zips")
EXCEL_DIR = os.path.join(OUTPUT_DIR, "reports")
AUDIO_PATH = "static/audio/finish_sound.mp3"

# Ensure output folders exist
for folder in [HTML_DIR, ZIP_DIR, EXCEL_DIR]:
    os.makedirs(folder, exist_ok=True)

# APP PAGE
if menu == "🕸️ App":
    st.title("🌐 Website Localization Analysis Tool")
    st.markdown("This tool crawls websites and prepares reports for translation estimation.")

    url = st.text_input("Enter Website URL", placeholder="https://www.example.com")

    crawl_mode = st.radio("Crawl Mode", ["Full Website", "Limit to 3 Levels"], index=0)

    if st.button("Start Analysis"):
        if not url.strip():
            st.warning("⚠️ Please enter a valid URL.")
        else:
            st.info("🔍 Starting analysis. This may take a few minutes...")

            # Clean previous output
            shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
            for folder in [HTML_DIR, ZIP_DIR, EXCEL_DIR]:
                os.makedirs(folder, exist_ok=True)

            domain = get_domain_name(url)
            depth = 3 if crawl_mode == "Limit to 3 Levels" else None

            # Run crawler
            run_spider(start_url=url, depth_limit=depth)

            # Analyze crawled pages
            report_data, language_folders = analyze_pages(HTML_DIR)

            # Generate Excel report
            excel_file_name = f"website_{domain}_Scrapy.xlsx"
            excel_path = os.path.join(EXCEL_DIR, excel_file_name)
            generate_excel_report(report_data, excel_path)

            # Zip per-language HTML folders
            zip_paths = zip_html_folders(language_folders, ZIP_DIR)

            # Play notification sound
            if os.path.exists(AUDIO_PATH):
                with open(AUDIO_PATH, 'rb') as audio_file:
                    st.audio(audio_file.read(), format="audio/mp3")

            st.success("✅ Analysis completed!")

            # Download buttons
            st.markdown("### 📥 Download Files")

            with open(excel_path, "rb") as f:
                st.download_button(
                    label="📊 Download Excel Report",
                    data=f,
                    file_name=excel_file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            for lang, zip_file in zip_paths.items():
                with open(zip_file, "rb") as zf:
                    st.download_button(
                        label=f"📦 Download {lang.upper()} ZIP",
                        data=zf,
                        file_name=os.path.basename(zip_file),
                        mime="application/zip"
                    )

# ABOUT PAGE
elif menu == "ℹ️ About":
    st.title("ℹ️ About Web Scrapy Tool")
    st.markdown("""
### What is this tool?
A smart solution for localization engineers to crawl websites and estimate translation effort based on word count, content types, media, and structure.

### Features
- Full HTML crawl of multilingual websites.
- Word and segment count with per-language analysis.
- Generates Excel reports with totals.
- ZIP export per language.
- Compatible with Trados / memoQ workflows.

### Developer Info
**Ahmed Mostafa Saad**  
Localization Engineering & TMS Support Team Lead  
📧 [ahmed.mostafa@future-group.com](mailto:ahmed.mostafa@future-group.com)  
🏢 Future Group Translation Services
    """)
