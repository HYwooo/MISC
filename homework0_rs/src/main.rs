use std::f32;
use std::f64;

// 计算级数 Sn = Σ(1/(i²-1)) 从 i=2 到 n
// 从小到大累加计算
fn sn_small_to_big(n: i32) -> f32 {
    let mut sn: f32 = 0.0;
    // 注意：在Rust中，i32可能会溢出，但这里n最大为10000，i64更安全
    for i in 2..=n as i32 {
        sn += 1.0 / ((i * i - 1) as f32);
    }
    sn
}

// 从小到大累加计算（调试版本）
fn sn_small_to_big_debug(n: i32) -> f32 {
    let mut sn: f32 = 0.0;
    let mut sign_flip_count = 0;
    let mut zero_cross_count = 0;
    let mut first_negative = true;

    println!("=== 调试信息: n={} ===", n);

    for i in 2..=n as i64 {
        let old_sn = sn;
        let term = 1.0 / ((i * i - 1) as f32);
        sn += term;

        // 检测符号翻转
        if (old_sn > 0.0 && sn < 0.0) || (old_sn < 0.0 && sn > 0.0) {
            sign_flip_count += 1;
            if sign_flip_count <= 5 {
                println!(
                    "符号翻转 #{} at i={}, Sn从 {} 变为 {}, term={}",
                    sign_flip_count, i, old_sn, sn, term
                );
            }
        }

        // 检测过零点
        if old_sn * sn < 0.0 {
            zero_cross_count += 1;
            if zero_cross_count <= 3 {
                println!(
                    "过零点 #{} at i={}, Sn从 {} 变为 {}",
                    zero_cross_count, i, old_sn, sn
                );
            }
        }

        // 第一次变为负数
        if sn < 0.0 && first_negative {
            first_negative = false;
            let ulp = sn.abs() * (1.0 / (1 << 23) as f32);
            println!(
                "第一次变为负数: i={}, Sn={}, term={}, 累加器ULP≈{}",
                i, sn, term, ulp
            );
        }

        // 进度报告
        if i % 100000 == 0 {
            println!("进度: i={}/{}, Sn={}", i, n, sn);
        }
    }

    println!(
        "总计: 符号翻转 {} 次, 过零点 {} 次",
        sign_flip_count, zero_cross_count
    );
    println!("最终结果: Sn={}", sn);
    println!("=== 调试结束 ===\n");

    sn
}

// 从小到大累加计算（详细分析版本）
fn sn_small_to_big_detailed(n: i32) -> f32 {
    let mut sn: f32 = 0.0;
    let mut found_flip = false;

    println!("=== 详细分析: n={} ===", n);

    for i in 2..=n as i64 {
        let old_sn = sn;
        let term = 1.0 / ((i * i - 1) as f32);

        // 在关键区域进行详细分析
        if i >= 65530 && i <= 65542 {
            let actual_sum = old_sn + term;
            let ulp = sn.abs() * (1.0 / (1 << 23) as f32);

            println!(
                "i={}, old_Sn={}, term={} (2^{}), term/ULP={}, 数学和={}, 浮点和={}",
                i,
                old_sn,
                term,
                term.log2(),
                term / ulp,
                actual_sum,
                old_sn + term
            );

            if actual_sum > 0.0 && (old_sn + term) < 0.0 {
                println!("!!! 预测符号翻转 !!!");
            }
        }

        sn += term;

        // 检测实际符号翻转
        if old_sn > 0.0 && sn < 0.0 && !found_flip {
            found_flip = true;
            println!(
                "!!! 实际符号翻转 at i={}, 从 {} 到 {}, term={}",
                i, old_sn, sn, term
            );

            let ulp = old_sn.abs() * (1.0 / (1 << 23) as f32);
            println!(
                "分析: old_Sn={}, ULP≈{}, term={}, term/ULP={}",
                old_sn,
                ulp,
                term,
                term / ulp
            );

            // 在Rust中，我们可以使用to_bits来获取浮点数的位表示
            let old_bits = old_sn.to_bits();
            let new_bits = sn.to_bits();
            println!("二进制: old_Sn=0x{:x}, new_Sn=0x{:x}", old_bits, new_bits);
        }

        if found_flip && i > 65542 {
            break;
        }
    }

    println!("=== 详细分析结束 ===\n");
    sn
}

// 从大到小累加计算
fn sn_big_to_small(n: i32) -> f32 {
    let mut sn: f32 = 0.0;
    for i in (2..=n as i64).rev() {
        sn += 1.0 / ((i * i - 1) as f32);
    }
    sn
}

