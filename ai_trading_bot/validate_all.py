"""
Validation script to verify all imports and basic functionality.
Run this to check if everything is working correctly.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("AI Trading Bot - Comprehensive Validation")
print("=" * 60)

errors = []
warnings = []

def test_import(module_name, description):
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {description}: OK")
        return True
    except ImportError as e:
        error_msg = f"❌ {description}: FAILED - {e}"
        print(error_msg)
        errors.append(error_msg)
        return False
    except Exception as e:
        warning_msg = f"⚠️  {description}: WARNING - {e}"
        print(warning_msg)
        warnings.append(warning_msg)
        return False

def test_class_instantiation(module_name, class_name, description, *args, **kwargs):
    """Test if a class can be instantiated."""
    try:
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        instance = cls(*args, **kwargs)
        print(f"✅ {description}: OK")
        return True
    except Exception as e:
        error_msg = f"❌ {description}: FAILED - {e}"
        print(error_msg)
        errors.append(error_msg)
        return False

print("\n📦 Testing Core Imports...")
print("-" * 60)

# Test core modules
test_import("ai_trading_bot.config", "Config module")
test_import("ai_trading_bot.utils.logger", "Logger module")
test_import("ai_trading_bot.utils.openrouter_client", "OpenRouter client")
test_import("ai_trading_bot.data.data_manager", "Data manager")
test_import("ai_trading_bot.data.websocket_client", "WebSocket client")
test_import("ai_trading_bot.features.indicators", "Technical indicators")
test_import("ai_trading_bot.risk.risk_manager", "Risk manager")
test_import("ai_trading_bot.allocator.position_allocator", "Position allocator")
test_import("ai_trading_bot.execution.order_executor", "Order executor")
test_import("ai_trading_bot.strategies.base_strategy", "Base strategy")
test_import("ai_trading_bot.strategies.ai_signal_generator", "AI signal generator")
test_import("ai_trading_bot.strategies.momentum_strategy", "Momentum strategy")
test_import("ai_trading_bot.main", "Main bot module")

print("\n🔧 Testing Class Instantiation...")
print("-" * 60)

# Test logger
try:
    from ai_trading_bot.utils.logger import get_logger
    logger = get_logger("test")
    print("✅ Logger instantiation: OK")
except Exception as e:
    errors.append(f"Logger instantiation failed: {e}")
    print(f"❌ Logger instantiation: FAILED - {e}")

# Test RiskManager
test_class_instantiation(
    "ai_trading_bot.risk.risk_manager",
    "RiskManager",
    "RiskManager instantiation",
    100.0, 5.0, 2.0, 10
)

# Test PositionAllocator
test_class_instantiation(
    "ai_trading_bot.allocator.position_allocator",
    "PositionAllocator",
    "PositionAllocator instantiation",
    1000.0, 1.0, 20.0
)

# Test OrderExecutor
test_class_instantiation(
    "ai_trading_bot.execution.order_executor",
    "OrderExecutor",
    "OrderExecutor instantiation",
    True
)

print("\n📊 Testing Configuration...")
print("-" * 60)

try:
    from ai_trading_bot.config import load_config, validate_config
    config = load_config()
    is_valid, config_errors = validate_config(config)
    if is_valid:
        print("✅ Configuration validation: OK")
    else:
        print(f"⚠️  Configuration validation: {len(config_errors)} warnings")
        for err in config_errors:
            warnings.append(f"Config: {err}")
except Exception as e:
    errors.append(f"Configuration test failed: {e}")
    print(f"❌ Configuration test: FAILED - {e}")

print("\n🧪 Testing Technical Indicators...")
print("-" * 60)

try:
    from ai_trading_bot.features.indicators import (
        calculate_rsi, calculate_macd, calculate_bollinger_bands,
        safe_get_last, safe_divide
    )
    import numpy as np
    
    # Test with sample data
    prices = [100 + i * 0.5 for i in range(50)]
    rsi = calculate_rsi(prices, 14)
    if rsi is not None:
        print("✅ RSI calculation: OK")
    else:
        warnings.append("RSI returned None (insufficient data)")
        print("⚠️  RSI calculation: Insufficient data (expected for short array)")
    
    macd = calculate_macd(prices)
    if macd is not None:
        print("✅ MACD calculation: OK")
    else:
        warnings.append("MACD returned None")
        print("⚠️  MACD calculation: Insufficient data")
    
    # Test helper functions
    arr = np.array([1, 2, 3, 4, 5])
    result = safe_get_last(arr)
    if result == 5.0:
        print("✅ safe_get_last function: OK")
    else:
        errors.append(f"safe_get_last returned {result}, expected 5.0")
        print(f"❌ safe_get_last function: FAILED")
    
    result = safe_divide(10, 2)
    if result == 5.0:
        print("✅ safe_divide function: OK")
    else:
        errors.append(f"safe_divide returned {result}, expected 5.0")
        print(f"❌ safe_divide function: FAILED")
    
except Exception as e:
    errors.append(f"Indicators test failed: {e}")
    print(f"❌ Indicators test: FAILED - {e}")

print("\n📋 Testing Test Files...")
print("-" * 60)

# Check if test files can be imported
test_import("tests.test_risk_manager", "Risk manager tests")
test_import("tests.test_indicators", "Indicators tests")
test_import("tests.test_position_allocator", "Position allocator tests")

print("\n" + "=" * 60)
print("📊 Validation Summary")
print("=" * 60)

if errors:
    print(f"\n❌ ERRORS ({len(errors)}):")
    for error in errors:
        print(f"  - {error}")
else:
    print("\n✅ No errors found!")

if warnings:
    print(f"\n⚠️  WARNINGS ({len(warnings)}):")
    for warning in warnings:
        print(f"  - {warning}")

if not errors:
    print("\n🎉 All core functionality validated successfully!")
    print("✅ Codebase is ready to use!")
    sys.exit(0)
else:
    print("\n❌ Validation failed. Please fix the errors above.")
    sys.exit(1)

