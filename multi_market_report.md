# Global Tail Risk Measures Report
Generated on 2026-03-21

Period: 2018-01-01 to 2026-02-27

## US (S&P 500) (^GSPC)
**Optimal Parameters Used:**
- KJ Measure: window=90, quantile=0.1

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -0.0015 |            -0.2429 |              -0.0073 |                -0.2571 |          -0.001  |
|                5 |          -0.0052 |            -0.2036 |              -0.0768 |                -1.194  |           0.0007 |
|               10 |           0.0011 |             0.0222 |              -0.1303 |                -1.1623 |           0.0013 |
|               21 |           0.0427 |             0.3882 |              -0.1516 |                -0.8569 |           0.0012 |

**Predicting Future Market Volatility Ratio:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -0.3437 |            -0.5973 |               0.1523 |                 0.1027 |          -0.0008 |
|                5 |          -0.0323 |            -0.0359 |               0.5489 |                 0.2919 |          -0.001  |
|               10 |          -0.1001 |            -0.0894 |               0.9372 |                 0.5157 |          -0.0007 |
|               21 |          -0.5778 |            -0.3799 |               1.9723 |                 0.9023 |           0.0007 |

**Predicting Future Max Drawdown:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -0.0015 |            -0.2429 |              -0.0073 |                -0.2571 |          -0.001  |
|                5 |          -0.0134 |            -0.7037 |              -0.0495 |                -0.9134 |           0.0008 |
|               10 |          -0.0106 |            -0.2886 |              -0.109  |                -1.2151 |           0.0017 |
|               21 |           0.0074 |             0.0929 |              -0.2275 |                -1.7298 |           0.0038 |

**Hit Rate Analysis (KJ Lambda > 90th Pct):**
|   Horizon (Days) |   N (High Signal) |   N (Normal) |   Signal Threshold (>90th Pct) |   Hit Rate: Ret<0 (%) |   Avg Ret (High Signal) |   Avg Ret (Normal) |   Ret Spread (High-Normal, %) |   Hit Rate: MaxDD<-1% (%) |   Hit Rate: MaxDD<-2% (%) |   Hit Rate: MaxDD<-3% (%) |
|-----------------:|------------------:|-------------:|-------------------------------:|----------------------:|------------------------:|-------------------:|------------------------------:|--------------------------:|--------------------------:|--------------------------:|
|                1 |               192 |         1724 |                          0.513 |                  44.3 |                    0.11 |               0.04 |                          0.07 |                      10.4 |                       2.6 |                       0.5 |
|                5 |               192 |         1720 |                          0.513 |                  37   |                    0.48 |               0.21 |                          0.27 |                      37   |                      20.3 |                       6.8 |
|               10 |               192 |         1715 |                          0.513 |                  27.1 |                    0.96 |               0.4  |                          0.56 |                      46.9 |                      26.6 |                      16.1 |
|               21 |               192 |         1704 |                          0.513 |                  28.1 |                    1.63 |               0.92 |                          0.7  |                      56.2 |                      39.6 |                      30.2 |

![US (S&P 500) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_GSPC.png)


**KJ Lambda — Scatter: Risk Measure vs Forward Outcomes**
![KJ Scatter US (S&P 500)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KJ_GSPC.png)


**KL MEES — Scatter: Risk Measure vs Forward Outcomes**
![KL Scatter US (S&P 500)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KL_GSPC.png)

---

## China (CSI 300) (000300.SS)
**Optimal Parameters Used:**
- KJ Measure: window=30, quantile=0.05

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0025 |             0.4616 |               0.0241 |                 2.704  |           0.0063 |
|                5 |           0.0058 |             0.2703 |               0.073  |                 2.356  |           0.0115 |
|               10 |          -0.0095 |            -0.2297 |               0.0769 |                 1.6406 |           0.0046 |
|               21 |          -0.0584 |            -0.7102 |               0.0505 |                 0.6212 |           0.0028 |

**Predicting Future Market Volatility Ratio:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -1.2386 |            -3.0618 |               0.1207 |                 0.1752 |           0.0069 |
|                5 |          -1.5448 |            -3.1517 |              -0.0496 |                -0.0779 |           0.0267 |
|               10 |          -1.6502 |            -2.9194 |               0.469  |                 0.671  |           0.0239 |
|               21 |          -2.4338 |            -3.2465 |               1.1741 |                 1.135  |           0.0475 |

