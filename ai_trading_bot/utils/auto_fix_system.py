"""
🤖 Human-like Auto-Fix System
Proactively detects and fixes potential issues before they cause problems.
"""
import ast
import re
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AutoFixSystem:
    """Self-healing system that detects and fixes issues automatically."""
    
    def __init__(self, codebase_path: str = "ai_trading_bot"):
        self.codebase_path = Path(codebase_path)
        self.issues_found: List[Dict] = []
        self.fixes_applied: List[Dict] = []
        
    def scan_all_files(self) -> Dict[str, List[Dict]]:
        """Scan all Python files for potential issues."""
        logger.info("🔍 Starting comprehensive codebase scan...")
        
        all_issues = {
            "syntax_errors": [],
            "try_except_issues": [],
            "index_errors": [],
            "division_by_zero": [],
            "none_checks": [],
            "type_errors": [],
            "logic_errors": []
        }
        
        # Find all Python files
        python_files = list(self.codebase_path.rglob("*.py"))
        
        for file_path in python_files:
            # Skip test files and __pycache__
            if "test" in str(file_path) or "__pycache__" in str(file_path):
                continue
                
            try:
                issues = self._scan_file(file_path)
                for category, issue_list in issues.items():
                    all_issues[category].extend(issue_list)
            except Exception as e:
                logger.error(f"Error scanning {file_path}: {e}")
        
        logger.info(f"✅ Scan complete: {sum(len(v) for v in all_issues.values())} potential issues found")
        return all_issues
    
    def _scan_file(self, file_path: Path) -> Dict[str, List[Dict]]:
        """Scan a single file for issues."""
        issues = {
            "syntax_errors": [],
            "try_except_issues": [],
            "index_errors": [],
            "division_by_zero": [],
            "none_checks": [],
            "type_errors": [],
            "logic_errors": []
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check syntax
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues["syntax_errors"].append({
                    "file": str(file_path),
                    "line": e.lineno,
                    "message": str(e),
                    "fix": "Fix syntax error"
                })
            
            # Check try-except blocks
            issues["try_except_issues"].extend(self._check_try_except_blocks(file_path, lines))
            
            # Check index access
            issues["index_errors"].extend(self._check_index_access(file_path, lines))
            
            # Check division operations
            issues["division_by_zero"].extend(self._check_division(file_path, lines))
            
            # Check None checks
            issues["none_checks"].extend(self._check_none_access(file_path, lines))
            
            # Check type conversions
            issues["type_errors"].extend(self._check_type_conversions(file_path, lines))
            
        except Exception as e:
            logger.warning(f"Could not scan {file_path}: {e}")
        
        return issues
    
    def _check_try_except_blocks(self, file_path: Path, lines: List[str]) -> List[Dict]:
        """Check for malformed try-except blocks."""
        issues = []
        in_try = False
        try_indent = 0
        has_except = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for try
            if stripped.startswith('try:'):
                in_try = True
                try_indent = len(line) - len(line.lstrip())
                has_except = False
            # Check for except
            elif stripped.startswith('except') and in_try:
                except_indent = len(line) - len(line.lstrip())
                if except_indent != try_indent:
                    issues.append({
                        "file": str(file_path),
                        "line": i,
                        "message": f"Misaligned except block (try indent: {try_indent}, except indent: {except_indent})",
                        "fix": f"Align except block to try block indent level"
                    })
                has_except = True
            # Check for finally
            elif stripped.startswith('finally:') and in_try:
                finally_indent = len(line) - len(line.lstrip())
                if finally_indent != try_indent:
                    issues.append({
                        "file": str(file_path),
                        "line": i,
                        "message": f"Misaligned finally block",
                        "fix": "Align finally block to try block indent level"
                    })
                has_except = True
            # Check if try block ended without except/finally
            elif in_try and not has_except:
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= try_indent and stripped and not stripped.startswith('#'):
                    # Try block ended without except
                    issues.append({
                        "file": str(file_path),
                        "line": i - 1,
                        "message": "Try block without except or finally",
                        "fix": "Add except or finally block"
                    })
                    in_try = False
        
        # Check if last try block has except
        if in_try and not has_except:
            issues.append({
                "file": str(file_path),
                "line": len(lines),
                "message": "Try block at end of file without except or finally",
                "fix": "Add except or finally block"
            })
        
        return issues
    
    def _check_index_access(self, file_path: Path, lines: List[str]) -> List[Dict]:
        """Check for unsafe index access."""
        issues = []
        
        patterns = [
            (r'\[-1\]', "Accessing last element without length check"),
            (r'\[0\]', "Accessing first element without length check"),
            (r'\[.*\]', "Array/list access without validation")
        ]
        
        for i, line in enumerate(lines, 1):
            # Skip if already in try-except
            if 'try:' in line or 'except' in line:
                continue
                
            for pattern, message in patterns:
                if re.search(pattern, line) and not any(keyword in line for keyword in ['if', 'len(', 'try:', 'except']):
                    # Check if it's a safe access (with check)
                    if 'len(' not in lines[max(0, i-3):i] and 'if' not in lines[max(0, i-3):i]:
                        issues.append({
                            "file": str(file_path),
                            "line": i,
                            "message": message,
                            "fix": "Add length check before accessing"
                        })
        
        return issues
    
    def _check_division(self, file_path: Path, lines: List[str]) -> List[Dict]:
        """Check for division by zero."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            # Check for division
            if '/' in line or '//' in line or '%' in line:
                # Skip if already checked
                if any(keyword in line for keyword in ['if', 'safe_divide', 'except', 'try']):
                    continue
                    
                # Check previous lines for divisor check
                has_check = False
                for prev_line in lines[max(0, i-5):i]:
                    if 'if' in prev_line and ('!= 0' in prev_line or '> 0' in prev_line):
                        has_check = True
                        break
                
                if not has_check:
                    issues.append({
                        "file": str(file_path),
                        "line": i,
                        "message": "Division without zero check",
                        "fix": "Add zero check before division or use safe_divide()"
                    })
        
        return issues
    
    def _check_none_access(self, file_path: Path, lines: List[str]) -> List[Dict]:
        """Check for None access."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            # Check for .get() usage (safe) vs direct access (unsafe)
            if re.search(r'\[["\']\w+["\']\]', line) and '.get(' not in line:
                # Dictionary access without .get()
                if 'if' not in line and 'except' not in line:
                    issues.append({
                        "file": str(file_path),
                        "line": i,
                        "message": "Dictionary access without .get() safety",
                        "fix": "Use .get() with default value"
                    })
        
        return issues
    
    def _check_type_conversions(self, file_path: Path, lines: List[str]) -> List[Dict]:
        """Check for unsafe type conversions."""
        issues = []
        
        conversion_patterns = [
            (r'int\([^)]+\)', "int() conversion without error handling"),
            (r'float\([^)]+\)', "float() conversion without error handling"),
            (r'str\([^)]+\)', "str() conversion (usually safe)")
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, message in conversion_patterns:
                if re.search(pattern, line) and 'try:' not in lines[max(0, i-3):i+1]:
                    if 'int(' in line or 'float(' in line:
                        issues.append({
                            "file": str(file_path),
                            "line": i,
                            "message": message,
                            "fix": "Wrap in try-except or validate before conversion"
                        })
        
        return issues
    
    def auto_fix_issues(self, issues: Dict[str, List[Dict]]) -> Dict[str, int]:
        """Automatically fix common issues."""
        logger.info("🔧 Starting auto-fix process...")
        
        fixes = {
            "syntax_errors": 0,
            "try_except_blocks": 0,
            "safety_checks": 0,
            "total": 0
        }
        
        # Fix try-except blocks
        for issue in issues.get("try_except_issues", []):
            if self._fix_try_except(issue):
                fixes["try_except_blocks"] += 1
                fixes["total"] += 1
        
        # Fix index access
        for issue in issues.get("index_errors", []):
            if self._fix_index_access(issue):
                fixes["safety_checks"] += 1
                fixes["total"] += 1
        
        # Fix division
        for issue in issues.get("division_by_zero", []):
            if self._fix_division(issue):
                fixes["safety_checks"] += 1
                fixes["total"] += 1
        
        logger.info(f"✅ Auto-fix complete: {fixes['total']} fixes applied")
        return fixes
    
    def _fix_try_except(self, issue: Dict) -> bool:
        """Fix try-except block issues."""
        # This would implement actual fixes
        # For now, just log
        logger.debug(f"Would fix try-except in {issue['file']}:{issue['line']}")
        return False
    
    def _fix_index_access(self, issue: Dict) -> bool:
        """Fix index access issues."""
        logger.debug(f"Would fix index access in {issue['file']}:{issue['line']}")
        return False
    
    def _fix_division(self, issue: Dict) -> bool:
        """Fix division issues."""
        logger.debug(f"Would fix division in {issue['file']}:{issue['line']}")
        return False
    
    def validate_and_fix_all(self) -> Dict:
        """Comprehensive validation and auto-fix."""
        logger.info("🚀 Starting comprehensive validation and auto-fix...")
        
        # Scan all files
        issues = self.scan_all_files()
        
        # Auto-fix
        fixes = self.auto_fix_issues(issues)
        
        # Generate report
        report = {
            "issues_found": {k: len(v) for k, v in issues.items()},
            "fixes_applied": fixes,
            "remaining_issues": {k: len(v) - fixes.get(k, 0) for k, v in issues.items()}
        }
        
        logger.info("=" * 70)
        logger.info("📊 VALIDATION REPORT")
        logger.info("=" * 70)
        for category, count in report["issues_found"].items():
            logger.info(f"  {category}: {count} issues")
        logger.info(f"  Total fixes applied: {fixes['total']}")
        logger.info("=" * 70)
        
        return report

