# Amazon Best Selling Books ETL Pipeline

An automated, end-to-end Data Engineering pipeline built with Python and Pandas. This project automatically ingests raw Amazon bestseller data (2009–2019), standardizes schemas, computes key aggregated metrics, and exports structured results into flat CSV reports and a relational SQLite database.

The workflow is fully automated using GitHub Actions to execute on a scheduled daily CRON trigger inside a cloud environment.

---

## 🏗️ Project Architecture & Directory Structure

amazon_books_analysis/
├── .github/
│ └── workflows/
│ └── pipeline.yml # GitHub Actions automated daily workflow
├── data/
│ ├── raw/ # Raw downloaded dataset
│ └── processed/ # Cleaned dataset & SQLite database
├── src/
│ ├── **init**.py
│ └── main.py # Main ETL pipeline script
├── reports/ # Exported analytical CSV reports
├── .gitignore
├── README.md
└── requirements.txt # Python package dependencies

---

## ⚙️ Pipeline Stages & Features

1. Ingestion (Extract): Streams the raw bestseller CSV dataset from a remote endpoint using HTTP requests with custom headers.
2. Transformation (Transform):
   - Standardizes column naming conventions to snake_case.
   - Casts explicit numerical data types (float for prices/ratings, int for reviews).
   - Generates summary tables (author frequency, genre rating/pricing breakdowns, high-performing titles).
3. Storage (Load):
   - Saves processed datasets to data/processed/cleaned_bestsellers.csv.
   - Writes clean tables into an SQLite database (data/processed/amazon_books.db).
   - Generates executive summary CSV reports in reports/.
4. CI/CD Automation: Runs headlessly every midnight UTC via GitHub Actions with write permissions to commit updated artifacts back to the repository.

---

## 🚀 Local Installation & Execution

### 1. Clone the repository and set up environment

git clone https://github.com/Monim22/amazon-books-analysis.git
cd amazon-books-analysis

python3 -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

### 2. Run the pipeline manually

python src/main.py

---

## 📊 Output Deliverables

After execution, the following pipeline deliverables are produced:

- data/processed/cleaned_bestsellers.csv – Clean master dataset.
- data/processed/amazon_books.db – SQLite database storing the bestsellers table.
- reports/top_10_authors.csv – Top 10 authors ranked by total bestseller appearances.
- reports/genre_summary.csv – Comparison of price, rating, and review metrics between Fiction and Non-Fiction.
- reports/top_rated_books.csv – Top 10 highest-rated titles with a minimum threshold of 10,000 user reviews.
