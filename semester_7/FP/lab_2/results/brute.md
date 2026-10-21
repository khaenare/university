Brute force, 32-bit problem (seed 2026), 3 run(s) per configuration
p = 2638159379, g = 2, h = 2109798053
Order of g: n = 2638159378 (about 2^31.3)
Worker threads: 12; runtime capabilities (+RTS -N): 12; CPU cores: 12

| Version    | Threads | Mean, s | Min, s | Speedup vs 1 thread | Speedup vs sequential | Efficiency |
|------------|---------|---------|--------|---------------------|-----------------------|------------|
| sequential | 1       | 5.062   | 5.051  | -                   | 1.00                  | -          |
| parallel   | 1       | 5.051   | 5.045  | 1.00                | 1.00                  | 1.00       |
| parallel   | 2       | 2.585   | 2.584  | 1.95                | 1.96                  | 0.98       |
| parallel   | 4       | 1.358   | 1.353  | 3.72                | 3.73                  | 0.93       |
| parallel   | 6       | 0.931   | 0.929  | 5.42                | 5.44                  | 0.90       |
| parallel   | 8       | 0.718   | 0.716  | 7.03                | 7.05                  | 0.88       |
| parallel   | 10      | 0.623   | 0.614  | 8.11                | 8.12                  | 0.81       |
| parallel   | 12      | 0.551   | 0.542  | 9.17                | 9.19                  | 0.76       |
