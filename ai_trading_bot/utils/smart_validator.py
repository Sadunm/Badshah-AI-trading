"""
🧠 Smart Validator - Human-like code validation
Predicts and prevents issues before they occur.
"""
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SmartValidator:
    """Validates code for common issues and suggests fixes."""
    
    KNOWN_ISSUES = {
        "indentation": {
            "pattern": "try-except block indentation",
            "severity": "critical",
            "fix": "Align except/finally with try block"
        },
        "division_by_zero": {
            "pattern": "Division without zero check",
            "severity": "high",
            "fix": "Add zero check or use safe_divide()"
        },
        "index_error": {
            "pattern": "Index access without length check",
            "severity": "high",
            "fix": "Check length before accessing"
        },
        "none_access": {
            "pattern": "Dictionary access without .get()",
            "severity": "medium",
            "fix": "Use .get() with default"
        },
        "type_conversion": {
            "pattern": "Type conversion without error handling",
            "severity": "medium",
            "fix": "Wrap in try-except"
        }
    }
    
    def validate_file(self, file_path: Path) -> List[Dict]:
        """Validate a single file."""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check syntax
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append({
                    "type": "syntax_error",
                    "severity": "critical",
                    "line": e.lineno,
                    "message": str(e),
                    "file": str(file_path)
                })
            
            # Check for common patterns
            lines = content.split('\n')
            issues.extend(self._check_indentation(lines, file_path))
            issues.extend(self._check_safety_patterns(lines, file_path))
            
        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")
        
        return issues
    
    def _check_indentation(self, lines: List[str], file_path: Path) -> List[Dict]:
        """Check for indentation issues in try-except blocks."""
        issues = []
        stack = []  # Track try blocks
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())
            
            if stripped.startswith('try:'):
                stack.append({"line": i, "indent": indent})
            elif stripped.startswith('except') or stripped.startswith('finally:'):
                if stack:
                    try_block = stack[-1]
                    if indent != try_block["indent"]:
                        issues.append({
                            "type": "indentation",
                            "severity": "critical",
                            "line": i,
                            "message": f"Except/finally block misaligned with try at line {try_block['line']}",
                            "file": str(file_path),
                            "fix": f"Align to indent level {try_block['indent']}"
                        })
                    stack.pop()
                else:
                    issues.append({
                        "type": "indentation",
                        "severity": "critical",
                        "line": i,
                        "message": "Except/finally without matching try",
                        "file": str(file_path)
                    })
        
        # Check for unmatched try blocks
        for try_block in stack:
            issues.append({
                "type": "indentation",
                "severity": "critical",
                "line": try_block["line"],
                "message": "Try block without except or finally",
                "file": str(file_path),
                "fix": "Add except or finally block"
            })
        
        return issues
    
    def _check_safety_patterns(self, lines: List[str], file_path: Path) -> List[Dict]:
        """Check for unsafe patterns."""
        issues = []
        
        for i, line in enumerate(lines, 1):
            # Skip comments and empty lines
            if line.strip().startswith('#') or not line.strip():
                continue
            
            # Check for division
            if '/' in line and 'safe_divide' not in line:
                # Check if divisor is checked
                has_check = any(
                    'if' in prev_line and ('!= 0' in prev_line or '> 0' in prev_line or 'denominator' in prev_line)
                    for prev_line in lines[max(0, i-5):i]
                )
                if not has_check and 'try:' not in lines[max(0, i-3):i]:
                    issues.append({
                        "type": "division_by_zero",
                        "severity": "high",
                        "line": i,
                        "message": "Division without zero check",
                        "file": str(file_path),
                        "fix": "Add zero check or use safe_divide()"
                    })
            
            # Check for index access
            if '[' in line and ']' in line:
                # Skip safe patterns
                if any(safe in line for safe in ['.get(', 'len(', 'if ', 'try:', 'except']):
                    continue
                
                # Check if length is checked
                has_length_check = any(
                    'len(' in prev_line and ('>' in prev_line or '>=' in prev_line or 'if' in prev_line)
                    for prev_line in lines[max(0, i-5):i]
                )
                if not has_length_check:
                    issues.append({
                        "type": "index_error",
                        "severity": "high",
                        "line": i,
                        "message": "Index access without length check",
                        "file": str(file_path),
                        "fix": "Add length check before accessing"
                    })
        
        return issues
    
    def validate_codebase(self, codebase_path: str = "ai_trading_bot") -> Dict:
        """Validate entire codebase."""
        logger.info("🔍 Starting smart validation...")
        
        codebase = Path(codebase_path)
        all_issues = []
        
        # Find all Python files
        python_files = list(codebase.rglob("*.py"))
        
        for file_path in python_files:
            # Skip tests and cache
            if any(skip in str(file_path) for skip in ['test', '__pycache__', '.pyc']):
                continue
            
            issues = self.validate_file(file_path)
            all_issues.extend(issues)
        
        # Group by type
        issues_by_type = {}
        for issue in all_issues:
            issue_type = issue["type"]
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        logger.info(f"✅ Validation complete: {len(all_issues)} issues found")
        
        return {
            "total_issues": len(all_issues),
            "issues_by_type": issues_by_type,
            "critical": len([i for i in all_issues if i.get("severity") == "critical"]),
            "high": len([i for i in all_issues if i.get("severity") == "high"]),
            "medium": len([i for i in all_issues if i.get("severity") == "medium"])
        }

