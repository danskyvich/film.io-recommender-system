import numpy as np
from pathlib import Path
import sys
import json
from scipy.sparse import load_npz, csr_matrix
from sklearn.metrics.pairwise import linear_kernel

# RECOMMENDER ENGINE
# import /artifacts data to this file

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

output_dir = PROJECT_ROOT / "artifacts"

film_ids = np.load(output_dir / "film_ids.npy") 
quality_values = np.load(output_dir / "quality_values.npy")
matrix = load_npz(output_dir / "tfid_matrix.npz")

def retrieve_sliced_corpus(positions: list[int], matrix: csr_matrix):
    if not positions: return []
    return matrix[positions]

def generate_recommendations(picked_ids: list[int], limit: int = 10):
    onboarding_positions = []
    for film_id in picked_ids:
        position = film_dict.get(film_id)
        if position is not None: onboarding_positions.append(position)
    
    if not onboarding_positions: return []
    sliced_corpus = matrix[onboarding_positions]
    
    similarity = linear_kernel(sliced_corpus, matrix)
    similarity_mean_scores = similarity.mean(axis=0)
    blended_array = 0.85 * similarity_mean_scores + 0.15 * quality_values
    blended_array[onboarding_positions] = -1

    sorted_blended_array = np.argsort(blended_array)[::-1]
    top_positions = sorted_blended_array[:limit]
    top_ids = film_ids[top_positions]
    top_scores = blended_array[top_positions]

    return list(zip([int(x) for x in top_ids], [float(x) for x in top_scores]))

try:
    with open(output_dir / "training_snapshot.json", encoding="utf-8") as file:
        metadata = json.load(file)

    film_dict = {film: position for position, film in enumerate(film_ids)}

    # sample films
    picked_films = [3933, 122, 497]
    recommendations = generate_recommendations(picked_films, limit=10)
    print(recommendations)

except FileNotFoundError as f:
    raise(f"{Path(__file__).name} not found. Error: {f}")
    sys.exit(1)