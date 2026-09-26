"""
Algorithms Implementation in Python
==================================================

1. Binary Search: Efficiently find an element in a sorted list (O(log n)).
2. Prism Calculations: Calculate geometry metrics for a prism.
"""

# ==================== BINARY SEARCH ====================

def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


# ==================== PRISM ALGORITHM ====================

def prism_metrics(base_area, perimeter, height):
    """
    Calculates metrics for a right prism.
    
    Args:
        base_area (float): Area of the base polygon
        perimeter (float): Perimeter of the base polygon
        height (float): Height of the prism
        
    Returns:
        dict: Lateral area, total surface area, and volume
    """
    lateral_area = perimeter * height
    total_surface_area = lateral_area + (2 * base_area)
    volume = base_area * height
    
    return {
        "lateral_area": lateral_area,
        "total_surface_area": total_surface_area,
        "volume": volume
    }


# ==================== MAIN / TESTS ====================

if __name__ == "__main__":
    print("--- Binary Search Test ---")
    arr = [1, 3, 5, 7, 9]
    print(f"Index of 7: {binary_search(arr, 7)}")
    
    print("\n--- Prism Metric Test ---")
    # Example: A triangular prism with base area 6, perimeter 12, height 10
    metrics = prism_metrics(base_area=6.0, perimeter=12.0, height=10.0)
    for key, value in metrics.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