// 使用精确数学公式计算（双精度）
fn sn_accuracy(n: i32) -> f64 {
    // 精确公式: Sn = 0.5 * (1.5 - 1/n - 1/(n+1))
    0.5 * (1.5 - 1.0 / (n as f64) - 1.0 / ((n + 1) as f64))
}

fn main() {
    // 在Rust中，数组大小必须是编译时常量
    let mut sn_s2b = [0.0f32; 3];
    let mut sn_b2s = [0.0f32; 3];
    let mut sn_s2b_debug = [0.0f32; 3];
    let mut sn_s2b_detailed = [0.0f32; 3];
    let mut e_s2b = [0.0f64; 3];
    let mut e_b2s = [0.0f64; 3];
    let mut sn_acc = [0.0f64; 3];

    let mut n = 1;
    for i in 0..3 {
        n = n * 100;

        sn_acc[i] = sn_accuracy(n);
        sn_s2b[i] = sn_small_to_big(n);
        sn_b2s[i] = sn_big_to_small(n);
        sn_s2b_debug[i] = sn_small_to_big_debug(n);
        sn_s2b_detailed[i] = sn_small_to_big_detailed(n);

        e_s2b[i] = sn_acc[i] - sn_s2b[i] as f64;
        e_b2s[i] = sn_acc[i] - sn_b2s[i] as f64;

        println!("n={}  Sn_acc={:.15}", n, sn_acc[i]);
        println!("Sn_small2big: {:.15}, e: {:.15}", sn_s2b[i], e_s2b[i]);
        println!("Sn_big2small: {:.15}, e: {:.15}", sn_b2s[i], e_b2s[i]);
        println!("Sn_small2big_debug: {:.15}", sn_s2b_debug[i]);
        println!("Sn_small2big_detailed: {:.15}", sn_s2b_detailed[i]);
        println!();
    }

    // 额外测试：整数溢出演示
    println!("=== 整数溢出测试 ===");
    test_integer_overflow();
}

// 测试整数在不同语言中的溢出行为
fn test_integer_overflow() {
    println!("\n整数溢出行为对比:");

    // 在Rust中，默认情况下debug模式会panic，release模式会wrap around
    let max_i32 = i32::MAX;
    println!("i32最大值: {}", max_i32);

    // 演示有符号整数溢出
    let _x: i32 = max_i32;
    // 在release模式下这会wrap around，在debug模式下会panic
    // x += 1; // 这会在debug模式下panic

    println!("在Rust debug模式下，整数溢出会导致panic");
    println!(
        "在Rust release模式下，整数溢出会wrap around: {} + 1 = {}",
        max_i32,
        max_i32.wrapping_add(1)
    );

    // 使用wrapping操作显式处理溢出
    let wrapped = max_i32.wrapping_add(1);
    println!("使用wrapping_add: {} + 1 = {}", max_i32, wrapped);

    // 使用checked操作安全地处理溢出
    match max_i32.checked_add(1) {
        Some(result) => println!("checked_add: {} + 1 = {}", max_i32, result),
        None => println!("checked_add: {} + 1 会导致溢出", max_i32),
    }

    // 对比C++的行为（通常是wrap around）
    println!("在C++中，有符号整数溢出是未定义行为(UB)");
    println!("在Rust中，通过类型系统和编译选项提供了更安全的处理");

    // 无符号整数溢出
    let max_u32 = u32::MAX;
    println!("u32最大值: {}", max_u32);
    let wrapped_u = max_u32.wrapping_add(1);
    println!("无符号整数溢出(wrapping): {} + 1 = {}", max_u32, wrapped_u);

    println!("\n浮点数精度问题:");
    // 演示浮点数精度损失
    let mut float_sum: f32 = 0.0;
    for i in 1..=1000000 {
        float_sum += 1.0 / (i as f32);
    }
    println!("浮点数累加(从小到大): {}", float_sum);

    let mut float_sum_rev: f32 = 0.0;
    for i in (1..=1000000).rev() {
        float_sum_rev += 1.0 / (i as f32);
    }
    println!("浮点数累加(从大到小): {}", float_sum_rev);
    println!("精度差异: {}", (float_sum_rev - float_sum).abs());

    // 对比双精度浮点数
    let mut double_sum: f64 = 0.0;
    for i in 1..=1000000 {
        double_sum += 1.0 / (i as f64);
    }
    println!("双精度累加: {}", double_sum);
    println!(
        "单精度vs双精度差异: {}",
        (double_sum - float_sum_rev as f64).abs()
    );
}
