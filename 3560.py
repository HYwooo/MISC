class Solution:
    def minCuttingCost(self, n: int, m: int, k: int) -> int:
        return max(k * (max(n, m) - k), 0)
        