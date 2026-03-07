# Global Tail Risk Measures Report
Generated on 2026-03-07

Period: 2018-01-01 to 2026-02-27

## US (S&P 500) (^GSPC)
**Optimal Parameters Used:**
- KJ Measure: window=90, quantile=0.1
- KL Measure: window=30, n_pca=4, alpha=0.1

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -0.0014 |            -0.2124 |              -0.01   |                -0.352  |          -0.0009 |
|                5 |          -0.005  |            -0.1965 |              -0.0702 |                -1.0867 |           0.0004 |
|               10 |          -0.0003 |            -0.0058 |              -0.1257 |                -1.13   |           0.0011 |
|               21 |           0.0446 |             0.4053 |              -0.1488 |                -0.8501 |           0.0012 |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -0.3311 |            -0.5754 |               0.0988 |                 0.067  |          -0.0008 |
|                5 |           0.0218 |             0.0242 |               0.6274 |                 0.3314 |          -0.0009 |
|               10 |          -0.0455 |            -0.0406 |               0.9953 |                 0.5459 |          -0.0007 |
|               21 |          -0.5411 |            -0.3556 |               1.9998 |                 0.9189 |           0.0007 |

### KL MEES Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |        -0.0219 |          -0.3343 |            -0.0043 |              -0.1025 |          -0.0008 |
|                5 |         0.0727 |           0.4747 |            -0.1618 |              -1.2126 |           0.0012 |
|               10 |         0.1989 |           0.7835 |            -0.135  |              -0.7993 |           0.0001 |
|               21 |         0.5437 |           0.9959 |            -0.314  |              -1.1547 |           0.0029 |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |        -5.5197 |          -1.7911 |             4.111  |               1.8573 |           0.0006 |
|                5 |        -9.0762 |          -2.7346 |             9.4662 |               3.9128 |           0.0088 |
|               10 |       -12.0994 |          -3.2037 |             8.4927 |               3.2708 |           0.0113 |
|               21 |       -17.0265 |          -3.2336 |            10.9098 |               3.5061 |           0.0178 |

![US (S&P 500) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_GSPC.png)

---

## China (CSI 300) (000300.SS)
**Optimal Parameters Used:**
- KJ Measure: window=30, quantile=0.05
- KL Measure: window=30, n_pca=4, alpha=0.1

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0025 |             0.4695 |               0.0244 |                 2.7283 |           0.0065 |
|                5 |           0.0045 |             0.2102 |               0.0748 |                 2.4039 |           0.0117 |
|               10 |          -0.0102 |            -0.2487 |               0.0798 |                 1.7027 |           0.005  |
|               21 |          -0.056  |            -0.6776 |               0.0505 |                 0.6214 |           0.0025 |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -1.2639 |            -3.1368 |               0.1571 |                 0.2276 |           0.0072 |
|                5 |          -1.5405 |            -3.1563 |              -0.0436 |                -0.0683 |           0.0267 |
|               10 |          -1.6478 |            -2.9301 |               0.4748 |                 0.6778 |           0.024  |
|               21 |          -2.4361 |            -3.2711 |               1.2041 |                 1.1596 |           0.0479 |

### KL MEES Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |        -0.028  |          -0.3505 |             0.0714 |               1.2808 |          -0.0005 |
|                5 |         0.2089 |           0.8028 |            -0.1733 |              -0.9469 |          -0.0003 |
|               10 |         0.6123 |           1.5398 |            -0.495  |              -1.6737 |           0.0046 |
|               21 |         1.0036 |           1.7453 |            -0.2462 |              -0.7135 |           0.0066 |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |       -12.8947 |          -2.674  |            10.6554 |               2.7071 |           0.0044 |
|                5 |       -19.9245 |          -3.9695 |            10.4945 |               2.9419 |           0.022  |
|               10 |       -22.7738 |          -4.7201 |            10.0471 |               2.6143 |           0.0256 |
|               21 |       -27.6786 |          -5.3627 |            14.6895 |               3.628  |           0.0344 |

![China (CSI 300) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_000300.SS.png)

---

## Hong Kong (Hang Seng) (^HSI)
**Optimal Parameters Used:**
- KJ Measure: window=90, quantile=0.05
- KL Measure: window=30, n_pca=4, alpha=0.1

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0184 |             1.7135 |               0.0176 |                 0.785  |           0.0007 |
|                5 |           0.0891 |             1.9271 |               0.0602 |                 0.7795 |           0.0066 |
|               10 |           0.1525 |             1.679  |               0.1022 |                 0.8719 |           0.0103 |
|               21 |           0.3147 |             1.7273 |              -0.0308 |                -0.1575 |           0.019  |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -0.4548 |            -0.8363 |               0.6863 |                 0.6343 |          -0.0006 |
|                5 |          -0.8796 |            -1.4029 |               0.2559 |                 0.2297 |           0.0017 |
|               10 |          -1.066  |            -1.3705 |              -0.458  |                -0.4233 |           0.0048 |
|               21 |          -1.4214 |            -1.3829 |              -0.6728 |                -0.7316 |           0.0103 |

