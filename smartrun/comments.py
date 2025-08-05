import re
from typing import List, Dict, Union, Optional
from pathlib import Path


class SmartRunCommentRequirements:
    def __init__(self, source: Union[str, Path], is_content: bool = False):
        """
        Initialize SmartRunCommentRequirements.
        Args:
            source: Either a file path or content string
            is_content: True if source is content, False if it's a file path
        """
        self.source = source
        self.is_content = is_content
        self.requirements = self._parse_requirements()

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "SmartRunCommentRequirements":
        """Create instance from file path."""
        return cls(file_path, is_content=False)

    @classmethod
    def from_content(cls, content: str) -> "SmartRunCommentRequirements":
        """Create instance from content string."""
        return cls(content, is_content=True)

    def _get_content(self) -> str:
        """Get content either from file or directly from string."""
        if self.is_content:
            return self.source
        else:
            with open(self.source, "r", encoding="utf-8") as f:
                return f.read()

    def _parse_requirementsOld(self) -> List[str]:
        """Parse all smartrun requirements from the content."""
        content = self._get_content()
        requirements = []
        # Multiple patterns for flexibility
        patterns = [
            r"#\s*smartrun:\s*(.+)",
            r"#\s*smartrun-requires:\s*(.+)",
            r"#\s*requires:\s*(.+)",
            r"#\s*@smartrun\s+(.+)",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                deps = [dep.strip() for dep in match.split(",") if dep.strip()]
                requirements.extend(deps)
        return list(set(requirements))  # Remove duplicates

    def _parse_requirements(self) -> List[str]:
        """Parse all smartrun requirements from the content."""
        content = self._get_content()
        requirements = []
        # Multiple patterns for flexibility
        patterns = [
            r"#\s*smartrun:\s*(.+)",
            r"#\s*smartrun-requires:\s*(.+)",
            r"#\s*requires:\s*(.+)",
            r"#\s*@smartrun\s+(.+)",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:

                deps = re.split(r"[,\s]+", match)
                requirements.extend(dep.strip() for dep in deps if dep.strip())
        return list(set(requirements))  # Remove duplicates

    def get_requirements_near_imports(self) -> Dict[str, str]:
        """Extract requirements that are near import statements."""
        content = self._get_content()
        lines = content.splitlines()
        requirements = {}
        for i, line in enumerate(lines):
            # Check if line contains import
            if "import" in line and not line.strip().startswith("#"):
                # Look for smartrun comments in surrounding lines (±3 lines)
                for j in range(max(0, i - 3), min(len(lines), i + 4)):
                    comment_line = lines[j].strip()
                    if comment_line.startswith("#"):
                        match = re.search(
                            r"#\s*smartrun:\s*(.+)", comment_line, re.IGNORECASE
                        )
                        if match:
                            module_name = self._extract_module_name(line)
                            if module_name:
                                requirements[module_name] = match.group(1).strip()
        return requirements

    def _extract_module_name(self, import_line: str) -> Optional[str]:
        """Extract module name from import statement."""
        import_line = import_line.strip()
        # Handle different import patterns
        patterns = [
            r"from\s+([a-zA-Z_][a-zA-Z0-9_]*)",  # from module
            r"import\s+([a-zA-Z_][a-zA-Z0-9_]*)",  # import module
        ]
        for pattern in patterns:
            match = re.search(pattern, import_line)
            if match:
                return match.group(1)
        return None

    def get_block_requirements(self) -> List[str]:
        """Extract requirements from block-style comments or docstrings."""
        content = self._get_content()
        requirements = []
        # Look for block-style requirements in docstrings
        docstring_pattern = r'"""[\s\S]*?smartrun-requirements:\s*([\s\S]*?)"""'
        matches = re.findall(docstring_pattern, content, re.IGNORECASE)
        for match in matches:
            lines = match.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line and not line.startswith("smartrun-requirements:"):
                    requirements.append(line)
        # Look for block-style requirements in comments
        comment_block_pattern = r"#\s*smartrun-requirements:\s*\n((?:#.*\n)*)"
        matches = re.findall(comment_block_pattern, content, re.IGNORECASE)
        for match in matches:
            lines = match.split("\n")
            for line in lines:
                line = line.strip().lstrip("#").strip()
                if line:
                    requirements.append(line)
        return requirements

    def get_all_requirements(self) -> Dict[str, List[str]]:
        """Get all requirements categorized by type."""
        return {
            "inline": self.requirements,
            "near_imports": list(self.get_requirements_near_imports().values()),
            "block_style": self.get_block_requirements(),
        }

    def install_requirements(self):
        """Install the parsed requirements."""
        all_reqs = []
        all_reqs.extend(self.requirements)
        all_reqs.extend(self.get_requirements_near_imports().values())
        all_reqs.extend(self.get_block_requirements())
        # Remove duplicates while preserving order
        unique_reqs = list(dict.fromkeys(all_reqs))
        for req in unique_reqs:
            print(f"Installing {req}...")
            # Your installation logic here


# Standalone functions for backward compatibility and convenience
def extract_smartrun_requirements_from_file(file_path: Union[str, Path]) -> List[str]:
    """Extract smartrun requirements from a Python file."""
    parser = SmartRunCommentRequirements.from_file(file_path)
    return parser.requirements


def extract_smartrun_requirements_from_content(content: str) -> List[str]:
    """Extract smartrun requirements from content string."""
    parser = SmartRunCommentRequirements.from_content(content)
    return parser.requirements


def parse_requirements(source: Union[str, Path], is_content: bool = False) -> List[str]:
    """
    Parse requirements from either file or content.
    Args:
        source: File path or content string
        is_content: True if source is content, False if file path
    Returns:
        List of requirement strings
    """
    if is_content:
        return extract_smartrun_requirements_from_content(source)
    else:
        return extract_smartrun_requirements_from_file(source)
