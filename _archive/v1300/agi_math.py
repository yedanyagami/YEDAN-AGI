import numpy as np
from typing import Tuple

class FractalMath:
    """
    Zero-Dependency Fractal Mathematics for YEDAN AGI.
    Implements DFA (Detrended Fluctuation Analysis) to distinguish
    Mean-Reverting Noise (Alpha < 0.5) from True Trends (Alpha > 0.5).
    """

    @staticmethod
    def _linear_regression(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
        """Fast OLS linear regression using numpy."""
        n_times = x.size
        sx2 = np.sum(x**2)
        sx = np.sum(x)
        sxy = np.sum(x * y)
        sy = np.sum(y)
        
        den = n_times * sx2 - (sx**2)
        if den == 0:
            return 0.0, 0.0
            
        num = n_times * sxy - sx * sy
        slope = num / den
        intercept = np.mean(y) - slope * np.mean(x)
        return slope, intercept

    @staticmethod
    def calculate_dfa_alpha(x: list) -> float:
        """
        Calculates the Hurst/Alpha exponent using DFA.
        Input: List or Array of price/returns.
        Output: Alpha (0.5 = Random, >0.5 = Trending, <0.5 = Mean Reverting)
        """
        x = np.asarray(x)
        N = len(x)
        if N < 20: 
            return 0.5 # Not enough data
            
        # 1. Integrate the series (Profile)
        # Using centered cumsum approximates the 'Profile'
        walk = np.cumsum(x - np.mean(x))
        
        # 2. Define Box Sizes (Log Scale)
        min_n, max_n = 4, N // 4
        if max_n <= min_n:
            return 0.5
            
        # Generate log-scale scales
        scales = np.unique(np.logspace(np.log10(min_n), np.log10(max_n), num=10).astype(int))
        scales = scales[scales > 3] # Filter too small
        
        fluctuations = []
        valid_scales = []

        for n in scales:
            # 3. Cut into boxes
            num_boxes = N // n
            if num_boxes < 2: continue
            
            d = walk[:num_boxes * n].reshape((num_boxes, n))
            
            # 4. Detrend & Calc RMS
            # Create x-axis for regression (0, 1, ..., n-1)
            t = np.arange(n)
            
            rms_sum = 0
            for i in range(num_boxes):
                y_segment = d[i]
                slope, intercept = FractalMath._linear_regression(t, y_segment)
                trend = slope * t + intercept
                rms_sum += np.sum((y_segment - trend)**2)
                
            scale_rms = np.sqrt(rms_sum / (num_boxes * n))
            fluctuations.append(scale_rms)
            valid_scales.append(n)

        # 5. Log-Log Regression for Alpha
        if len(valid_scales) < 2:
            return 0.5
            
        log_n = np.log(valid_scales)
        log_f = np.log(fluctuations)
        
        alpha, _ = FractalMath._linear_regression(log_n, log_f)
        return alpha