### KL MEES Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |         0.0383 |           0.7066 |            -0.0192 |              -0.3609 |          -0.0008 |
|                5 |         0.1592 |           0.8883 |            -0.115  |              -0.8184 |          -0      |
|               10 |         0.223  |           0.6962 |             0.0345 |               0.1751 |           0.0006 |
|               21 |         0.3241 |           0.5563 |            -0.1372 |              -0.4507 |          -0      |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |        -8.028  |          -3.5105 |             7.5775 |               3.5744 |           0.0055 |
|                5 |       -10.9009 |          -5.0517 |             7.893  |               4.8967 |           0.0216 |
|               10 |       -13.6025 |          -6.3619 |             7.0896 |               4.2395 |           0.0407 |
|               21 |       -15.8582 |          -6.6639 |             7.5177 |               4.5567 |           0.0597 |

![Hong Kong (Hang Seng) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_HSI.png)

---

## Taiwan (TAIEX) (^TWII)
**Optimal Parameters Used:**
- KJ Measure: window=90, quantile=0.05
- KL Measure: window=30, n_pca=4, alpha=0.1

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0017 |             0.2984 |               0.0392 |                 1.1168 |           0.0013 |
|                5 |           0.0169 |             0.6538 |               0.1137 |                 1.3866 |           0.0038 |
|               10 |           0.0268 |             0.5755 |               0.011  |                 0.0955 |          -0.0001 |
|               21 |           0.0774 |             0.9019 |              -0.1117 |                -0.5244 |           0.0032 |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -0.3798 |            -0.9415 |               3.8754 |                 2.4059 |           0.0041 |
|                5 |          -0.7692 |            -1.3778 |               1.4443 |                 0.8258 |           0.003  |
|               10 |          -1.1159 |            -1.5306 |               0.6521 |                 0.4302 |           0.0062 |
|               21 |          -1.534  |            -1.5439 |               0.7875 |                 0.5618 |           0.0136 |

### KL MEES Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |         0.0088 |           0.1361 |            -0.0871 |              -1.4187 |           0.0019 |
|                5 |         0.1617 |           0.7731 |            -0.2186 |              -1.4406 |           0.0019 |
|               10 |         0.3933 |           1.2981 |            -0.2837 |              -1.567  |           0.003  |
|               21 |         0.7127 |           1.3074 |            -0.3586 |              -1.1785 |           0.0046 |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |        -9.0608 |          -2.9381 |            10.4536 |               3.777  |           0.0067 |
|                5 |       -10.1959 |          -3.108  |             7.9837 |               2.7347 |           0.0105 |
|               10 |       -11.406  |          -2.898  |             7.1426 |               3.0658 |           0.0133 |
|               21 |       -11.7136 |          -2.8626 |             5.8802 |               2.5821 |           0.0148 |

![Taiwan (TAIEX) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_TWII.png)

---

## Japan (Nikkei 225) (^N225)
**Optimal Parameters Used:**
- KJ Measure: window=60, quantile=0.1
- KL Measure: window=30, n_pca=4, alpha=0.1

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0164 |             1.4352 |               0.0229 |                 0.7729 |           0.0021 |
|                5 |           0.0677 |             1.6619 |               0.0212 |                 0.2477 |           0.0054 |
|               10 |           0.1276 |             1.8439 |               0.0323 |                 0.3083 |           0.0111 |
|               21 |           0.2487 |             1.8382 |              -0.1089 |                -0.7834 |           0.0192 |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.4894 |             0.7644 |               1.6916 |                 1.2088 |           0.0011 |
|                5 |          -0.1098 |            -0.1283 |               0.2124 |                 0.1205 |          -0.001  |
|               10 |           0.5735 |             0.5132 |              -2.1509 |                -1.1553 |           0.004  |
|               21 |           2.0242 |             1.2813 |              -2.046  |                -1.1457 |           0.0145 |

### KL MEES Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |         0.1366 |           2.0625 |            -0.0382 |              -0.8299 |           0.0038 |
|                5 |         0.2483 |           1.4441 |            -0.169  |              -1.2648 |           0.0022 |
|               10 |         0.526  |           1.7194 |            -0.1811 |              -0.7801 |           0.0068 |
|               21 |         1.0833 |           2.1959 |            -0.5697 |              -1.6398 |           0.0153 |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |        -8.881  |          -3.2547 |             6.8796 |               3.1665 |           0.0051 |
|                5 |       -11.9151 |          -4.1312 |             6.0667 |               2.07   |           0.0168 |
|               10 |       -14.5862 |          -5.0281 |             5.9464 |               2.3878 |           0.0328 |
|               21 |       -17.7756 |          -5.502  |             8.0865 |               3.9259 |           0.0464 |