**Predicting Future Max Drawdown:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0025 |             0.4616 |               0.0241 |                 2.704  |           0.0063 |
|                5 |           0.0182 |             1.0929 |               0.0318 |                 1.5133 |           0.0104 |
|               10 |           0.0203 |             0.592  |               0.0338 |                 0.9986 |           0.0069 |
|               21 |           0.0231 |             0.3329 |               0.0399 |                 0.8494 |           0.0046 |

**Hit Rate Analysis (KJ Lambda > 90th Pct):**
|   Horizon (Days) |   N (High Signal) |   N (Normal) |   Signal Threshold (>90th Pct) |   Hit Rate: Ret<0 (%) |   Avg Ret (High Signal) |   Avg Ret (Normal) |   Ret Spread (High-Normal, %) |   Hit Rate: MaxDD<-1% (%) |   Hit Rate: MaxDD<-2% (%) |   Hit Rate: MaxDD<-3% (%) |
|-----------------:|------------------:|-------------:|-------------------------------:|----------------------:|------------------------:|-------------------:|------------------------------:|--------------------------:|--------------------------:|--------------------------:|
|                1 |               118 |         1046 |                         0.4191 |                  42.4 |                    0.11 |              -0.01 |                          0.13 |                       9.3 |                       2.5 |                       0   |
|                5 |               118 |         1042 |                         0.4191 |                  51.7 |                    0.13 |              -0.02 |                          0.15 |                      39.8 |                      16.9 |                       6.8 |
|               10 |               118 |         1037 |                         0.4191 |                  49.2 |                    0    |              -0.01 |                          0.02 |                      55.1 |                      34.7 |                      22.9 |
|               21 |               118 |         1026 |                         0.4191 |                  59.3 |                   -1.08 |               0.08 |                         -1.16 |                      70.3 |                      59.3 |                      52.5 |

![China (CSI 300) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_000300.SS.png)


**KJ Lambda — Scatter: Risk Measure vs Forward Outcomes**
![KJ Scatter China (CSI 300)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KJ_000300.SS.png)


**KL MEES — Scatter: Risk Measure vs Forward Outcomes**
![KL Scatter China (CSI 300)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KL_000300.SS.png)

---

## Hong Kong (Hang Seng) (^HSI)
**Optimal Parameters Used:**
- KJ Measure: window=90, quantile=0.05

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0183 |             1.6996 |               0.0028 |                 0.1312 |           0.0003 |
|                5 |           0.0917 |             1.9421 |               0.0385 |                 0.5298 |           0.0063 |
|               10 |           0.1535 |             1.6767 |               0.1061 |                 0.9102 |           0.0104 |
|               21 |           0.3088 |             1.6837 |              -0.0421 |                -0.2199 |           0.0178 |

**Predicting Future Market Volatility Ratio:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -0.5336 |            -0.9677 |               0.9037 |                 0.8257 |          -0.0004 |
|                5 |          -0.9511 |            -1.4881 |               0.2005 |                 0.1765 |           0.0021 |
|               10 |          -1.1371 |            -1.4135 |              -0.5088 |                -0.4704 |           0.0056 |
|               21 |          -1.5156 |            -1.4248 |              -0.6587 |                -0.6959 |           0.0115 |

**Predicting Future Max Drawdown:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0183 |             1.6996 |               0.0028 |                 0.1312 |           0.0003 |
|                5 |           0.0972 |             3.1157 |              -0.0156 |                -0.302  |           0.0133 |
|               10 |           0.1672 |             2.8    |               0.0318 |                 0.3976 |           0.0243 |
|               21 |           0.3066 |             2.5313 |              -0.019  |                -0.1595 |           0.0404 |

**Hit Rate Analysis (KJ Lambda > 90th Pct):**
|   Horizon (Days) |   N (High Signal) |   N (Normal) |   Signal Threshold (>90th Pct) |   Hit Rate: Ret<0 (%) |   Avg Ret (High Signal) |   Avg Ret (Normal) |   Ret Spread (High-Normal, %) |   Hit Rate: MaxDD<-1% (%) |   Hit Rate: MaxDD<-2% (%) |   Hit Rate: MaxDD<-3% (%) |
|-----------------:|------------------:|-------------:|-------------------------------:|----------------------:|------------------------:|-------------------:|------------------------------:|--------------------------:|--------------------------:|--------------------------:|
|                1 |               191 |         1717 |                         0.4068 |                  45.5 |                    0.11 |              -0.01 |                          0.12 |                      15.7 |                       2.6 |                       1   |
|                5 |               191 |         1713 |                         0.4068 |                  48.7 |                    0.28 |              -0.02 |                          0.31 |                      48.7 |                      26.7 |                      15.7 |
|               10 |               191 |         1708 |                         0.4068 |                  49.7 |                    0.36 |              -0.01 |                          0.36 |                      64.9 |                      45.5 |                      30.4 |
|               21 |               191 |         1697 |                         0.4068 |                  46.1 |                   -0    |               0.07 |                         -0.07 |                      73.3 |                      59.2 |                      45   |

