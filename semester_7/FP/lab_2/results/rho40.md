Pollard's rho, 40-bit problem (seed 2026), 60 run(s) per configuration
p = 1046645745143, g = 5, h = 1035666343544
Order of g: n = 1046645745142 (about 2^39.9)
Worker threads: 12; runtime capabilities (+RTS -N): 12; CPU cores: 12

| Version    | Threads | Mean, s | Min, s | Speedup vs 1 thread | Speedup vs sequential | Efficiency |
|------------|---------|---------|--------|---------------------|-----------------------|------------|
| sequential | 1       | 0.059   | 0.003  | -                   | 1.00                  | -          |
| parallel   | 1       | 0.030   | 0.004  | 1.00                | 1.96                  | 1.00       |
| parallel   | 2       | 0.014   | 0.003  | 2.16                | 4.23                  | 1.08       |
| parallel   | 4       | 0.007   | 0.002  | 4.38                | 8.58                  | 1.10       |
| parallel   | 6       | 0.005   | 0.002  | 6.29                | 12.31                 | 1.05       |
| parallel   | 8       | 0.004   | 0.002  | 7.58                | 14.84                 | 0.95       |
| parallel   | 10      | 0.004   | 0.001  | 8.40                | 16.45                 | 0.84       |
| parallel   | 12      | 0.004   | 0.001  | 7.72                | 15.12                 | 0.64       |
