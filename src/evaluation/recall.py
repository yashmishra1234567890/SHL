def recall_at_k(predicted: list, relevant: list, k: int = 10) -> float:
    predicted_at_k = predicted[:k]
    hits = len(set(predicted_at_k) & set(relevant))
    return hits / len(relevant) if relevant else 0.0


def mean_recall_at_k(results: list, k: int = 10) -> float:
    if not results:
        return 0.0
    return sum(results) / len(results)
