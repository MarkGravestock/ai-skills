#!/usr/bin/env python3
"""
Analyse coupling metrics for a codebase.
Calculates afferent/efferent coupling, instability, and identifies hotspots.
"""

import argparse
import os
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PackageMetrics:
    name: str
    afferent: int = 0      # Ca - incoming dependencies (who depends on me)
    efferent: int = 0      # Ce - outgoing dependencies (who I depend on)
    classes: int = 0
    volatility: int = 0    # Git changes in last 6 months
    
    @property
    def instability(self) -> float:
        """I = Ce / (Ca + Ce). Range 0 (stable) to 1 (unstable)."""
        total = self.afferent + self.efferent
        return self.efferent / total if total > 0 else 0.5
    
    @property
    def coupling_score(self) -> float:
        """Combined risk score considering instability and volatility."""
        # High instability + high volatility = high risk
        vol_factor = min(self.volatility / 20, 1.0)  # Normalise to 0-1
        return (self.instability * 0.6) + (vol_factor * 0.4)


def find_java_packages(path: str) -> dict[str, PackageMetrics]:
    """Scan Java codebase and build package metrics."""
    packages = defaultdict(lambda: PackageMetrics(name=""))
    dependencies = defaultdict(set)  # package -> set of packages it imports
    
    for root, _, files in os.walk(path):
        if any(skip in root for skip in ['test', 'target', 'build', '.git']):
            continue
            
        for file in files:
            if not file.endswith('.java'):
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract package
                pkg_match = re.search(r'^package\s+([\w.]+)\s*;', content, re.MULTILINE)
                if not pkg_match:
                    continue
                    
                pkg = pkg_match.group(1)
                if packages[pkg].name == "":
                    packages[pkg].name = pkg
                packages[pkg].classes += 1
                
                # Extract imports
                for match in re.finditer(r'^import\s+(?:static\s+)?([\w.]+)', content, re.MULTILINE):
                    imp = match.group(1)
                    # Skip standard library
                    if imp.startswith(('java.', 'javax.', 'jakarta.', 'org.slf4j', 'lombok')):
                        continue
                    # Get package from import
                    parts = imp.rsplit('.', 1)
                    if len(parts) == 2 and parts[1][0].isupper():
                        imp_pkg = parts[0]
                    else:
                        imp_pkg = imp
                    
                    if imp_pkg != pkg:  # Don't count self-references
                        dependencies[pkg].add(imp_pkg)
                        
            except Exception as e:
                print(f"Warning: {file_path}: {e}")
    
    # Calculate afferent and efferent coupling
    for pkg, deps in dependencies.items():
        packages[pkg].efferent = len(deps)
        for dep in deps:
            if dep in packages:
                packages[dep].afferent += 1
    
    return packages


def get_git_volatility(path: str, packages: dict[str, PackageMetrics]) -> None:
    """Add git-based volatility metrics to packages."""
    try:
        result = subprocess.run(
            ['git', 'log', '--pretty=format:', '--name-only', '--since=6 months ago'],
            cwd=path, capture_output=True, text=True, timeout=30
        )
        
        changes = defaultdict(int)
        for line in result.stdout.split('\n'):
            if line.endswith('.java'):
                # Extract package from file path
                parts = line.replace('/', '.').replace('.java', '').split('.')
                # Find matching package
                for i in range(len(parts), 0, -1):
                    candidate = '.'.join(parts[:i])
                    if candidate in packages:
                        changes[candidate] += 1
                        break
        
        for pkg, count in changes.items():
            if pkg in packages:
                packages[pkg].volatility = count
                
    except Exception as e:
        print(f"Warning: Could not get git history: {e}")


