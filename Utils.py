def positive_part(x):
    return x if x > 0 else 0
    
from itertools import combinations

def get_subsets(li, size=3):
    return set(combinations(li, size))