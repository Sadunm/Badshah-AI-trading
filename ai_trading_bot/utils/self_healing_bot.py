"""
🔄 Self-Healing Bot System
Automatically detects, fixes, and prevents issues.
"""
import time
import threading
from typing import Dict, List, Optional
from pathlib import Path
from ..utils.logger import get_logger
from .smart_validator import SmartValidator
from .auto_fix_system import AutoFixSystem

logger = get_logger(__name__)


class SelfHealingBot:
    """Self-healing system that monitors and fixes issues automatically."""
    
    def __init__(self, codebase_path: str = "ai_trading_bot", check_interval: int = 300):
        """
        Initialize self-healing bot.
        
        Args:
            codebase_path: Path to codebase
            check_interval: Check interval in seconds (default: 5 minutes)
        """
        self.codebase_path = codebase_path
        self.check_interval = check_interval
        self.validator = SmartValidator()
        self.auto_fix = AutoFixSystem(codebase_path)
        self.is_running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_validation: Optional[Dict] = None
        
    def start(self) -> None:
        """Start self-healing monitoring."""
        if self.is_running:
            logger.warning("Self-healing bot already running")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"🔄 Self-healing bot started (check interval: {self.check_interval}s)")
    
    def stop(self) -> None:
        """Stop self-healing monitoring."""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 Self-healing bot stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.is_running:
            try:
                # Run validation
                logger.info("🔍 Running periodic validation...")
                validation_result = self.validator.validate_codebase(self.codebase_path)
                
                # Check for critical issues
                if validation_result.get("critical", 0) > 0:
                    logger.warning(f"⚠️  {validation_result['critical']} critical issues found!")
                    # Attempt auto-fix
                    self.auto_fix.validate_and_fix_all()
                
                self.last_validation = validation_result
                
                # Wait for next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in self-healing monitor: {e}", exc_info=True)
                time.sleep(self.check_interval)
    
    def run_one_time_validation(self) -> Dict:
        """Run one-time validation and fix."""
        logger.info("🚀 Running one-time comprehensive validation...")
        
        # Validate
        validation = self.validator.validate_codebase(self.codebase_path)
        
        # Auto-fix
        if validation.get("total_issues", 0) > 0:
            logger.info("🔧 Attempting auto-fix...")
            fixes = self.auto_fix.validate_and_fix_all()
            validation["fixes_applied"] = fixes
        
        return validation
    
    def get_status(self) -> Dict:
        """Get current status."""
        return {
            "is_running": self.is_running,
            "last_validation": self.last_validation,
            "check_interval": self.check_interval
        }


def run_validation():
    """Run validation as standalone script."""
    bot = SelfHealingBot()
    result = bot.run_one_time_validation()
    
    print("\n" + "=" * 70)
    print("📊 VALIDATION RESULTS")
    print("=" * 70)
    print(f"Total Issues: {result.get('total_issues', 0)}")
    print(f"Critical: {result.get('critical', 0)}")
    print(f"High: {result.get('high', 0)}")
    print(f"Medium: {result.get('medium', 0)}")
    print("=" * 70)
    
    if result.get("issues_by_type"):
        print("\n📋 Issues by Type:")
        for issue_type, issues in result["issues_by_type"].items():
            print(f"  {issue_type}: {len(issues)}")
            for issue in issues[:5]:  # Show first 5
                print(f"    - {issue.get('file')}:{issue.get('line')} - {issue.get('message')}")
    
    return result

