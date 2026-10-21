Baby-step giant-step, 46-bit problem (seed 2026), 3 run(s) per configuration
p = 65550714212903, g = 5, h = 65239057494039
Order of g: n = 65550714212902 (about 2^45.9)
Worker threads: 12; runtime capabilities (+RTS -N): 12; CPU cores: 12

| Version    | Threads | Mean, s | Min, s | Speedup vs 1 thread | Speedup vs sequential | Efficiency |
|------------|---------|---------|--------|---------------------|-----------------------|------------|
| sequential | 1       | 1.986   | 1.965  | -                   | 1.00                  | -          |
| parallel   | 1       | 2.024   | 2.016  | 1.00                | 0.98                  | 1.00       |
| parallel   | 2       | 1.066   | 1.054  | 1.90                | 1.86                  | 0.95       |
| parallel   | 4       | 0.564   | 0.552  | 3.59                | 3.52                  | 0.90       |
| parallel   | 6       | 0.379   | 0.378  | 5.34                | 5.24                  | 0.89       |
| parallel   | 8       | 0.299   | 0.298  | 6.77                | 6.65                  | 0.85       |
| parallel   | 10      | 0.276   | 0.265  | 7.33                | 7.20                  | 0.73       |
| parallel   | 12      | 0.269   | 0.256  | 7.53                | 7.39                  | 0.63       |
