"""Author the illustrative SoD conflict list: seeded, disjoint pairs among the 12 highest-volume ROLE_FAMILY ids.
IDs are anonymised, so which pairs truly conflict is unknowable; this rule is reproducible and disclosed."""
import random

def pick_pairs(families_by_volume, n_pairs=6, seed=42):
    pool = list(families_by_volume[:12]); random.Random(seed).shuffle(pool)
    return [tuple(sorted(pool[i:i + 2])) for i in range(0, 2 * n_pairs, 2)]
