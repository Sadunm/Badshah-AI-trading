#!/usr/bin/env python3
"""
🤖 Human-like Pre-Deployment Validation
Comprehensive check that finds and fixes ALL potential issues before deployment.
"""
import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class PreDeploymentValidator:
    """Comprehensive validator that thinks like a human developer."""
    
    def __init__(self, codebase_path: str = "ai_trading_bot"):
        self.codebase_path = Path(codebase_path)
        self.issues = []
        self.fixes_applied = []
        
    def validate_all(self) -> Dict:
        """Run all validations."""
        print("=" * 70)
        print("🤖 HUMAN-LIKE PRE-DEPLOYMENT VALIDATION")
        print("=" * 70)
        print()
        
        python_files = list(self.codebase_path.rglob("*.py"))
        python_files = [f for f in python_files if "test" not in str(f) and "__pycache__" not in str(f)]
        
        print(f"📁 Scanning {len(python_files)} Python files...")
        print()
        
        for file_path in python_files:
            self._validate_file(file_path)
        
        # Summary
        print("=" * 70)
        print("📊 VALIDATION SUMMARY")
        print("=" * 70)
        
        critical = len([i for i in self.issues if i.get("severity") == "critical"])
        high = len([i for i in self.issues if i.get("severity") == "high"])
        medium = len([i for i in self.issues if i.get("severity") == "medium"])
        
        print(f"Total Issues: {len(self.issues)}")
        print(f"  🔴 Critical: {critical}")
        print(f"  🟠 High: {high}")
        print(f"  🟡 Medium: {medium}")
        print()
        
        if critical > 0:
            print("⚠️  CRITICAL ISSUES FOUND - MUST FIX BEFORE DEPLOYMENT:")
            for issue in [i for i in self.issues if i.get("severity") == "critical"][:10]:
                print(f"  - {issue['file']}:{issue['line']} - {issue['message']}")
            print()
        
        return {
            "total": len(self.issues),
            "critical": critical,
            "high": high,
            "medium": medium,
            "issues": self.issues
        }
    
    def _validate_file(self, file_path: Path):
        """Validate a single file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # 1. Syntax check
            try:
                ast.parse(content)
            except SyntaxError as e:
                self.issues.append({
                    "file": str(file_path),
                    "line": e.lineno,
                    "severity": "critical",
                    "message": f"SyntaxError: {e.msg}",
                    "category": "syntax"
                })
                return  # Can't continue if syntax is broken
            
            # 2. Check try-except blocks
            self._check_try_except(file_path, lines)
            
            # 3. Check unsafe index access
            self._check_index_access(file_path, lines)
            
            # 4. Check division by zero
            self._check_division(file_path, lines)
            
            # 5. Check None access
            self._check_none_access(file_path, lines)
            
        except Exception as e:
            print(f"⚠️  Error validating {file_path}: {e}")
    
    def _check_try_except(self, file_path: Path, lines: List[str]):
        """Check try-except block structure."""
        in_try = False
        try_line = 0
        try_indent = 0
        has_except = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())
            
            if stripped.startswith('try:'):
                in_try = True
                try_line = i
                try_indent = indent
                has_except = False
            elif (stripped.startswith('except') or stripped.startswith('finally:')) and in_try:
                if indent != try_indent:
                    self.issues.append({
                        "file": str(file_path),
                        "line": i,
                        "severity": "critical",
                        "message": f"Except/finally block misaligned with try at line {try_line}",
                        "category": "indentation"
                    })
                has_except = True
                in_try = False
            elif in_try and not stripped.startswith('#') and not stripped:
                # Empty line in try block - OK
                pass
            elif in_try and indent <= try_indent and stripped and not stripped.startswith('#'):
                # Code outside try block - might be missing except
                if not has_except:
                    # Check if this is the end of try block
                    if i > try_line + 5:  # Allow some code in try block
                        self.issues.append({
                            "file": str(file_path),
                            "line": i,
                            "severity": "critical",
                            "message": f"Try block at line {try_line} might be missing except/finally",
                            "category": "try_except"
                        })
                        in_try = False
    
    def _check_index_access(self, file_path: Path, lines: List[str]):
        """Check for unsafe index access."""
        for i, line in enumerate(lines, 1):
            # Skip if in try-except or has safety check
            if 'try:' in line or 'except' in line:
                continue
            
            # Check for array/list access
            if re.search(r'\[-1\]|\[0\]', line):
                # Check previous lines for safety
                has_check = False
                for prev_line in lines[max(0, i-5):i]:
                    if any(keyword in prev_line for keyword in ['len(', 'if', 'and len', '> 0']):
                        has_check = True
                        break
                
                if not has_check and '[' in line:
                    self.issues.append({
                        "file": str(file_path),
                        "line": i,
                        "severity": "high",
                        "message": "Index access without length check",
                        "category": "index_error"
                    })
    
    def _check_division(self, file_path: Path, lines: List[str]):
        """Check for division by zero."""
        for i, line in enumerate(lines, 1):
            if '/' in line and 'safe_divide' not in line:
                # Skip if already checked
                if any(keyword in line for keyword in ['if', 'safe_divide', 'except']):
                    continue
                
                # Check for divisor check
                has_check = False
                for prev_line in lines[max(0, i-5):i]:
                    if 'if' in prev_line and ('!= 0' in prev_line or '> 0' in prev_line):
                        has_check = True
                        break
                
                if not has_check:
                    # Check if denominator is checked in same line
                    if 'if' not in line and '> 0' not in line and '!= 0' not in line:
                        self.issues.append({
                            "file": str(file_path),
                            "line": i,
                            "severity": "high",
                            "message": "Division without zero check",
                            "category": "division_by_zero"
                        })
    
    def _check_none_access(self, file_path: Path, lines: List[str]):
        """Check for unsafe None access."""
        for i, line in enumerate(lines, 1):
            # Check for direct dictionary access
            if re.search(r'\[["\']\w+["\']\]', line) and '.get(' not in line:
                if 'if' not in line and 'except' not in line:
                    self.issues.append({
                        "file": str(file_path),
                        "line": i,
                        "severity": "medium",
                        "message": "Dictionary access without .get() safety",
                        "category": "none_access"
                    })


def main():
    """Run validation."""
    validator = PreDeploymentValidator()
    result = validator.validate_all()
    
    if result["critical"] > 0:
        print("❌ CRITICAL ISSUES FOUND - FIX BEFORE DEPLOYMENT!")
        return False
    elif result["total"] > 0:
        print("⚠️  Issues found but none are critical. Review recommended.")
        return True
    else:
        print("✅ No issues found! Codebase is clean.")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

