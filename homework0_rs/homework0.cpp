#include <iostream>
#include <iomanip>
#include <cmath>
using namespace std;

float Sn_small2big(int n);
float Sn_small2big_debug(int n);
float Sn_small2big_detailed(int n);
float Sn_big2small(int n);
double Sn_accuracy(int n);

int main()
{
    float Sn_s2b[3], Sn_b2s[3],;
    float Sn_s2b_debug[3], Sn_s2b_detailed[3];
    double e_s2b[3], e_b2s[3]，Sn_acc[3];

    cout << fixed << setprecision(15);

    for (int i = 0; i <= 2; i++)
    {
        static int n = 1;
        n = n * 100;

        Sn_acc[i] = Sn_accuracy(n);
        Sn_s2b[i] = Sn_small2big(n);
        Sn_b2s[i] = Sn_big2small(n);
        Sn_s2b_debug[i] = Sn_small2big_debug(n);
        Sn_s2b_detailed[i] = Sn_small2big_detailed(n);

        e_s2b[i] = Sn_acc[i] - (double)Sn_s2b[i];
        e_b2s[i] = Sn_acc[i] - (double)Sn_b2s[i];

        cout << "n=" << n << "  Sn_acc=" << Sn_acc[i] << endl;
        cout << "Sn_small2big: " << Sn_s2b[i] << ", e: " << e_s2b[i] << endl;
        cout << "Sn_big2small: " << Sn_b2s[i] << ", e: " << e_b2s[i] << endl;
        cout << "Sn_small2big_debug: " << Sn_s2b_debug[i] << endl;
        cout << "Sn_small2big_detailed: " << Sn_s2b_detailed[i] << endl;
        cout << endl;
    }
}

float Sn_small2big(int n)
{
    float Sn = 0;
    for (long long i = 2; i <= n; i++)
    {
        Sn += 1.0 / (i * i - 1);
    }
    return Sn;
}

float Sn_small2big_debug(int n)
{
    float Sn = 0;
    int sign_flip_count = 0;
    int zero_cross_count = 0;
    bool first_negative = true;

    cout << "=== 调试信息: n=" << n << " ===" << endl;

    for (long long i = 2; i <= n; i++) {
        float old_Sn = Sn;
        float term = 1.0 / (i * i - 1);
        Sn += term;

        if ((old_Sn > 0 && Sn < 0) || (old_Sn < 0 && Sn > 0)) {
            sign_flip_count++;
            if (sign_flip_count <= 5) {
                cout << "符号翻转 #" << sign_flip_count << " at i=" << i
                     << ", Sn从 " << old_Sn << " 变为 " << Sn
                     << ", term=" << term << endl;
            }
        }

        if (old_Sn * Sn < 0) {
            zero_cross_count++;
            if (zero_cross_count <= 3) {
                cout << "过零点 #" << zero_cross_count << " at i=" << i
                     << ", Sn从 " << old_Sn << " 变为 " << Sn << endl;
            }
        }

        if (Sn < 0 && first_negative) {
            first_negative = false;
            cout << "第一次变为负数: i=" << i
                 << ", Sn=" << Sn << ", term=" << term
                 << ", 累加器ULP≈" << (Sn * (1.0f / (1 << 23))) << endl;
        }

        if (i % 100000 == 0) {
            cout << "进度: i=" << i << "/" << n << ", Sn=" << Sn << endl;
        }
    }

    cout << "总计: 符号翻转 " << sign_flip_count << " 次, 过零点 " << zero_cross_count << " 次" << endl;
    cout << "最终结果: Sn=" << Sn << endl;
    cout << "=== 调试结束 ===" << endl << endl;

    return Sn;
}

float Sn_small2big_detailed(int n)
{
    float Sn = 0;
    bool found_flip = false;

    cout << "=== 详细分析: n=" << n << " ===" << endl;

    for (long long i = 2; i <= n; i++) {
        float old_Sn = Sn;
        float term = 1.0f / (i * i - 1);

        if (i >= 65530 && i <= 65542) {
            float actual_sum = old_Sn + term;
            float ulp = fabsf(Sn) * (1.0f / (1 << 23));

            cout << "i=" << i << ", old_Sn=" << old_Sn
                 << ", term=" << term << " (2^" << log2f(term) << ")"
                 << ", term/ULP=" << (term / ulp)
                 << ", 数学和=" << actual_sum
                 << ", 浮点和=" << (old_Sn + term) << endl;

            if (actual_sum > 0 && (old_Sn + term) < 0) {
                cout << "!!! 预测符号翻转 !!!" << endl;
            }
        }

        Sn += term;

        if (old_Sn > 0 && Sn < 0 && !found_flip) {
            found_flip = true;
            cout << "!!! 实际符号翻转 at i=" << i
                 << ", 从 " << old_Sn << " 到 " << Sn
                 << ", term=" << term << endl;

            float ulp = fabsf(old_Sn) * (1.0f / (1 << 23));
            cout << "分析: old_Sn=" << old_Sn
                 << ", ULP≈" << ulp
                 << ", term=" << term
                 << ", term/ULP=" << (term / ulp) << endl;

            unsigned int* old_bits = (unsigned int*)&old_Sn;
            unsigned int* new_bits = (unsigned int*)&Sn;
            cout << "二进制: old_Sn=0x" << hex << *old_bits << dec
                 << ", new_Sn=0x" << hex << *new_bits << dec << endl;
        }

        if (found_flip && i > 65542) break;
    }

    cout << "=== 详细分析结束 ===" << endl << endl;
    return Sn;
}

float Sn_big2small(int n)
{
    float Sn = 0;
    for (long long i = n; i >= 2; i--)
    {
        Sn += 1.0 / (i * i - 1);
    }
    return Sn;
}

double Sn_accuracy(int n)
{
    double Sn;
    Sn = 0.5 * (1.5 - 1.0 / n - 1.0 / (n + 1));
    return Sn;
}