![Japan (Nikkei 225) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_N225.png)

---

## Korea (KOSPI) (^KS11)
**Optimal Parameters Used:**
- KJ Measure: window=90, quantile=0.1
- KL Measure: window=30, n_pca=4, alpha=0.1

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0078 |             0.6753 |              -0.0432 |                -1.3001 |           0.0021 |
|                5 |           0.0507 |             1.091  |              -0.1378 |                -0.8967 |           0.0067 |
|               10 |           0.1069 |             1.1688 |              -0.0579 |                -0.5337 |           0.006  |
|               21 |           0.1525 |             0.7484 |               0.1099 |                 0.6259 |           0.0065 |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -0.5359 |            -0.7987 |               2.3199 |                 1.3005 |           0.0014 |
|                5 |          -0.5525 |            -0.5766 |               1.6933 |                 0.5256 |           0.0018 |
|               10 |          -1.4816 |            -1.2692 |               2.5952 |                 0.8045 |           0.0116 |
|               21 |          -2.4066 |            -1.6987 |               0.4103 |                 0.1861 |           0.0248 |

### KL MEES Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |         0.0373 |           0.5972 |             0.0165 |               0.4497 |          -0      |
|                5 |         0.2695 |           1.2978 |            -0.1421 |              -1.3379 |           0.0024 |
|               10 |         0.5356 |           1.4462 |            -0.2926 |              -1.5431 |           0.0054 |
|               21 |         1.5138 |           1.9373 |            -0.8429 |              -2.0896 |           0.02   |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |        -8.6077 |          -2.8534 |             5.7468 |               2.4898 |           0.004  |
|                5 |       -12.3295 |          -4.2958 |             6.148  |               3.2734 |           0.0175 |
|               10 |       -13.3903 |          -4.1221 |             6.3179 |               2.9895 |           0.0246 |
|               21 |       -17.5683 |          -5.4082 |             8.519  |               3.5441 |           0.0485 |

![Korea (KOSPI) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_KS11.png)

---

## Europe (Euro Stoxx 50) (^STOXX50E)
**Optimal Parameters Used:**
- KJ Measure: window=30, quantile=0.05
- KL Measure: window=30, n_pca=4, alpha=0.1

### KJ Lambda Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |           0.0087 |             1.3142 |              -0.0181 |                -1.6546 |           0.0017 |
|                5 |           0.0511 |             1.5257 |              -0.0718 |                -1.7459 |           0.0108 |
|               10 |           0.0903 |             1.2794 |              -0.0962 |                -1.5199 |           0.0136 |
|               21 |           0.1019 |             0.7066 |               0.0502 |                 0.5427 |           0.0112 |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KJ_Lambda Beta |   KJ_Lambda t-stat |   KJ_Lambda_Vel Beta |   KJ_Lambda_Vel t-stat |   Adj. R-squared |
|-----------------:|-----------------:|-------------------:|---------------------:|-----------------------:|-----------------:|
|                1 |          -0.4105 |            -0.9797 |               0.2784 |                 0.4741 |          -0.0005 |
|                5 |          -0.8516 |            -1.3404 |               1.215  |                 1.4973 |           0.005  |
|               10 |          -1.4845 |            -1.7078 |               1.3379 |                 1.4049 |           0.0136 |
|               21 |          -2.0161 |            -1.6249 |               0.3368 |                 0.346  |           0.0287 |

### KL MEES Predictive Significance (Level + Velocity Multivariate Model)
**Predicting Future Market Returns:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |         0.0227 |           0.2902 |            -0.0323 |              -0.4933 |          -0.0008 |
|                5 |         0.5719 |           2.7512 |             0.0507 |               0.3637 |           0.0217 |
|               10 |         0.7128 |           2.4301 |             0.0141 |               0.077  |           0.0149 |
|               21 |         1.2479 |           2.1868 |            -0.0894 |              -0.2528 |           0.0212 |

**Predicting Future Market Volatility:**
|   Horizon (Days) |   KL_MEES Beta |   KL_MEES t-stat |   KL_MEES_Vel Beta |   KL_MEES_Vel t-stat |   Adj. R-squared |
|-----------------:|---------------:|-----------------:|-------------------:|---------------------:|-----------------:|
|                1 |       -12.362  |          -4.3981 |            10.0003 |               3.5671 |           0.0081 |
|                5 |       -15.9181 |          -4.2383 |            10.0964 |               3.432  |           0.0203 |
|               10 |       -20.115  |          -4.833  |            10.4723 |               3.9043 |           0.0348 |
|               21 |       -23.4451 |          -5.3836 |            10.1055 |               3.628  |           0.0543 |

![Europe (Euro Stoxx 50) Tail Risk Prediction Plot](/Users/ryanhokh/Documents/GitHub/kjkl_tail_risk/export_img/daily_tail_risk_STOXX50E.png)

---
