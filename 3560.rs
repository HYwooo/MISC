use std::cmp::max;
impl Solution {
    pub fn min_cutting_cost(n: i32, m: i32, k: i32) -> i64 {
        max(0,(k as i64 * (max(n,m)-k) as i64))
    }
}