def identify_hotspots(packages: dict[str, PackageMetrics]) -> list[tuple[str, str, float]]:
    """Identify coupling hotspots that need attention."""
    hotspots = []
    
    for name, pkg in packages.items():
        issues = []
        
        # High afferent + high volatility = dangerous (many depend on unstable code)
        if pkg.afferent > 5 and pkg.volatility > 10:
            issues.append(f"Volatile hub: {pkg.afferent} dependents, {pkg.volatility} changes")
        
        # High efferent = high coupling
        if pkg.efferent > 10:
            issues.append(f"High coupling: depends on {pkg.efferent} packages")
        
        # Instability mismatch (stable depending on unstable)
        # This would require tracking dependency directions
        
        if issues:
            hotspots.append((name, '; '.join(issues), pkg.coupling_score))
    
    return sorted(hotspots, key=lambda x: -x[2])


def print_report(packages: dict[str, PackageMetrics], hotspots: list) -> None:
    """Print the coupling analysis report."""
    print("\n" + "=" * 70)
    print("COUPLING METRICS REPORT")
    print("=" * 70)
    
    # Summary
    total_packages = len(packages)
    avg_instability = sum(p.instability for p in packages.values()) / total_packages if total_packages else 0
    
    print(f"\nSummary:")
    print(f"  Total packages: {total_packages}")
    print(f"  Average instability: {avg_instability:.2f}")
    print(f"  Hotspots identified: {len(hotspots)}")
    
    # Top coupled packages
    print("\n" + "-" * 70)
    print("TOP 15 PACKAGES BY COUPLING")
    print("-" * 70)
    print(f"{'Package':<45} {'Ca':>5} {'Ce':>5} {'I':>5} {'Vol':>5}")
    print("-" * 70)
    
    sorted_pkgs = sorted(packages.values(), key=lambda p: p.efferent + p.afferent, reverse=True)[:15]
    for pkg in sorted_pkgs:
        print(f"{pkg.name[:44]:<45} {pkg.afferent:>5} {pkg.efferent:>5} {pkg.instability:>5.2f} {pkg.volatility:>5}")
    
    print("\nLegend: Ca=Afferent(incoming), Ce=Efferent(outgoing), I=Instability, Vol=Git changes")
    
    # Hotspots
    if hotspots:
        print("\n" + "-" * 70)
        print("⚠️  COUPLING HOTSPOTS (require attention)")
        print("-" * 70)
        for name, issue, score in hotspots[:10]:
            print(f"\n• {name}")
            print(f"  Risk score: {score:.2f}")
            print(f"  Issue: {issue}")
    
    # Recommendations
    print("\n" + "-" * 70)
    print("RECOMMENDATIONS")
    print("-" * 70)
    
    # Find packages that should be stable but aren't
    unstable_hubs = [p for p in packages.values() if p.afferent > 5 and p.instability > 0.7]
    if unstable_hubs:
        print("\n1. Stabilise these high-dependency packages:")
        for p in unstable_hubs[:5]:
            print(f"   - {p.name} (I={p.instability:.2f}, {p.afferent} dependents)")
    
    # Find packages with too many dependencies
    high_efferent = [p for p in packages.values() if p.efferent > 10]
    if high_efferent:
        print("\n2. Reduce dependencies in these packages:")
        for p in sorted(high_efferent, key=lambda x: -x.efferent)[:5]:
            print(f"   - {p.name} (Ce={p.efferent})")
    
    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Analyse coupling metrics')
    parser.add_argument('--path', '-p', default='.', help='Path to analyse')
    parser.add_argument('--no-git', action='store_true', help='Skip git volatility analysis')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    print(f"Analysing coupling metrics for: {args.path}")
    
    packages = find_java_packages(args.path)
    
    if not args.no_git:
        get_git_volatility(args.path, packages)
    
    hotspots = identify_hotspots(packages)
    
    if args.json:
        import json
        output = {
            'packages': {name: {
                'afferent': p.afferent,
                'efferent': p.efferent,
                'instability': p.instability,
                'volatility': p.volatility,
                'classes': p.classes
            } for name, p in packages.items()},
            'hotspots': [{'name': h[0], 'issue': h[1], 'score': h[2]} for h in hotspots]
        }
        print(json.dumps(output, indent=2))
    else:
        print_report(packages, hotspots)
    
    return 0


if __name__ == '__main__':
    exit(main())
