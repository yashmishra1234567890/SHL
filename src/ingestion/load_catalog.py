import sys
import re
from pathlib import Path
import pandas as pd

try:
    from src.utils.text import clean_text
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from src.utils.text import clean_text


DEFAULT_CATALOG_PATH = "data/processed/shl_catalog_clean.csv"


def _resolve_path(path: str | Path) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p

    project_root = Path(__file__).resolve().parents[2]
    return project_root / p


def load_catalog(path: str | Path = DEFAULT_CATALOG_PATH) -> pd.DataFrame:
    file_path = _resolve_path(path)
    
    if file_path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    elif file_path.suffix.lower() == '.json':
        df = pd.read_json(file_path)
    else:
        df = pd.read_csv(file_path)

    column_map = {
        "Solution Name": "name",
        "Product Name": "name",
        "Assessment Name": "name",
        "Title": "name",
        "title": "name",
        
        "Solution Description": "description",
        "Product Description": "description",
        "Description": "description",
        "Details": "description",
        "content": "description",
        
        "Link": "url",
        "URL": "url",
        "Product Link": "url",
        
        "Test Type": "test_type",
        "Type": "test_type",
        
        "Duration": "duration",
        "Time": "duration",
        
        "Remote Testing": "remote_support",
        "Remote": "remote_support",
        "remote_testing": "remote_support",
        
        "Adaptive/IRT": "adaptive_support",
        "Adaptive": "adaptive_support",
        "adaptive_irt": "adaptive_support"
    }
    
    df = df.rename(columns=column_map)

    # Ensure required columns exist
    required_cols = ["name", "description", "test_type", "url"]
    for col in required_cols:
        if col not in df.columns:
            # If missing, try to find a case-insensitive match
            found = False
            for existing_col in df.columns:
                if existing_col.lower() == col.lower():
                    df = df.rename(columns={existing_col: col})
                    found = True
                    break
            if not found:
                df[col] = "" # Fill missing with empty string

    # Map remote_testing/adaptive_irt if they still exist under old names (fallback)
    if "remote_support" not in df.columns and "remote_testing" in df.columns:
        df["remote_support"] = df["remote_testing"]

    if "adaptive_support" not in df.columns and "adaptive_irt" in df.columns:
        df["adaptive_support"] = df["adaptive_irt"]

    # Extract duration from description if missing
    # Some datasets embed the duration in the description text
    if "description" in df.columns:
        def extract_duration(text):
            if not isinstance(text, str):
                return None
            # Look for "Approximate Completion Time in minutes = <value>"
            match = re.search(r"Approximate Completion Time in minutes\s*=\s*(.+?)(?:\s+Test Type|$)", text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                # Remove trailing "minutes" if present
                val = re.sub(r"\s*minutes\.?$", "", val, flags=re.IGNORECASE)
                return val
            return None

        # If duration column doesn't exist, create it
        if "duration" not in df.columns:
            df["duration"] = ""
            
        # Fill missing duration where it is NaN or empty
        mask = df["duration"].isna() | (df["duration"] == "") | (df["duration"] == "N/A")
        extracted = df.loc[mask, "description"].apply(extract_duration)
        df.loc[mask, "duration"] = extracted.fillna("N/A")

    # Create combined text for embedding
    # We combine name, description, and test type to give the model full context
    df["combined_text"] = (
        df["name"].fillna("") + " " +
        df["description"].fillna("") + " " +
        df["test_type"].fillna("")
    )

    # Clean the text (remove special chars, extra spaces, etc.)
    df["combined_text"] = df["combined_text"].apply(clean_text)
    return df


if __name__ == "__main__":
    from src.config import CATALOG_PATH

    print(f"Loading catalog from: {CATALOG_PATH}")
    df = load_catalog(CATALOG_PATH)
    print(df.head())
    print(f"\nSuccessfully loaded {len(df)} rows.")