![Hong Kong (Hang Seng) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_HSI.png)


**KJ Lambda — Scatter: Risk Measure vs Forward Outcomes**
![KJ Scatter Hong Kong (Hang Seng)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KJ_HSI.png)


**KL MEES — Scatter: Risk Measure vs Forward Outcomes**
![KL Scatter Hong Kong (Hang Seng)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KL_HSI.png)

---

## Taiwan (TAIEX) (^TWII)
**Optimal Parameters Used:**
- KJ Measure: window=90, quantile=0.05

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0015 |             0.2529 |               0.0381 |                 1.0901 |           0.0012 |
|                5 |           0.0159 |             0.616  |               0.1075 |                 1.3147 |           0.0033 |
|               10 |           0.0281 |             0.6046 |               0.0045 |                 0.0396 |          -0      |
|               21 |           0.0802 |             0.9315 |              -0.1126 |                -0.529  |           0.0034 |

**Predicting Future Market Volatility Ratio:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -0.3303 |            -0.8201 |               3.8294 |                 2.3824 |           0.004  |
|                5 |          -0.7425 |            -1.3312 |               1.4426 |                 0.8276 |           0.0028 |
|               10 |          -1.1029 |            -1.5154 |               0.6828 |                 0.45   |           0.0061 |
|               21 |          -1.5458 |            -1.5507 |               0.8092 |                 0.5743 |           0.0138 |

**Predicting Future Max Drawdown:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0015 |             0.2529 |               0.0381 |                 1.0901 |           0.0012 |
|                5 |           0.0223 |             1.0782 |               0.0567 |                 0.9713 |           0.0025 |
|               10 |           0.0415 |             1.0907 |               0.0409 |                 0.4534 |           0.0029 |
|               21 |           0.0905 |             1.2022 |              -0.1149 |                -1.0395 |           0.0078 |

**Hit Rate Analysis (KJ Lambda > 90th Pct):**
|   Horizon (Days) |   N (High Signal) |   N (Normal) |   Signal Threshold (>90th Pct) |   Hit Rate: Ret<0 (%) |   Avg Ret (High Signal) |   Avg Ret (Normal) |   Ret Spread (High-Normal, %) |   Hit Rate: MaxDD<-1% (%) |   Hit Rate: MaxDD<-2% (%) |   Hit Rate: MaxDD<-3% (%) |
|-----------------:|------------------:|-------------:|-------------------------------:|----------------------:|------------------------:|-------------------:|------------------------------:|--------------------------:|--------------------------:|--------------------------:|
|                1 |               188 |         1682 |                         0.4246 |                  49.5 |                    0.07 |               0.06 |                          0.01 |                      11.2 |                       2.1 |                       0.5 |
|                5 |               188 |         1678 |                         0.4246 |                  45.7 |                    0.26 |               0.33 |                         -0.06 |                      44.1 |                      25.5 |                       9   |
|               10 |               188 |         1673 |                         0.4246 |                  42   |                    0.54 |               0.64 |                         -0.11 |                      54.3 |                      37.8 |                      22.9 |
|               21 |               188 |         1662 |                         0.4246 |                  37.2 |                    1.46 |               1.32 |                          0.14 |                      61.7 |                      49.5 |                      37.8 |

![Taiwan (TAIEX) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_TWII.png)


**KJ Lambda — Scatter: Risk Measure vs Forward Outcomes**
![KJ Scatter Taiwan (TAIEX)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KJ_TWII.png)


**KL MEES — Scatter: Risk Measure vs Forward Outcomes**
![KL Scatter Taiwan (TAIEX)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KL_TWII.png)

---

## Japan (Nikkei 225) (^N225)
**Optimal Parameters Used:**
- KJ Measure: window=60, quantile=0.1

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0173 |             1.4825 |               0.019  |                 0.5919 |           0.0018 |
|                5 |           0.0769 |             1.8995 |              -0.0187 |                -0.2082 |           0.0061 |
|               10 |           0.1452 |             2.0852 |              -0.006  |                -0.056  |           0.0132 |
|               21 |           0.2798 |             2.0859 |              -0.1113 |                -0.7573 |           0.0254 |

