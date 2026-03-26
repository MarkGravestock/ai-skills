#!/usr/bin/env python3
"""
Detect circular dependencies in a codebase.
Supports Java, TypeScript, and Python.
"""

import argparse
import os
import re
from collections import defaultdict
from pathlib import Path


def find_java_imports(file_path: str) -> list[tuple[str, str]]:
    """Extract package and imports from a Java file."""
    package = None
    imports = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Extract package
    pkg_match = re.search(r'^package\s+([\w.]+)\s*;', content, re.MULTILINE)
    if pkg_match:
        package = pkg_match.group(1)
    
    # Extract imports (excluding java.* and standard libs)
    for match in re.finditer(r'^import\s+(?:static\s+)?([\w.]+)(?:\.\*)?;', content, re.MULTILINE):
        imp = match.group(1)
        # Filter out standard library
        if not imp.startswith(('java.', 'javax.', 'jakarta.', 'org.slf4j', 'lombok')):
            # Get package portion (remove class name)
            parts = imp.rsplit('.', 1)
            if len(parts) == 2 and parts[1][0].isupper():
                imports.append(parts[0])
            else:
                imports.append(imp)
    
    return package, list(set(imports))


def find_ts_imports(file_path: str) -> list[tuple[str, str]]:
    """Extract module and imports from a TypeScript file."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Get relative path as module identifier
    module = str(Path(file_path).parent)
    imports = []
    
    # Match import statements
    for match in re.finditer(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]", content):
        imp = match.group(1)
        if imp.startswith('.'):
            # Resolve relative import
            resolved = str((Path(file_path).parent / imp).resolve())
            imports.append(resolved)
    
    return module, imports


def find_python_imports(file_path: str) -> list[tuple[str, str]]:
    """Extract module and imports from a Python file."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Get module from file path
    module = str(Path(file_path).parent).replace('/', '.')
    imports = []
    
    # Match import statements
    for match in re.finditer(r'^(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))', content, re.MULTILINE):
        imp = match.group(1) or match.group(2)
        if imp and not imp.startswith(('os', 'sys', 'typing', 're', 'json', 'pathlib')):
            imports.append(imp)
    
    return module, list(set(imports))


def build_dependency_graph(path: str, lang: str) -> dict[str, set[str]]:
    """Build a dependency graph from the codebase."""
    graph = defaultdict(set)
    
    extensions = {
        'java': '.java',
        'typescript': '.ts',
        'python': '.py'
    }
    ext = extensions.get(lang, '.java')
    
    parsers = {
        'java': find_java_imports,
        'typescript': find_ts_imports,
        'python': find_python_imports
    }
    parser = parsers.get(lang, find_java_imports)
    
    for root, _, files in os.walk(path):
        # Skip test directories and build outputs
        if any(skip in root for skip in ['test', 'target', 'build', 'node_modules', '__pycache__', '.git']):
            continue
            
        for file in files:
            if file.endswith(ext):
                file_path = os.path.join(root, file)
                try:
                    module, imports = parser(file_path)
                    if module:
                        for imp in imports:
                            graph[module].add(imp)
                except Exception as e:
                    print(f"Warning: Could not parse {file_path}: {e}")
    
    return graph


def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """Find all cycles in the dependency graph using DFS."""
    cycles = []
    visited = set()
    rec_stack = []
    rec_set = set()
    
    def dfs(node: str, path: list[str]):
        if node in rec_set:
            # Found cycle - extract it
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return
        
        if node in visited:
            return
            
        visited.add(node)
        rec_stack.append(node)
        rec_set.add(node)
        
        for neighbour in graph.get(node, []):
            dfs(neighbour, rec_stack.copy())
        
        rec_set.remove(node)
        rec_stack.pop()
    
    for node in graph:
        if node not in visited:
            dfs(node, [])
    
    # Deduplicate cycles (same cycle can be found from different starting points)
    unique_cycles = []
    seen = set()
    for cycle in cycles:
        # Normalise cycle for comparison
        min_idx = cycle.index(min(cycle))
        normalised = tuple(cycle[min_idx:-1] + cycle[:min_idx])
        if normalised not in seen:
            seen.add(normalised)
            unique_cycles.append(cycle)
    
    return unique_cycles


def analyse_cycle_severity(cycle: list[str]) -> str:
    """Assess the severity of a dependency cycle."""
    # Longer cycles are generally worse
    if len(cycle) > 5:
        return "HIGH"
    elif len(cycle) > 3:
        return "MEDIUM"
    return "LOW"


def main():
    parser = argparse.ArgumentParser(description='Detect circular dependencies in a codebase')
    parser.add_argument('--path', '-p', default='.', help='Path to analyse')
    parser.add_argument('--lang', '-l', default='java', choices=['java', 'typescript', 'python'],
                       help='Language to analyse')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    args = parser.parse_args()
    
    print(f"Analysing {args.lang} codebase at: {args.path}")
    print("-" * 60)
    
    graph = build_dependency_graph(args.path, args.lang)
    print(f"Found {len(graph)} modules/packages")
    
    cycles = find_cycles(graph)
    
    if not cycles:
        print("\n✅ No circular dependencies detected!")
        return 0
    
    print(f"\n⚠️  Found {len(cycles)} circular dependency cycle(s):\n")
    
    # Sort by severity
    cycles_with_severity = [(c, analyse_cycle_severity(c)) for c in cycles]
    cycles_with_severity.sort(key=lambda x: ('HIGH', 'MEDIUM', 'LOW').index(x[1]))
    
    for i, (cycle, severity) in enumerate(cycles_with_severity, 1):
        print(f"{i}. [{severity}] {' → '.join(cycle)}")
        if args.verbose:
            print(f"   Length: {len(cycle) - 1} edges")
            print()
    
    print("\n" + "-" * 60)
    print("Recommendations:")
    print("1. Break cycles by introducing interfaces/abstractions")
    print("2. Consider dependency inversion for the longest cycles")
    print("3. Evaluate if cycles indicate misplaced responsibilities")
    
    return 1 if cycles else 0


if __name__ == '__main__':
    exit(main())
