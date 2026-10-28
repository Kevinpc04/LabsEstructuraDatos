#   * capacity = 4 points per node
#   * MAX_DEPTH = 20 to avoid infinite subdivision when points are identical/very close
#   * insert, query_range, nearest, k_nearest
#   * helper functions for distance calculations and point ordering
#
# The tree works with Euclidean coordinates (meters). All distances are in the same unit.

import math
import heapq
from typing import List, Tuple, Optional

Point = Tuple[float, float]


def euclidean_distance(p1: Point, p2: Point) -> float:
    """Return Euclidean distance between two points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


class QuadTreeNode:
    """Node of a Quadtree.

    Attributes
    ----------
    bounds: Tuple[float, float, float, float]
        (xmin, xmax, ymin, ymax) defining the rectangular region.
    points: List[Point]
        Points stored directly in this node (until capacity is exceeded).
    children: Optional[Tuple[QuadTreeNode, QuadTreeNode, QuadTreeNode, QuadTreeNode]]
        Quadrants ordered as (NE, NW, SW, SE) – None if leaf.
    depth: int
        Current depth of the node (root = 0).
    """

    MAX_CAPACITY = 4
    MAX_DEPTH = 20

    def __init__(self, bounds: Tuple[float, float, float, float], depth: int = 0):
        self.bounds = bounds
        self.points: List[Point] = []
        self.children: Optional[Tuple[QuadTreeNode, QuadTreeNode, QuadTreeNode, QuadTreeNode]] = None
        self.depth = depth

    # ---------------------------------------------------------------------
    # Helper geometry utilities
    # ---------------------------------------------------------------------
    def _contains(self, point: Point) -> bool:
        xmin, xmax, ymin, ymax = self.bounds
        return xmin <= point[0] <= xmax and ymin <= point[1] <= ymax

    def _intersects_circle(self, center: Point, radius: float) -> bool:
        """Check whether the node rectangle intersects a circle.
        Used for pruning in range queries.
        """
        xmin, xmax, ymin, ymax = self.bounds
        cx, cy = center
        # Find the closest point on the rectangle to the circle centre
        closest_x = max(xmin, min(cx, xmax))
        closest_y = max(ymin, min(cy, ymax))
        return euclidean_distance((closest_x, closest_y), center) <= radius

    def _subdivide(self):
        """Create four children covering the current bounds.
        The subdivision stops when MAX_DEPTH is reached.
        """
        if self.depth >= QuadTreeNode.MAX_DEPTH:
            return  # do not subdivide further
        xmin, xmax, ymin, ymax = self.bounds
        xmid = (xmin + xmax) / 2.0
        ymid = (ymin + ymax) / 2.0
        ne = QuadTreeNode((xmid, xmax, ymid, ymax), self.depth + 1)
        nw = QuadTreeNode((xmin, xmid, ymid, ymax), self.depth + 1)
        sw = QuadTreeNode((xmin, xmid, ymin, ymid), self.depth + 1)
        se = QuadTreeNode((xmid, xmax, ymin, ymid), self.depth + 1)
        self.children = (ne, nw, sw, se)
        # Re‑insert existing points into appropriate children
        old_points = self.points
        self.points = []
        for pt in old_points:
            self._insert_into_children(pt)

    def _insert_into_children(self, point: Point) -> bool:
        """Try to insert the point into one of the children.
        Returns True if insertion succeeded.
        """
        if not self.children:
            return False
        for child in self.children:
            if child._contains(point):
                child.insert(point)
                return True
        # Should never happen if geometry is consistent
        return False

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def insert(self, point: Point) -> bool:
        """Insert a point into the quadtree.
        Returns True on success, False if the point lies outside the root bounds.
        """
        if not self._contains(point):
            return False
        # If leaf and capacity not exceeded, store directly
        if self.children is None:
            if len(self.points) < QuadTreeNode.MAX_CAPACITY or self.depth >= QuadTreeNode.MAX_DEPTH:
                self.points.append(point)
                return True
            # Capacity exceeded – need to subdivide
            self._subdivide()
        # Insert recursively into the appropriate child
        return self._insert_into_children(point)

    def query_range(self, center: Point, radius: float) -> List[Point]:
        """Return all points within *radius* of *center*.
        The result is **unsorted**; call ``sorted_by_distance`` if ordering is needed.
        """
        result: List[Point] = []
        if not self._intersects_circle(center, radius):
            return result  # prune entire subtree
        # Check points stored in this node
        for pt in self.points:
            if euclidean_distance(pt, center) <= radius:
                result.append(pt)
        # Recurse into children if they exist
        if self.children:
            for child in self.children:
                result.extend(child.query_range(center, radius))
        return result

    def _nearest_search(self, target: Point, heap: List[Tuple[float, Point]], k: int):
        """Recursive helper for k‑nearest search.
        ``heap`` is a max‑heap (negative distance) limited to size *k*.
        """
        # Prune if this node's rectangle is farther than the farthest candidate
        if self.children:
            # Compute minimal possible distance from target to rectangle
            xmin, xmax, ymin, ymax = self.bounds
            cx, cy = target
            dx = max(xmin - cx, 0, cx - xmax)
            dy = max(ymin - cy, 0, cy - ymax)
            min_dist_sq = dx * dx + dy * dy
            if len(heap) == k:
                farthest = -heap[0][0]
                if min_dist_sq > farthest * farthest:
                    return  # cannot improve existing candidates
        # Check points in this node
        for pt in self.points:
            dist = euclidean_distance(pt, target)
            if len(heap) < k:
                heapq.heappush(heap, (-dist, pt))
            else:
                if dist < -heap[0][0]:
                    heapq.heapreplace(heap, (-dist, pt))
        # Recurse into children (order does not matter for correctness)
        if self.children:
            for child in self.children:
                child._nearest_search(target, heap, k)

    def k_nearest(self, target: Point, k: int = 1) -> List[Point]:
        """Return the *k* nearest points to *target* (ordered from closest to farthest)."""
        if k <= 0:
            return []
        heap: List[Tuple[float, Point]] = []  # max‑heap using negative distances
        self._nearest_search(target, heap, k)
        # Convert heap to sorted list (ascending distance)
        result = [pt for (_, pt) in sorted(heap, key=lambda x: -x[0])]
        return result

    # Convenience wrapper for single nearest neighbor
    def nearest(self, target: Point) -> Optional[Point]:
        nearest_pts = self.k_nearest(target, k=1)
        return nearest_pts[0] if nearest_pts else None


# ---------------------------------------------------------------------------
# Utility functions working on the raw list of points (brute‑force equivalents)
# ---------------------------------------------------------------------------

def brute_range(points: List[Point], center: Point, radius: float) -> List[Point]:
    return [p for p in points if euclidean_distance(p, center) <= radius]


def brute_k_nearest(points: List[Point], target: Point, k: int) -> List[Point]:
    sorted_pts = sorted(points, key=lambda p: euclidean_distance(p, target))
    return sorted_pts[:k]


def sorted_by_distance(points: List[Point], center: Point) -> List[Point]:
    """Return *points* ordered by distance to *center* (closest first)."""
    return sorted(points, key=lambda p: euclidean_distance(p, center))

# End of QuadTree.py