**Predicting Future Market Volatility Ratio:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.4308 |             0.6575 |               2.0036 |                 1.3239 |           0.0014 |
|                5 |          -0.1696 |            -0.198  |               0.3743 |                 0.2021 |          -0.001  |
|               10 |           0.5068 |             0.448  |              -1.9922 |                -1.0157 |           0.003  |
|               21 |           1.9487 |             1.1981 |              -2.1043 |                -1.1171 |           0.0138 |

**Predicting Future Max Drawdown:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0173 |             1.4825 |               0.019  |                 0.5919 |           0.0018 |
|                5 |           0.008  |             0.2574 |               0.0089 |                 0.1471 |          -0.0009 |
|               10 |          -0.0056 |            -0.0994 |               0.0444 |                 0.4938 |          -0.0006 |
|               21 |          -0.0514 |            -0.486  |               0.092  |                 0.7199 |           0.001  |

**Hit Rate Analysis (KJ Lambda > 90th Pct):**
|   Horizon (Days) |   N (High Signal) |   N (Normal) |   Signal Threshold (>90th Pct) |   Hit Rate: Ret<0 (%) |   Avg Ret (High Signal) |   Avg Ret (Normal) |   Ret Spread (High-Normal, %) |   Hit Rate: MaxDD<-1% (%) |   Hit Rate: MaxDD<-2% (%) |   Hit Rate: MaxDD<-3% (%) |
|-----------------:|------------------:|-------------:|-------------------------------:|----------------------:|------------------------:|-------------------:|------------------------------:|--------------------------:|--------------------------:|--------------------------:|
|                1 |               186 |         1719 |                         0.4524 |                  36   |                    0.43 |               0.03 |                          0.4  |                      12.4 |                       3.8 |                       1.6 |
|                5 |               187 |         1715 |                         0.4524 |                  28.9 |                    1.42 |               0.17 |                          1.25 |                      30.6 |                      18.6 |                       9.3 |
|               10 |               189 |         1707 |                         0.4524 |                  23.8 |                    2.29 |               0.38 |                          1.91 |                      41.5 |                      30.1 |                      17.5 |
|               21 |               189 |         1696 |                         0.4524 |                  31.2 |                    3.49 |               0.9  |                          2.59 |                      54.2 |                      41.9 |                      32.4 |

![Japan (Nikkei 225) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_N225.png)


**KJ Lambda — Scatter: Risk Measure vs Forward Outcomes**
![KJ Scatter Japan (Nikkei 225)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KJ_N225.png)


**KL MEES — Scatter: Risk Measure vs Forward Outcomes**
![KL Scatter Japan (Nikkei 225)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KL_N225.png)

---

## Korea (KOSPI) (^KS11)
**Optimal Parameters Used:**
- KJ Measure: window=90, quantile=0.1

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0      |             0.0031 |              -0.0507 |                -1.5443 |           0.0034 |
|                5 |           0.039  |             0.9033 |              -0.1451 |                -0.9574 |           0.0064 |
|               10 |           0.0911 |             1.034  |              -0.0679 |                -0.6472 |           0.0042 |
|               21 |           0.135  |             0.6753 |               0.0981 |                 0.5715 |           0.0049 |

**Predicting Future Market Volatility Ratio:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -0.5348 |            -0.7678 |               2.0593 |                 1.1832 |           0.0009 |
|                5 |          -0.497  |            -0.5015 |               1.5751 |                 0.4946 |           0.0013 |
|               10 |          -1.438  |            -1.2083 |               2.4992 |                 0.783  |           0.0107 |
|               21 |          -2.3535 |            -1.6375 |               0.338  |                 0.1548 |           0.0236 |

**Predicting Future Max Drawdown:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0      |             0.0031 |              -0.0507 |                -1.5443 |           0.0034 |
|                5 |           0.014  |             0.4935 |              -0.1871 |                -1.0807 |           0.0171 |
|               10 |           0.0593 |             1.0753 |              -0.2348 |                -1.2214 |           0.016  |
|               21 |           0.1379 |             1.0919 |              -0.1976 |                -0.9499 |           0.0126 |

