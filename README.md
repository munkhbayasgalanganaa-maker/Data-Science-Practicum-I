# AI-Driven Analysis of Tariff and CPI

This project studies one simple question:

Do U.S. tariffs related to CPI (consumer prices), or is CPI history a stronger predictor?

## What this project does

- Uses U.S. public data (USITC tariff data and BLS CPI data)
- Cleans and merges the data by category and month
- Trains 6 models:
  - Linear Regression
  - Ridge
  - Lasso
  - Elastic Net
  - Random Forest
  - Gradient Boosting
- Compares two setups:
  - Baseline: tariff-only features
  - Enhanced: tariff + CPI lag + seasonality features

## Main result (simple)

- Tariff-only models are weak
- Enhanced models are much better
- This means tariffs matter, but CPI history is a stronger short-run predictor

## Project files

- `AI_Driven Analysis of CPI and Tariff_Ganaa_Code.ipynb` — main notebook
- `tariff_cpi_app.py` — Streamlit app
- `AI-Driven Analysis of Tariff and CPI_Ganaa.pptx` — presentation slides
- `Data_Science_Practicum_Proposal_Mugi_Ganaa (6).pdf` — proposal PDF
- `raw_data/` — original data
- `processed_data/` — cleaned and merged data
- `results/` — model outputs and figures
- `docs/` — supporting notes/files

## How to run

### 1) Run notebook

Open this file and run cells:

- `AI_Driven Analysis of CPI and Tariff_Ganaa_Code.ipynb`

### 2) Run app

From project folder:

```bash
python -m streamlit run tariff_cpi_app.py --server.port 8501
```

Then open:

- http://localhost:8501

## Notes

- `localhost` works only on your own computer
- If you want a public app link, you need to deploy it (for example, Streamlit Community Cloud)
