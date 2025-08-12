#!/usr/bin/env python3
"""
Documentation Validation Script

This script validates the documentation for completeness, accuracy,
and consistency across all components.
"""

import os
import re
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse

class DocumentationValidator:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.docs_dir = self.root_dir / "docs"
        self.examples_dir = self.root_dir / "examples"
        self.sdks_dir = self.root_dir / "sdks"
        
        self.issues = []
        self.warnings = []
        
    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating documentation...")
        
        # Validate structure
        self.validate_structure()
        
        # Validate content
        self.validate_content()
        
        # Validate links
        self.validate_links()
        
        # Validate code examples
        self.validate_code_examples()
        
        # Validate API consistency
        self.validate_api_consistency()
        
        # Validate notebooks
        self.validate_notebooks()
        
        # Report results
        return self.report_results()
    
    def validate_structure(self) -> None:
        """Validate documentation structure."""
        print("📁 Validating documentation structure...")
        
        required_files = [
            "mkdocs.yml",
            "docs/index.md",
            "docs/guides/quickstart.md",
            "docs/guides/installation.md",
            "docs/api/overview.md",
            "docs/api/endpoints.md",
            "docs/api/schemas.md",
            "docs/reference/architecture.md",
            "docs/examples/notebooks.md"
        ]
        
        for file_path in required_files:
            full_path = self.root_dir / file_path
            if not full_path.exists():
                self.issues.append(f"Missing required file: {file_path}")
        
        # Check for empty files
        for md_file in self.docs_dir.rglob("*.md"):
            if md_file.stat().st_size == 0:
                self.issues.append(f"Empty documentation file: {md_file.relative_to(self.root_dir)}")
    
    def validate_content(self) -> None:
        """Validate documentation content."""
        print("📝 Validating content quality...")
        
        for md_file in self.docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            rel_path = md_file.relative_to(self.root_dir)
            
            # Check for common issues
            if len(content.strip()) < 100:
                self.warnings.append(f"Very short content in {rel_path}")
            
            # Check for TODO/FIXME markers
            if re.search(r'TODO|FIXME|XXX', content, re.IGNORECASE):
                self.warnings.append(f"TODO/FIXME markers found in {rel_path}")
            
            # Check for broken markdown
            if content.count('```') % 2 != 0:
                self.issues.append(f"Unmatched code blocks in {rel_path}")
            
            # Check for proper headings hierarchy
            headings = re.findall(r'^(#+)\s+(.+)$', content, re.MULTILINE)
            if headings:
                prev_level = 0
                for heading in headings:
                    level = len(heading[0])
                    if level > prev_level + 1:
                        self.warnings.append(f"Heading hierarchy issue in {rel_path}: {heading[1]}")
                    prev_level = level
    
    def validate_links(self) -> None:
        """Validate internal and external links."""
        print("🔗 Validating links...")
        
        internal_links = set()
        external_links = set()
        
        for md_file in self.docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            rel_path = md_file.relative_to(self.root_dir)
            
            # Find markdown links
            links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)
            
            for link_text, link_url in links:
                if link_url.startswith(('http://', 'https://')):
                    external_links.add(link_url)
                elif link_url.startswith('#'):
                    # Anchor link - check if target exists in same file
                    anchor = link_url[1:].lower().replace(' ', '-')
                    if not self._check_anchor_exists(content, anchor):
                        self.warnings.append(f"Anchor not found in {rel_path}: {link_url}")
                else:
                    # Internal link
                    internal_links.add((str(rel_path), link_url))
        
        # Validate internal links
        for source_file, link_path in internal_links:
            if not self._validate_internal_link(source_file, link_path):
                self.issues.append(f"Broken internal link in {source_file}: {link_path}")
    
    def _check_anchor_exists(self, content: str, anchor: str) -> bool:
        """Check if an anchor exists in the content."""
        # Extract headings and convert to anchor format
        headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        anchors = set()
        
        for heading in headings:
            # Convert heading to anchor format
            anchor_text = re.sub(r'[^\w\s-]', '', heading).strip()
            anchor_text = re.sub(r'\s+', '-', anchor_text).lower()
            anchors.add(anchor_text)
        
        return anchor in anchors
    
    def _validate_internal_link(self, source_file: str, link_path: str) -> bool:
        """Validate an internal link."""
        # Convert relative path to absolute
        source_dir = Path(source_file).parent
        if link_path.startswith('/'):
            target_path = self.docs_dir / link_path.lstrip('/')
        else:
            target_path = self.docs_dir / source_dir / link_path
        
        # Remove anchor part
        if '#' in link_path:
            target_path = Path(str(target_path).split('#')[0])
        
        return target_path.exists()
    
    def validate_code_examples(self) -> None:
        """Validate code examples in documentation."""
        print("💻 Validating code examples...")
        
        for md_file in self.docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            rel_path = md_file.relative_to(self.root_dir)
            
            # Find code blocks
            code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
            
            for language, code in code_blocks:
                if language in ['python', 'py']:
                    self._validate_python_code(code, rel_path)
                elif language in ['javascript', 'typescript', 'js', 'ts']:
                    self._validate_js_code(code, rel_path)
                elif language == 'bash':
                    self._validate_bash_code(code, rel_path)
    
    def _validate_python_code(self, code: str, file_path: str) -> None:
        """Validate Python code examples."""
        try:
            # Basic syntax check
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            self.issues.append(f"Python syntax error in {file_path}: {e}")
        
        # Check for common issues
        if 'import requests' in code and 'response.raise_for_status()' not in code:
            self.warnings.append(f"Missing error handling in {file_path}")
    
    def _validate_js_code(self, code: str, file_path: str) -> None:
        """Validate JavaScript/TypeScript code examples."""
        # Basic checks for common issues
        if 'await ' in code and 'async ' not in code:
            self.warnings.append(f"Await without async in {file_path}")
        
        if 'fetch(' in code and '.catch(' not in code and 'try' not in code:
            self.warnings.append(f"Missing error handling for fetch in {file_path}")
    
    def _validate_bash_code(self, code: str, file_path: str) -> None:
        """Validate Bash code examples."""
        lines = code.strip().split('\n')
        for line in lines:
            if line.strip().startswith('curl') and '-f' not in line:
                self.warnings.append(f"Curl without -f flag in {file_path}")
    
    def validate_api_consistency(self) -> None:
        """Validate API documentation consistency."""
        print("🔄 Validating API consistency...")
        
        try:
            # Check if OpenAPI spec exists
            openapi_path = self.root_dir / "backend" / "openapi.json"
            if not openapi_path.exists():
                self.warnings.append("OpenAPI spec not found - generating...")
                self._generate_openapi_spec()
            
            # Load OpenAPI spec
            with open(openapi_path, 'r') as f:
                openapi_spec = json.load(f)
            
            # Validate against documentation
            self._validate_endpoints_documentation(openapi_spec)
            self._validate_schemas_documentation(openapi_spec)
            
        except Exception as e:
            self.issues.append(f"Failed to validate API consistency: {e}")
    
    def _generate_openapi_spec(self) -> None:
        """Generate OpenAPI specification."""
        try:
            backend_dir = self.root_dir / "backend"
            os.chdir(backend_dir)
            
            result = subprocess.run([
                sys.executable, "-c",
                "from app.main import app; import json; print(json.dumps(app.openapi(), indent=2))"
            ], capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "."})
            
            if result.returncode == 0:
                with open("openapi.json", "w") as f:
                    f.write(result.stdout)
            
        except Exception as e:
            self.warnings.append(f"Failed to generate OpenAPI spec: {e}")
        finally:
            os.chdir(self.root_dir)
    
    def _validate_endpoints_documentation(self, openapi_spec: Dict[str, Any]) -> None:
        """Validate endpoints documentation."""
        endpoints_file = self.docs_dir / "api" / "endpoints.md"
        
        if not endpoints_file.exists():
            self.issues.append("API endpoints documentation missing")
            return
        
        content = endpoints_file.read_text(encoding='utf-8')
        
        # Check if all endpoints are documented
        paths = openapi_spec.get("paths", {})
        for path, methods in paths.items():
            if path not in content:
                self.warnings.append(f"Endpoint not documented: {path}")
    
    def _validate_schemas_documentation(self, openapi_spec: Dict[str, Any]) -> None:
        """Validate schemas documentation."""
        schemas_file = self.docs_dir / "api" / "schemas.md"
        
        if not schemas_file.exists():
            self.issues.append("API schemas documentation missing")
            return
        
        content = schemas_file.read_text(encoding='utf-8')
        
        # Check if all schemas are documented
        schemas = openapi_spec.get("components", {}).get("schemas", {})
        for schema_name in schemas.keys():
            if schema_name not in content:
                self.warnings.append(f"Schema not documented: {schema_name}")
    
    def validate_notebooks(self) -> None:
        """Validate Jupyter notebooks."""
        print("📓 Validating Jupyter notebooks...")
        
        notebook_files = list(self.examples_dir.glob("**/*.ipynb"))
        
        if not notebook_files:
            self.warnings.append("No Jupyter notebooks found")
            return
        
        for notebook_file in notebook_files:
            try:
                with open(notebook_file, 'r', encoding='utf-8') as f:
                    notebook = json.load(f)
                
                # Basic structure validation
                if 'cells' not in notebook:
                    self.issues.append(f"Invalid notebook structure: {notebook_file.name}")
                    continue
                
                # Check for empty notebooks
                if len(notebook['cells']) == 0:
                    self.warnings.append(f"Empty notebook: {notebook_file.name}")
                
                # Check for markdown cells with content
                markdown_cells = [cell for cell in notebook['cells'] if cell['cell_type'] == 'markdown']
                if not markdown_cells:
                    self.warnings.append(f"No documentation in notebook: {notebook_file.name}")
                
            except json.JSONDecodeError:
                self.issues.append(f"Invalid JSON in notebook: {notebook_file.name}")
            except Exception as e:
                self.issues.append(f"Error validating notebook {notebook_file.name}: {e}")
    
    def report_results(self) -> bool:
        """Report validation results."""
        print("\n" + "="*60)
        print("📊 VALIDATION RESULTS")
        print("="*60)
        
        if self.issues:
            print(f"\n❌ {len(self.issues)} ISSUES FOUND:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i:2d}. {issue}")
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} WARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i:2d}. {warning}")
        
        if not self.issues and not self.warnings:
            print("\n✅ ALL VALIDATION CHECKS PASSED!")
            return True
        elif not self.issues:
            print(f"\n✅ No critical issues found ({len(self.warnings)} warnings)")
            return True
        else:
            print(f"\n❌ Validation failed with {len(self.issues)} issues")
            return False
    
    def fix_common_issues(self) -> None:
        """Automatically fix common documentation issues."""
        print("🔧 Attempting to fix common issues...")
        
        fixed_count = 0
        
        # Fix trailing whitespace
        for md_file in self.docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            original_content = content
            
            # Remove trailing whitespace
            lines = content.split('\n')
            lines = [line.rstrip() for line in lines]
            content = '\n'.join(lines)
            
            # Ensure file ends with newline
            if content and not content.endswith('\n'):
                content += '\n'
            
            if content != original_content:
                md_file.write_text(content, encoding='utf-8')
                fixed_count += 1
        
        if fixed_count > 0:
            print(f"✅ Fixed issues in {fixed_count} files")
        else:
            print("ℹ️  No auto-fixable issues found")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Meridian Ephemeris Documentation")
    parser.add_argument("--fix", action="store_true", help="Automatically fix common issues")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")
    
    args = parser.parse_args()
    
    validator = DocumentationValidator()
    
    if args.fix:
        validator.fix_common_issues()
    
    if not args.quiet:
        success = validator.validate_all()
    else:
        # Run validation but suppress most output
        import contextlib
        import io
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            success = validator.validate_all()
        
        # Only show results
        output = f.getvalue()
        results_start = output.find("VALIDATION RESULTS")
        if results_start != -1:
            print(output[results_start:])
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()