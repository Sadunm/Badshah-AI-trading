#!/usr/bin/env python3
"""
🚀 Comprehensive Validation and Auto-Fix Script
Run this before deploying to catch all issues.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_trading_bot.utils.self_healing_bot import SelfHealingBot
from ai_trading_bot.utils.smart_validator import SmartValidator

def main():
    """Run comprehensive validation."""
    print("=" * 70)
    print("🤖 HUMAN-LIKE AUTO-FIX SYSTEM")
    print("=" * 70)
    print()
    
    # Initialize
    validator = SmartValidator()
    bot = SelfHealingBot()
    
    # Run validation
    print("🔍 Step 1: Scanning codebase...")
    validation = validator.validate_codebase("ai_trading_bot")
    
    print(f"\n✅ Found {validation['total_issues']} potential issues")
    print(f"   Critical: {validation.get('critical', 0)}")
    print(f"   High: {validation.get('high', 0)}")
    print(f"   Medium: {validation.get('medium', 0)}")
    
    # Show critical issues
    if validation.get('critical', 0) > 0:
        print("\n⚠️  CRITICAL ISSUES:")
        issues_by_type = validation.get('issues_by_type', {})
        for issue_type, issues in issues_by_type.items():
            if issues and issues[0].get('severity') == 'critical':
                print(f"\n  {issue_type.upper()}:")
                for issue in issues[:10]:  # Show first 10
                    print(f"    - {issue.get('file')}:{issue.get('line')} - {issue.get('message')}")
    
    # Run auto-fix
    print("\n🔧 Step 2: Running auto-fix...")
    fixes = bot.run_one_time_validation()
    
    print("\n" + "=" * 70)
    print("✅ VALIDATION COMPLETE")
    print("=" * 70)
    
    if validation['total_issues'] == 0:
        print("🎉 No issues found! Codebase is clean.")
    else:
        print(f"⚠️  {validation['total_issues']} issues found")
        print("   Review the issues above and fix manually if needed.")
    
    return validation['total_issues'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