**Hit Rate Analysis (KJ Lambda > 90th Pct):**
|   Horizon (Days) |   N (High Signal) |   N (Normal) |   Signal Threshold (>90th Pct) |   Hit Rate: Ret<0 (%) |   Avg Ret (High Signal) |   Avg Ret (Normal) |   Ret Spread (High-Normal, %) |   Hit Rate: MaxDD<-1% (%) |   Hit Rate: MaxDD<-2% (%) |   Hit Rate: MaxDD<-3% (%) |
|-----------------:|------------------:|-------------:|-------------------------------:|----------------------:|------------------------:|-------------------:|------------------------------:|--------------------------:|--------------------------:|--------------------------:|
|                1 |               190 |         1705 |                         0.4488 |                  46.3 |                   -0    |               0.06 |                         -0.06 |                      18.9 |                       6.3 |                       3.2 |
|                5 |               190 |         1701 |                         0.4488 |                  45.8 |                    0.38 |               0.25 |                          0.12 |                      44.7 |                      23.7 |                      17.4 |
|               10 |               190 |         1696 |                         0.4488 |                  46.3 |                    0.93 |               0.47 |                          0.46 |                      63.2 |                      38.4 |                      25.3 |
|               21 |               190 |         1685 |                         0.4488 |                  44.2 |                    1.9  |               0.98 |                          0.92 |                      68.9 |                      56.8 |                      43.7 |

![Korea (KOSPI) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_KS11.png)


**KJ Lambda — Scatter: Risk Measure vs Forward Outcomes**
![KJ Scatter Korea (KOSPI)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KJ_KS11.png)


**KL MEES — Scatter: Risk Measure vs Forward Outcomes**
![KL Scatter Korea (KOSPI)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KL_KS11.png)

---

## Europe (Euro Stoxx 50) (^STOXX50E)
**Optimal Parameters Used:**
- KJ Measure: window=30, quantile=0.05

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0107 |             1.4482 |              -0.0149 |                -1.3415 |           0.0013 |
|                5 |           0.0646 |             1.6853 |              -0.028  |                -0.6626 |           0.0112 |
|               10 |           0.1105 |             1.3472 |              -0.0093 |                -0.1553 |           0.0185 |
|               21 |           0.1089 |             0.6448 |               0.0958 |                 0.9733 |           0.0178 |

**Predicting Future Market Volatility Ratio:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -0.3551 |            -0.7584 |               0.2716 |                 0.4556 |          -0.0009 |
|                5 |          -0.9445 |            -1.3818 |               0.9443 |                 1.1802 |           0.0051 |
|               10 |          -1.7172 |            -1.8061 |               0.8981 |                 0.9476 |           0.0172 |
|               21 |          -2.4425 |            -1.7578 |               0.0536 |                 0.0524 |           0.0458 |

**Predicting Future Max Drawdown:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0107 |             1.4482 |              -0.0149 |                -1.3415 |           0.0013 |
|                5 |           0.0722 |             2.3051 |              -0.0655 |                -1.7839 |           0.0246 |
|               10 |           0.1506 |             2.1276 |              -0.107  |                -1.8588 |           0.0491 |
|               21 |           0.2752 |             1.7948 |              -0.0931 |                -0.9573 |           0.076  |

**Hit Rate Analysis (KJ Lambda > 90th Pct):**
|   Horizon (Days) |   N (High Signal) |   N (Normal) |   Signal Threshold (>90th Pct) |   Hit Rate: Ret<0 (%) |   Avg Ret (High Signal) |   Avg Ret (Normal) |   Ret Spread (High-Normal, %) |   Hit Rate: MaxDD<-1% (%) |   Hit Rate: MaxDD<-2% (%) |   Hit Rate: MaxDD<-3% (%) |
|-----------------:|------------------:|-------------:|-------------------------------:|----------------------:|------------------------:|-------------------:|------------------------------:|--------------------------:|--------------------------:|--------------------------:|
|                1 |               200 |         1766 |                         0.4104 |                  40.5 |                    0.05 |               0.03 |                          0.02 |                      16   |                       3.5 |                       2   |
|                5 |               200 |         1760 |                         0.4104 |                  33   |                    0.44 |               0.12 |                          0.31 |                      36.1 |                      15.7 |                      11   |
|               10 |               200 |         1753 |                         0.4104 |                  40   |                    0.71 |               0.28 |                          0.43 |                      43.6 |                      30.9 |                      22.1 |
|               21 |               198 |         1743 |                         0.4104 |                  35.4 |                    1.71 |               0.58 |                          1.13 |                      57.4 |                      45.1 |                      32.7 |

![Europe (Euro Stoxx 50) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_STOXX50E.png)


**KJ Lambda — Scatter: Risk Measure vs Forward Outcomes**
![KJ Scatter Europe (Euro Stoxx 50)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KJ_STOXX50E.png)


**KL MEES — Scatter: Risk Measure vs Forward Outcomes**
![KL Scatter Europe (Euro Stoxx 50)](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/scatter_KL_STOXX50E.png)

---
