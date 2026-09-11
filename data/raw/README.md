# Raw Dataset Instructions

## Dataset Information
* **Name**: Customer Support on Twitter (`twcs.csv`)
* **Source**: Kaggle (`thoughtvector/customer-support-on-twitter`)
* **Size**: Approximately 5.1 GB (approx. 2.8 million tweets)

## Why is this file excluded from Git?
The raw `twcs.csv` dataset is intentionally excluded from version control via `.gitignore` for two primary reasons:
1. **Repository Size**: Git is not designed to track multi-gigabyte monolithic CSV files, which would degrade clone speeds and exceed GitHub repository file limits.
2. **Licensing & Distribution**: Best practices require downloading original third-party benchmark datasets directly from their primary source.

## How to Obtain and Place the Dataset
1. Download the dataset from Kaggle:
   * **Direct URL**: [Customer Support on Twitter on Kaggle](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter)
   * **Kaggle CLI**:
     ```bash
     kaggle datasets download -d thoughtvector/customer-support-on-twitter
     ```
2. Extract the archive (`customer-support-on-twitter.zip`).
3. Place the extracted CSV file at:
   ```
   data/raw/twcs.csv
   ```

## Verification
Ensure the file is present at `data/raw/twcs.csv` before running the Phase 2 dataset audit or brand extraction scripts.
