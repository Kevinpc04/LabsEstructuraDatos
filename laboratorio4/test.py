import random
import unittest
import math
import os
import matplotlib.pyplot as plt
from typing import List, Tuple

# Ensure reproducibility
random.seed(42)

# Import the Quadtree implementation
from QuadTree import QuadTreeNode, euclidean_distance, brute_range, brute_k_nearest, sorted_by_distance

Point = Tuple[float, float]

def generate_points(n: int, x_max: float = 10000.0, y_max: float = 10000.0) -> List[Point]:
    """Generate *n* random points inside the rectangle [0, x_max] x [0, y_max]."""
    return [(random.uniform(0, x_max), random.uniform(0, y_max)) for _ in range(n)]

class TestQuadTree(unittest.TestCase):
    def setUp(self):
        # Small dataset for basic correctness tests
        self.points = generate_points(200)
        self.root = QuadTreeNode((0.0, 10000.0, 0.0, 10000.0))
        for p in self.points:
            inserted = self.root.insert(p)
            self.assertTrue(inserted, f"Point {p} should be inside root bounds")

    def test_range_query_correctness(self):
        center = (5000.0, 5000.0)
        radius = 1500.0
        qt_result = self.root.query_range(center, radius)
        brute_result = brute_range(self.points, center, radius)
        # Compare as unordered collections
        self.assertCountEqual(qt_result, brute_result)
        # Also test ordering helper
        ordered_qt = sorted_by_distance(qt_result, center)
        ordered_brute = sorted_by_distance(brute_result, center)
        self.assertEqual(ordered_qt, ordered_brute)

    def test_k_nearest_correctness(self):
        target = (4000.0, 3000.0)
        k = 5
        qt_knn = self.root.k_nearest(target, k)
        brute_knn = brute_k_nearest(self.points, target, k)
        self.assertEqual(qt_knn, brute_knn)

    def test_nearest_single(self):
        target = (8000.0, 2000.0)
        nn = self.root.nearest(target)
        brute_nn = brute_k_nearest(self.points, target, 1)[0]
        self.assertEqual(nn, brute_nn)

    def test_max_depth_prevents_infinite_subdivision(self):
        # Create many points with identical coordinates to force deep subdivision
        identical_point = (5000.0, 5000.0)
        root = QuadTreeNode((0.0, 10000.0, 0.0, 10000.0))
        for _ in range(50):
            root.insert(identical_point)
        # The tree should not exceed MAX_DEPTH
        def max_depth(node):
            if node.children is None:
                return node.depth
            return max(max_depth(c) for c in node.children)
        depth = max_depth(root)
        self.assertLessEqual(depth, QuadTreeNode.MAX_DEPTH)

    def test_insert_out_of_bounds(self):
        # Create a root with defined bounds
        root = QuadTreeNode((0.0, 10000.0, 0.0, 10000.0))
        # Point outside the bounds should not be inserted
        outside_point = (15000.0, -500.0)
        inserted = root.insert(outside_point)
        self.assertFalse(inserted, "Insert should return False for points outside the root bounds")
        # Tree should remain empty
        self.assertEqual(root.points, [], "Root should have no points after failed insert")

    def test_range_zero_radius(self):
        # Use the existing set of points from setUp
        centre = self.points[0]  # pick a known point
        # radius 0 should return only points that exactly match the centre
        result = self.root.query_range(centre, 0.0)
        # The result may contain the centre point (if it was inserted)
        self.assertTrue(all(p == centre for p in result), "Zero‑radius range should return only exact matches")
        # Verify that brute‑force behaves the same
        brute_res = brute_range(self.points, centre, 0.0)
        self.assertCountEqual(result, brute_res)

    def test_empty_tree_queries(self):
        empty_root = QuadTreeNode((0.0, 10000.0, 0.0, 10000.0))
        centre = (5000.0, 5000.0)
        # Range query on empty tree returns empty list
        self.assertEqual(empty_root.query_range(centre, 500.0), [], "Empty tree range query should return []")
        # Nearest neighbor on empty tree returns None
        self.assertIsNone(empty_root.nearest(centre), "Nearest on empty tree should be None")
        # k‑nearest on empty tree returns empty list
        self.assertEqual(empty_root.k_nearest(centre, 3), [], "k‑nearest on empty tree should return []")
    
    def test_visualization(self):
        # Simple visual sanity check – generate a figure and ensure it saves without error
        plt.figure(figsize=(6,6))
        # Plot points
        xs, ys = zip(*self.points)
        plt.scatter(xs, ys, s=10, c='blue', label='Points')
        # Plot node boundaries recursively
        def draw_bounds(node):
            xmin, xmax, ymin, ymax = node.bounds
            plt.plot([xmin, xmax, xmax, xmin, xmin], [ymin, ymin, ymax, ymax, ymin], 'k-')
            if node.children:
                for child in node.children:
                    draw_bounds(child)
        draw_bounds(self.root)
        plt.title('QuadTree bounds and points')
        plt.legend()
        os.makedirs('figuras', exist_ok=True)
        out_path = os.path.join(os.getcwd(), 'figuras', 'visualization_test.png')
        plt.savefig(out_path)
        plt.close()
        self.assertTrue(os.path.exists(out_path))
        # Keep the generated figure for repository inclusion

if __name__ == '__main__':
    unittest.main()
