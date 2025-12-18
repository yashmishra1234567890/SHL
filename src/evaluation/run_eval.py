import sys
import os
import json
import pandas as pd
from pathlib import Path
from tqdm import tqdm


project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.rag.rag_engine import AssessmentRecommendationEngine
from src.evaluation.recall import recall_at_k, mean_recall_at_k
from src.config import CATALOG_PATH

def load_ground_truth():
    if str(CATALOG_PATH).endswith('.json'):
        with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    else:
        df = pd.read_csv(CATALOG_PATH)
    
    if "title" in df.columns and "name" not in df.columns:
        df["name"] = df["title"]
    if "content" in df.columns and "description" not in df.columns:
        df["description"] = df["content"]
        
    test_cases = []
    for _, row in df.iterrows():
        if pd.notna(row.get('name')):
            test_cases.append({
                "query": row['name'],
                "relevant_ids": [row['name']],
                "type": "title"
            })
            
            if pd.notna(row.get('description')) and len(str(row['description'])) > 20:
                desc_query = str(row['description'])[:100]
                test_cases.append({
                    "query": desc_query,
                    "relevant_ids": [row['name']],
                    "type": "description"
                })
                
    return test_cases

def evaluate(k=10):
    print("Loading Engine...")
    engine = AssessmentRecommendationEngine()
    
    print("Loading Ground Truth...")
    test_cases = load_ground_truth()
    print(f"Found {len(test_cases)} test cases.")
    
    title_recalls = []
    desc_recalls = []
    
    print(f"Running Evaluation (k={k})...")
    for case in tqdm(test_cases):
        query = case['query']
        relevant = case['relevant_ids']
        
        results = engine.search(query, k=k)
        
        predicted = [doc.metadata.get('name') for doc in results]
        
        score = recall_at_k(predicted, relevant, k=k)
        
        if case['type'] == 'title':
            title_recalls.append(score)
        else:
            desc_recalls.append(score)
        
    mean_recall_title = mean_recall_at_k(title_recalls, k=k) if title_recalls else 0
    mean_recall_desc = mean_recall_at_k(desc_recalls, k=k) if desc_recalls else 0
    
    print(f"\nResults for k={k}:")
    print(f"Mean Recall (Title Queries): {mean_recall_title:.4f}")
    print(f"Mean Recall (Description Queries): {mean_recall_desc:.4f}")
    
    output_dir = project_root / "outputs"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "evaluation_results.csv"
    
    results_df = pd.DataFrame({
        "k": [k, k],
        "query_type": ["title", "description"],
        "mean_recall": [mean_recall_title, mean_recall_desc]
    })
    
    if output_file.exists():
        results_df.to_csv(output_file, mode='a', header=False, index=False)
    else:
        results_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

    output_file_2 = output_dir / "output.csv"
    if output_file_2.exists():
        results_df.to_csv(output_file_2, mode='a', header=False, index=False)
    else:
        results_df.to_csv(output_file_2, index=False)
    print(f"Results saved to {output_file_2}")

    output_json = output_dir / "output.json"
    new_data = results_df.to_dict(orient="records")
    
    if output_json.exists():
        with open(output_json, "r") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
        existing_data.extend(new_data)
        with open(output_json, "w") as f:
            json.dump(existing_data, f, indent=2)
    else:
        with open(output_json, "w") as f:
            json.dump(new_data, f, indent=2)
            
    print(f"Results saved to {output_json}")
    
    return mean_recall_title, mean_recall_desc

if __name__ == "__main__":
    # Clear previous results file if it exists to start fresh
    output_dir = Path(__file__).resolve().parents[2] / "outputs"
    output_file = output_dir / "evaluation_results.csv"
    output_file_2 = output_dir / "output.csv"
    output_file_3 = output_dir / "output.json"

    if output_file.exists():
        output_file.unlink()
    if output_file_2.exists():
        output_file_2.unlink()
    if output_file_3.exists():
        output_file_3.unlink()
        
    evaluate(k=5)
    evaluate(k=10)
