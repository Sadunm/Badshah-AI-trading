"""
Technical indicators for market analysis.
All indicators handle edge cases (NaN, division by zero, insufficient data).
"""
import numpy as np
from typing import List, Optional, Tuple
from ..utils.logger import get_logger

logger = get_logger(__name__)


def safe_get_last(arr: np.ndarray, default: float = 0.0) -> float:
    """
    Safely get last value from array, handling empty arrays and NaN.
    
    Args:
        arr: NumPy array
        default: Default value if array is empty or NaN
        
    Returns:
        Last value or default
    """
    if arr is None or len(arr) == 0:
        return default
    try:
        value = arr[-1]
        if np.isnan(value) or np.isinf(value):
            return default
        return float(value)
    except (IndexError, TypeError):
        return default


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, handling division by zero."""
    if denominator == 0 or np.isnan(denominator) or np.isinf(denominator):
        return default
    if np.isnan(numerator) or np.isinf(numerator):
        return default
    result = numerator / denominator
    if np.isnan(result) or np.isinf(result):
        return default
    return float(result)


def calculate_rsi(prices: List[float], period: int = 14) -> Optional[np.ndarray]:
    """
    Calculate RSI (Relative Strength Index).
    
    Args:
        prices: List of closing prices
        period: RSI period
        
    Returns:
        RSI values array or None if insufficient data
    """
    try:
        if len(prices) < period + 1:
            return None
        
        prices_arr = np.array(prices, dtype=float)
        deltas = np.diff(prices_arr)
        
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gain and loss
        avg_gain = np.zeros_like(prices_arr)
        avg_loss = np.zeros_like(prices_arr)
        
        # Initial average
        avg_gain[period] = np.mean(gains[:period])
        avg_loss[period] = np.mean(losses[:period])
        
        # Smooth averages
        for i in range(period + 1, len(prices_arr)):
            avg_gain[i] = (avg_gain[i-1] * (period - 1) + gains[i-1]) / period
            avg_loss[i] = (avg_loss[i-1] * (period - 1) + losses[i-1]) / period
        
        # Calculate RSI
        rs = np.where(avg_loss != 0, avg_gain / avg_loss, 100)
        rsi = 100 - (100 / (1 + rs))
        
        # Handle NaN and Inf
        rsi = np.nan_to_num(rsi, nan=50.0, posinf=100.0, neginf=0.0)
        
        return rsi
        
    except Exception as e:
        logger.error(f"Error calculating RSI: {e}", exc_info=True)
        return None


def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        prices: List of closing prices
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line period
        
    Returns:
        Tuple of (macd, signal_line, histogram) or None if insufficient data
    """
    try:
        if len(prices) < slow + signal:
            return None
        
        prices_arr = np.array(prices, dtype=float)
        
        # Calculate EMAs
        ema_fast = calculate_ema(prices, fast)
        ema_slow = calculate_ema(prices, slow)
        
        if ema_fast is None or ema_slow is None:
            return None
        
        # MACD line
        macd = ema_fast - ema_slow
        
        # Signal line (EMA of MACD)
        # Extract MACD values starting from where both EMAs are valid (slow-1)
        macd_list = macd[slow-1:].tolist()
        signal_line = calculate_ema(macd_list, signal)
        
        if signal_line is None:
            return None
        
        # Pad signal line to match MACD length
        # signal_line has same length as macd_list, but valid values start from index (signal-1)
        # We need to extract the valid portion and place it correctly
        signal_padded = np.full_like(macd, np.nan)
        
        # Calculate the correct indices
        # macd_list starts at index (slow-1) of macd
        # signal_line valid values start at index (signal-1) of signal_line
        # So in macd array, valid signal starts at: (slow-1) + (signal-1) = slow + signal - 2
        start_idx = slow + signal - 2
        valid_signal = signal_line[signal - 1:]  # Extract valid portion
        
        # Ensure sizes match
        if len(valid_signal) <= len(macd) - start_idx:
            signal_padded[start_idx:start_idx + len(valid_signal)] = valid_signal
        else:
            # If sizes don't match, truncate to fit
            signal_padded[start_idx:] = valid_signal[:len(macd) - start_idx]
        
        # Histogram
        histogram = macd - signal_padded
        
        # Handle NaN and Inf
        macd = np.nan_to_num(macd, nan=0.0, posinf=0.0, neginf=0.0)
        signal_padded = np.nan_to_num(signal_padded, nan=0.0, posinf=0.0, neginf=0.0)
        histogram = np.nan_to_num(histogram, nan=0.0, posinf=0.0, neginf=0.0)
        
        return (macd, signal_padded, histogram)
        
    except Exception as e:
        logger.error(f"Error calculating MACD: {e}", exc_info=True)
        return None


