Pollard's rho, 50-bit problem (seed 2026), 60 run(s) per configuration
p = 1075465972251899, g = 2, h = 667647538328387
Order of g: n = 1075465972251898 (about 2^49.9)
Worker threads: 12; runtime capabilities (+RTS -N): 12; CPU cores: 12

| Version    | Threads | Mean, s | Min, s | Speedup vs 1 thread | Speedup vs sequential | Efficiency |
|------------|---------|---------|--------|---------------------|-----------------------|------------|
| sequential | 1       | 1.546   | 0.459  | -                   | 1.00                  | -          |
| parallel   | 1       | 0.786   | 0.132  | 1.00                | 1.97                  | 1.00       |
| parallel   | 2       | 0.382   | 0.029  | 2.06                | 4.05                  | 1.03       |
| parallel   | 4       | 0.197   | 0.030  | 4.00                | 7.86                  | 1.00       |
| parallel   | 6       | 0.136   | 0.030  | 5.77                | 11.34                 | 0.96       |
| parallel   | 8       | 0.105   | 0.031  | 7.47                | 14.68                 | 0.93       |
| parallel   | 10      | 0.086   | 0.011  | 9.09                | 17.87                 | 0.91       |
| parallel   | 12      | 0.084   | 0.009  | 9.34                | 18.37                 | 0.78       |