def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Calculate Bollinger Bands.
    
    Args:
        prices: List of closing prices
        period: Moving average period
        std_dev: Standard deviation multiplier
        
    Returns:
        Tuple of (upper_band, middle_band, lower_band) or None if insufficient data
    """
    try:
        if len(prices) < period:
            return None
        
        prices_arr = np.array(prices, dtype=float)
        
        # Calculate SMA (middle band)
        middle_band = calculate_sma(prices, period)
        if middle_band is None:
            return None
        
        # Calculate standard deviation
        upper_band = np.zeros_like(prices_arr)
        lower_band = np.zeros_like(prices_arr)
        
        for i in range(period - 1, len(prices_arr)):
            window = prices_arr[i - period + 1:i + 1]
            std = np.std(window)
            upper_band[i] = middle_band[i] + (std_dev * std)
            lower_band[i] = middle_band[i] - (std_dev * std)
        
        # Handle NaN and Inf
        upper_band = np.nan_to_num(upper_band, nan=prices_arr[-1], posinf=prices_arr[-1], neginf=prices_arr[-1])
        lower_band = np.nan_to_num(lower_band, nan=prices_arr[-1], posinf=prices_arr[-1], neginf=prices_arr[-1])
        middle_band = np.nan_to_num(middle_band, nan=prices_arr[-1], posinf=prices_arr[-1], neginf=prices_arr[-1])
        
        return (upper_band, middle_band, lower_band)
        
    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {e}", exc_info=True)
        return None


def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Optional[np.ndarray]:
    """
    Calculate ATR (Average True Range).
    
    Args:
        highs: List of high prices
        lows: List of low prices
        closes: List of closing prices
        period: ATR period
        
    Returns:
        ATR values array or None if insufficient data
    """
    try:
        if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
            return None
        
        highs_arr = np.array(highs, dtype=float)
        lows_arr = np.array(lows, dtype=float)
        closes_arr = np.array(closes, dtype=float)
        
        # Calculate True Range
        tr_list = []
        for i in range(1, len(highs_arr)):
            tr1 = highs_arr[i] - lows_arr[i]
            tr2 = abs(highs_arr[i] - closes_arr[i-1])
            tr3 = abs(lows_arr[i] - closes_arr[i-1])
            tr = max(tr1, tr2, tr3)
            tr_list.append(tr)
        
        # Calculate ATR (SMA of TR)
        atr = np.zeros(len(highs_arr))
        atr[0] = np.nan
        
        # Initial ATR
        atr[period] = np.mean(tr_list[:period])
        
        # Smooth ATR
        for i in range(period + 1, len(highs_arr)):
            atr[i] = (atr[i-1] * (period - 1) + tr_list[i-1]) / period
        
        # Handle NaN and Inf
        atr = np.nan_to_num(atr, nan=0.0, posinf=0.0, neginf=0.0)
        
        return atr
        
    except Exception as e:
        logger.error(f"Error calculating ATR: {e}", exc_info=True)
        return None


def calculate_sma(prices: List[float], period: int) -> Optional[np.ndarray]:
    """
    Calculate SMA (Simple Moving Average).
    
    Args:
        prices: List of prices
        period: SMA period
        
    Returns:
        SMA values array or None if insufficient data
    """
    try:
        if len(prices) < period:
            return None
        
        prices_arr = np.array(prices, dtype=float)
        sma = np.zeros_like(prices_arr)
        
        for i in range(period - 1, len(prices_arr)):
            sma[i] = np.mean(prices_arr[i - period + 1:i + 1])
        
        # Handle NaN and Inf
        sma = np.nan_to_num(sma, nan=prices_arr[-1], posinf=prices_arr[-1], neginf=prices_arr[-1])
        
        return sma
        
    except Exception as e:
        logger.error(f"Error calculating SMA: {e}", exc_info=True)
        return None


def calculate_ema(prices: List[float], period: int) -> Optional[np.ndarray]:
    """
    Calculate EMA (Exponential Moving Average).
    
    Args:
        prices: List of prices
        period: EMA period
        
    Returns:
        EMA values array or None if insufficient data
    """
    try:
        if len(prices) < period:
            return None
        
        prices_arr = np.array(prices, dtype=float)
        multiplier = 2.0 / (period + 1)
        
        ema = np.zeros_like(prices_arr)
        ema[period - 1] = np.mean(prices_arr[:period])
        
        for i in range(period, len(prices_arr)):
            ema[i] = (prices_arr[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        
        # Handle NaN and Inf
        ema = np.nan_to_num(ema, nan=prices_arr[-1], posinf=prices_arr[-1], neginf=prices_arr[-1])
        
        return ema
        
    except Exception as e:
        logger.error(f"Error calculating EMA: {e}", exc_info=True)
        return None


def calculate_volume_ratio(volumes: List[float], period: int = 20) -> Optional[float]:
    """
    Calculate volume ratio (current volume / average volume).
    
    Args:
        volumes: List of volumes
        period: Period for average volume
        
    Returns:
        Volume ratio or None if insufficient data
    """
    try:
        if len(volumes) < period + 1:
            return None
        
        volumes_arr = np.array(volumes, dtype=float)
        current_volume = volumes_arr[-1]
        avg_volume = np.mean(volumes_arr[-period-1:-1])
        
        if avg_volume == 0:
            return 1.0
        
        ratio = current_volume / avg_volume
        return float(np.nan_to_num(ratio, nan=1.0, posinf=1.0, neginf=1.0))
        
    except Exception as e:
        logger.error(f"Error calculating volume ratio: {e}", exc_info=True)
        return None


def calculate_volatility(prices: List[float], period: int = 20) -> Optional[float]:
    """
    Calculate volatility (standard deviation of returns).
    
    Args:
        prices: List of prices
        period: Period for calculation
        
    Returns:
        Volatility or None if insufficient data
    """
    try:
        if len(prices) < period + 1:
            return None
        
        prices_arr = np.array(prices, dtype=float)
        returns = np.diff(prices_arr[-period-1:]) / prices_arr[-period-1:-1]
        volatility = np.std(returns)
        
        return float(np.nan_to_num(volatility, nan=0.01, posinf=0.01, neginf=0.01))
        
    except Exception as e:
        logger.error(f"Error calculating volatility: {e}", exc_info=True)
        return None


def calculate_z_score(prices: List[float], period: int = 20) -> Optional[float]:
    """
    Calculate z-score (how many standard deviations current price is from mean).
    
    Args:
        prices: List of prices
        period: Period for mean and std calculation
        
    Returns:
        Z-score or None if insufficient data
    """
    try:
        if len(prices) < period + 1:
            return None
        
        prices_arr = np.array(prices, dtype=float)
        window = prices_arr[-period-1:]
        mean_price = np.mean(window)
        std_price = np.std(window)
        
        if std_price == 0:
            return 0.0
        
        current_price = prices_arr[-1]
        z_score = (current_price - mean_price) / std_price
        
        return float(np.nan_to_num(z_score, nan=0.0, posinf=0.0, neginf=0.0))
        
    except Exception as e:
        logger.error(f"Error calculating z-score: {e}", exc_info=True)
        return None


def calculate_momentum(prices: List[float], period: int = 10) -> Optional[float]:
    """
    Calculate momentum (current price / price N periods ago).
    
    Args:
        prices: List of prices
        period: Period for momentum calculation
        
    Returns:
        Momentum or None if insufficient data
    """
    try:
        if len(prices) < period + 1:
            return None
        
        current_price = prices[-1]
        past_price = prices[-period-1]
        
        if past_price == 0:
            return 1.0
        
        momentum = current_price / past_price
        return float(np.nan_to_num(momentum, nan=1.0, posinf=1.0, neginf=1.0))
        
    except Exception as e:
        logger.error(f"Error calculating momentum: {e}", exc_info=True)
        return None


def get_bb_position(price: float, upper_band: float, lower_band: float) -> float:
    """
    Get position within Bollinger Bands (0 = lower band, 1 = upper band).
    
    Args:
        price: Current price
        upper_band: Upper Bollinger Band
        lower_band: Lower Bollinger Band
        
    Returns:
        Position (0-1) or 0.5 if bands are equal
    """
    try:
        if upper_band == lower_band:
            return 0.5
        
        position = (price - lower_band) / (upper_band - lower_band)
        return float(np.clip(np.nan_to_num(position, nan=0.5, posinf=1.0, neginf=0.0), 0.0, 1.0))
        
    except Exception as e:
        logger.error(f"Error calculating BB position: {e}", exc_info=True)
        return 0.5


def calculate_all_indicators(candles: List[dict]) -> dict:
    """
    Calculate all indicators from candle data.
    
    Args:
        candles: List of candle dictionaries with 'open', 'high', 'low', 'close', 'volume'
        
    Returns:
        Dictionary with all calculated indicators
    """
    if not candles or len(candles) < 30:
        return {}
    
    try:
        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        volumes = [c["volume"] for c in candles]
        
        indicators = {}
        
        # RSI
        rsi_14 = calculate_rsi(closes, 14)
        rsi_7 = calculate_rsi(closes, 7)
        indicators["rsi_14"] = safe_get_last(rsi_14, 50.0) if rsi_14 is not None else 50.0
        indicators["rsi_7"] = safe_get_last(rsi_7, 50.0) if rsi_7 is not None else 50.0
        
        # MACD (with error handling)
        try:
            macd_result = calculate_macd(closes, 12, 26, 9)
            if macd_result:
                macd, signal_line, histogram = macd_result
                indicators["macd"] = safe_get_last(macd, 0.0)
                indicators["macd_signal"] = safe_get_last(signal_line, 0.0)
                indicators["macd_histogram"] = safe_get_last(histogram, 0.0)
            else:
                indicators["macd"] = 0.0
                indicators["macd_signal"] = 0.0
                indicators["macd_histogram"] = 0.0
        except Exception as e:
            logger.warning(f"MACD calculation failed, using defaults: {e}")
            indicators["macd"] = 0.0
            indicators["macd_signal"] = 0.0
            indicators["macd_histogram"] = 0.0
        
        # Bollinger Bands
        bb_result = calculate_bollinger_bands(closes, 20, 2.0)
        if bb_result:
            upper, middle, lower = bb_result
            current_price = closes[-1]
            indicators["bb_upper"] = safe_get_last(upper, current_price)
            indicators["bb_middle"] = safe_get_last(middle, current_price)
            indicators["bb_lower"] = safe_get_last(lower, current_price)
            indicators["bb_position"] = get_bb_position(current_price, indicators["bb_upper"], indicators["bb_lower"])
        else:
            current_price = closes[-1]
            indicators["bb_upper"] = current_price
            indicators["bb_middle"] = current_price
            indicators["bb_lower"] = current_price
            indicators["bb_position"] = 0.5
        
        # ATR
        atr = calculate_atr(highs, lows, closes, 14)
        indicators["atr"] = safe_get_last(atr, closes[-1] * 0.01) if atr is not None else closes[-1] * 0.01
        
        # Volume ratio
        indicators["volume_ratio"] = calculate_volume_ratio(volumes, 20) or 1.0
        
        # Volatility
        indicators["volatility"] = calculate_volatility(closes, 20) or 0.01
        
        # Z-score
        indicators["z_score"] = calculate_z_score(closes, 20) or 0.0
        
        # Momentum
        indicators["momentum"] = calculate_momentum(closes, 10) or 1.0
        
        # Current price
        indicators["current_price"] = closes[-1]
        
        return indicators
        
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}", exc_info=True)
        return {}

