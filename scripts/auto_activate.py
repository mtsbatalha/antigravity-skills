#!/usr/bin/env python3
"""
Auto-Activate Skills - Analyze a target project and activate relevant skills.

Modes:
  focus   (default) - Disable irrelevant skills, keep only matching ones
  restore           - Re-enable all disabled skills back to active

Usage:
  # Analyze an existing project
  python scripts/auto_activate.py --target /path/to/project --dry-run
  python scripts/auto_activate.py --target /path/to/project

  # New project from scratch - declare your stack manually
  python scripts/auto_activate.py --stack react typescript next tailwindcss prisma
  python scripts/auto_activate.py --stack python fastapi postgres docker
  python scripts/auto_activate.py --stack flutter dart firebase

  # Combine both (target project + extra techs you plan to add)
  python scripts/auto_activate.py --target ./my-app --stack docker kubernetes aws

  # Other options
  python scripts/auto_activate.py --target . --verbose --max-skills 30
  python scripts/auto_activate.py --target . --keep bash-pro --skip unity-developer
  python scripts/auto_activate.py restore
"""

import sys
import os
import json
import re
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

# Ensure UTF-8 output for Windows compatibility
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import enable/disable from skills_manager
sys.path.insert(0, os.path.dirname(__file__))
from skills_manager import enable_skill, disable_skill, SKILLS_DIR, DISABLED_DIR

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SKIP_DIRS = {
    'node_modules', '.git', 'venv', '.venv', '__pycache__', 'dist', 'build',
    '.next', '.nuxt', '.output', 'target', 'vendor', '.disabled', '.tox',
    'env', '.env', 'egg-info', '.eggs', 'site-packages',
}

LANG_EXTENSIONS = {
    '.py': 'python',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.go': 'golang',
    '.rs': 'rust',
    '.java': 'java',
    '.kt': 'kotlin',
    '.rb': 'ruby',
    '.php': 'php',
    '.cs': 'csharp',
    '.swift': 'swift',
    '.dart': 'dart',
    '.scala': 'scala',
    '.cpp': 'cpp',
    '.c': 'c',
    '.lua': 'lua',
    '.ex': 'elixir',
    '.exs': 'elixir',
    '.sol': 'solidity',
}

MIN_FILES_FOR_LANG = 3

# Aliases: normalize variant names to canonical signal
ALIASES = {
    'nextjs': 'next', 'next.js': 'next',
    'reactjs': 'react', 'react.js': 'react',
    'vuejs': 'vue', 'vue.js': 'vue',
    'k8s': 'kubernetes',
    'pg': 'postgres', 'postgresql': 'postgres',
    'node': 'nodejs', 'node.js': 'nodejs',
    'expressjs': 'express', 'express.js': 'express',
    'nestjs': 'nestjs',
    'csharp': 'dotnet', 'c#': 'dotnet',
    'aspnet': 'dotnet', 'asp.net': 'dotnet',
    'tensorflow': 'tensorflow', 'tf': 'tensorflow',
    'pytorch': 'pytorch', 'torch': 'pytorch',
    'sklearn': 'scikit-learn',
}

# Explicit technology -> skill ID mapping (highest confidence)
TECH_TO_SKILLS = {
    # Languages
    'python': ['python-pro', 'python-patterns', 'python-testing-patterns', 'python-performance-optimization', 'python-packaging'],
    'typescript': ['typescript-pro', 'typescript-expert', 'typescript-advanced-types'],
    'javascript': ['javascript-pro', 'javascript-mastery', 'modern-javascript-patterns', 'javascript-testing-patterns'],
    'golang': ['golang-pro', 'go-concurrency-patterns'],
    'rust': ['rust-pro', 'rust-async-patterns', 'memory-safety-patterns'],
    'java': ['java-pro'],
    'ruby': ['ruby-pro'],
    'php': ['php-pro'],
    'scala': ['scala-pro'],
    'dart': ['flutter-expert'],
    'swift': ['swiftui-expert-skill', 'ios-developer'],
    'kotlin': ['android-jetpack-compose-expert'],
    'solidity': ['solidity-security'],

    # Frontend frameworks
    'react': ['react-best-practices', 'react-patterns', 'react-state-management', 'react-ui-patterns', 'react-modernization'],
    'next': ['nextjs-best-practices', 'nextjs-app-router-patterns', 'react-nextjs-development'],
    'angular': ['angular'],
    'vue': [],
    'svelte': [],
    'tailwindcss': [],
    'three': ['3d-web-experience'],
    'zustand': ['zustand-store-ts'],

    # Backend frameworks
    'fastapi': ['fastapi-pro', 'fastapi-templates', 'fastapi-router-py', 'python-fastapi-development'],
    'django': ['django-pro'],
    'flask': ['python-pro'],
    'express': ['nodejs-backend-patterns', 'nodejs-best-practices'],
    'nestjs': ['nestjs-expert'],
    'laravel': ['laravel-expert', 'laravel-security-audit'],
    'dotnet': ['dotnet-architect', 'dotnet-backend', 'dotnet-backend-patterns'],
    'spring': ['java-pro'],
    'rails': ['ruby-pro'],

    # ORMs / DB tools
    'prisma': ['prisma-expert'],
    'drizzle': ['drizzle-orm-expert'],
    'pydantic': ['pydantic-models-py'],
    'sqlalchemy': ['python-pro'],

    # Infrastructure
    'docker': ['docker-expert'],
    'kubernetes': ['kubernetes-architect', 'kubernetes-deployment', 'k8s-manifest-generator', 'k8s-security-policies', 'helm-chart-scaffolding'],
    'terraform': [],
    'helm': ['helm-chart-scaffolding'],

    # CI/CD
    'github-actions': ['gitops-workflow'],
    'gitlab-ci': ['gitlab-ci-patterns'],

    # Cloud
    'aws': ['aws-serverless', 'cdk-patterns'],
    'azure': ['azure-functions'],
    'firebase': ['firebase'],
    'supabase': ['supabase-automation', 'nextjs-supabase-auth'],
    'vercel': ['vercel-deployment'],

    # Databases
    'postgres': ['postgres-best-practices', 'postgresql', 'postgresql-optimization', 'sql-pro'],
    'sql': ['sql-pro', 'sql-optimization-patterns'],
    'redis': [],
    'mongodb': ['database-architect'],
    'neon': ['neon-postgres', 'using-neon'],

    # Mobile
    'react-native': ['react-native-architecture'],
    'flutter': ['flutter-expert'],
    'expo': ['expo-deployment'],
    'android': ['android-jetpack-compose-expert'],
    'ios': ['ios-developer', 'swiftui-expert-skill'],

    # AI/ML
    'pytorch': ['ml-engineer'],
    'tensorflow': ['ml-engineer'],
    'scikit-learn': ['data-scientist'],
    'langchain': ['rag-implementation'],
    'openai': ['llm-app-patterns'],

    # Auth
    'auth': ['auth-implementation-patterns', 'security-audit', 'cc-skill-security-review'],
    'clerk': ['clerk-auth'],
    'stripe': ['stripe-integration', 'payment-integration'],

    # Testing
    'playwright': ['go-playwright'],
    'jest': ['javascript-testing-patterns'],
    'pytest': ['python-testing-patterns'],
    'cypress': ['e2e-testing-patterns'],

    # Game engines
    'unity': ['unity-developer', 'unity-ecs-patterns'],
    'godot': [],
    'bevy': ['bevy-ecs-expert'],

    # Messaging
    'bullmq': ['bullmq-specialist'],
    'graphql': ['graphql', 'graphql-architect'],
    'grpc': ['grpc-golang'],

    # Misc
    'convex': ['convex'],
    'temporal': ['temporal-python-pro', 'temporal-golang-pro'],
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ProjectContext:
    languages: set = field(default_factory=set)
    frameworks: set = field(default_factory=set)
    infrastructure: set = field(default_factory=set)
    databases: set = field(default_factory=set)
    cloud_providers: set = field(default_factory=set)
    ci_cd: set = field(default_factory=set)
    security_signals: set = field(default_factory=set)
    mobile: set = field(default_factory=set)
    ai_ml: set = field(default_factory=set)
    testing: set = field(default_factory=set)
    misc: set = field(default_factory=set)

    @property
    def all_signals(self):
        return (self.languages | self.frameworks | self.infrastructure |
                self.databases | self.cloud_providers | self.ci_cd |
                self.security_signals | self.mobile | self.ai_ml |
                self.testing | self.misc)

    def is_empty(self):
        return len(self.all_signals) == 0


@dataclass
class ScoredSkill:
    id: str
    score: int
    reasons: list
    name: str = ''
    description: str = ''


# ---------------------------------------------------------------------------
# Phase 1: Project Analysis
# ---------------------------------------------------------------------------

def normalize_signal(s):
    """Normalize a signal name using aliases."""
    s = s.lower().strip()
    return ALIASES.get(s, s)


def detect_languages(target):
    """Count file extensions and return languages with >= MIN_FILES_FOR_LANG files."""
    counts = {}
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in LANG_EXTENSIONS:
                lang = LANG_EXTENSIONS[ext]
                counts[lang] = counts.get(lang, 0) + 1
    return {lang for lang, count in counts.items() if count >= MIN_FILES_FOR_LANG}


def detect_from_package_json(target):
    """Parse package.json for Node.js/frontend dependencies."""
    signals = set()
    pkg_path = Path(target) / 'package.json'
    if not pkg_path.exists():
        return signals

    try:
        with open(pkg_path, 'r', encoding='utf-8') as f:
            pkg = json.load(f)
    except (json.JSONDecodeError, OSError):
        return signals

    signals.add('nodejs')
    all_deps = {}
    all_deps.update(pkg.get('dependencies', {}))
    all_deps.update(pkg.get('devDependencies', {}))

    # Map known package names to signals
    dep_map = {
        'react': 'react', 'react-dom': 'react',
        'next': 'next',
        '@angular/core': 'angular',
        'vue': 'vue', 'nuxt': 'nuxt',
        'svelte': 'svelte', '@sveltejs/kit': 'svelte',
        'express': 'express',
        '@nestjs/core': 'nestjs',
        'fastify': 'fastify',
        'three': 'three', '@react-three/fiber': 'three',
        'tailwindcss': 'tailwindcss',
        'prisma': 'prisma', '@prisma/client': 'prisma',
        'drizzle-orm': 'drizzle',
        'zustand': 'zustand',
        '@supabase/supabase-js': 'supabase',
        'firebase': 'firebase',
        'stripe': 'stripe',
        '@clerk/nextjs': 'clerk', '@clerk/clerk-react': 'clerk',
        'bullmq': 'bullmq',
        'graphql': 'graphql', '@apollo/client': 'graphql',
        'playwright': 'playwright', '@playwright/test': 'playwright',
        'jest': 'jest',
        'cypress': 'cypress',
        'electron': 'electron',
        'react-native': 'react-native',
        'expo': 'expo',
        '@trigger.dev/sdk': 'trigger-dev',
        'convex': 'convex',
        'openai': 'openai',
        'langchain': 'langchain',
        '@vercel/analytics': 'vercel',
        'remotion': 'remotion',
        'discord.js': 'discord',
    }

    for dep_name in all_deps:
        normalized = dep_name.lower()
        if normalized in dep_map:
            signals.add(dep_map[normalized])

    return signals


def detect_from_requirements(target):
    """Parse Python requirements files for dependencies."""
    signals = set()
    req_files = ['requirements.txt', 'requirements-dev.txt', 'requirements_dev.txt']

    for req_file in req_files:
        req_path = Path(target) / req_file
        if not req_path.exists():
            continue
        try:
            with open(req_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('-'):
                        continue
                    # Extract package name (before version specifier)
                    pkg = re.split(r'[>=<!\[;]', line)[0].strip().lower().replace('_', '-')
                    signals.add(pkg)
        except OSError:
            continue

    # Also check pyproject.toml
    pyproject = Path(target) / 'pyproject.toml'
    if pyproject.exists():
        try:
            with open(pyproject, 'r', encoding='utf-8') as f:
                content = f.read()
            # Simple extraction of dependency names from [project.dependencies] or [tool.poetry.dependencies]
            in_deps = False
            for line in content.splitlines():
                if re.match(r'\[(project\.)?dependencies\]', line) or re.match(r'\[tool\.poetry\.dependencies\]', line):
                    in_deps = True
                    continue
                if in_deps:
                    if line.startswith('['):
                        in_deps = False
                        continue
                    match = re.match(r'^"?([a-zA-Z0-9_-]+)"?\s*[=,]', line)
                    if match:
                        signals.add(match.group(1).lower().replace('_', '-'))
        except OSError:
            pass

    # Map known Python packages to canonical signals
    pkg_map = {
        'fastapi': 'fastapi', 'django': 'django', 'flask': 'flask',
        'sqlalchemy': 'sqlalchemy', 'pydantic': 'pydantic',
        'celery': 'celery', 'pytest': 'pytest',
        'pytorch': 'pytorch', 'torch': 'pytorch',
        'tensorflow': 'tensorflow', 'scikit-learn': 'scikit-learn',
        'pandas': 'pandas', 'numpy': 'numpy',
        'langchain': 'langchain', 'openai': 'openai',
        'stripe': 'stripe', 'boto3': 'aws', 'botocore': 'aws',
        'redis': 'redis', 'psycopg2': 'postgres', 'psycopg2-binary': 'postgres',
        'asyncpg': 'postgres', 'pymongo': 'mongodb',
        'grpcio': 'grpc', 'temporalio': 'temporal',
    }

    mapped = set()
    for pkg in signals:
        if pkg in pkg_map:
            mapped.add(pkg_map[pkg])
    return mapped


def detect_from_cargo_toml(target):
    """Parse Cargo.toml for Rust dependencies."""
    signals = set()
    cargo = Path(target) / 'Cargo.toml'
    if not cargo.exists():
        return signals

    try:
        with open(cargo, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError:
        return signals

    dep_map = {
        'tokio': 'tokio', 'actix-web': 'actix', 'axum': 'axum',
        'bevy': 'bevy', 'serde': 'serde', 'warp': 'warp',
    }

    in_deps = False
    for line in content.splitlines():
        if re.match(r'\[.*dependencies.*\]', line):
            in_deps = True
            continue
        if in_deps:
            if line.startswith('['):
                in_deps = False
                continue
            match = re.match(r'^([a-zA-Z0-9_-]+)', line)
            if match:
                crate = match.group(1).lower()
                if crate in dep_map:
                    signals.add(dep_map[crate])

    return signals


def detect_from_go_mod(target):
    """Parse go.mod for Go dependencies."""
    signals = set()
    gomod = Path(target) / 'go.mod'
    if not gomod.exists():
        return signals

    try:
        with open(gomod, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError:
        return signals

    dep_map = {
        'gin': 'gin', 'fiber': 'fiber', 'echo': 'echo',
        'grpc': 'grpc', 'temporal': 'temporal',
    }

    for line in content.splitlines():
        line_lower = line.lower()
        for key, signal in dep_map.items():
            if key in line_lower:
                signals.add(signal)

    return signals


def detect_from_composer_json(target):
    """Parse composer.json for PHP dependencies."""
    signals = set()
    composer = Path(target) / 'composer.json'
    if not composer.exists():
        return signals

    try:
        with open(composer, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return signals

    all_deps = {}
    all_deps.update(data.get('require', {}))
    all_deps.update(data.get('require-dev', {}))

    for dep in all_deps:
        dep_lower = dep.lower()
        if 'laravel' in dep_lower:
            signals.add('laravel')
        if 'symfony' in dep_lower:
            signals.add('symfony')
        if 'wordpress' in dep_lower:
            signals.add('wordpress')

    return signals


def detect_infrastructure(target):
    """Detect infrastructure files."""
    signals = set()
    target = Path(target)

    # Docker
    if (target / 'Dockerfile').exists() or (target / 'docker-compose.yml').exists() or (target / 'docker-compose.yaml').exists():
        signals.add('docker')

    # Kubernetes
    if (target / 'Chart.yaml').exists() or (target / 'helm').is_dir():
        signals.add('kubernetes')
        signals.add('helm')

    # Terraform
    for f in target.glob('*.tf'):
        signals.add('terraform')
        break

    # CI/CD
    if (target / '.github' / 'workflows').is_dir():
        signals.add('github-actions')
    if (target / '.gitlab-ci.yml').exists():
        signals.add('gitlab-ci')
    if (target / 'Jenkinsfile').exists():
        signals.add('jenkins')

    # K8s manifests (check YAML files for kind: Deployment etc.)
    for yaml_file in target.glob('**/*.yaml'):
        if any(skip in str(yaml_file) for skip in SKIP_DIRS):
            continue
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                head = f.read(500)
            if re.search(r'kind:\s*(Deployment|Service|Pod|StatefulSet|DaemonSet|Ingress)', head):
                signals.add('kubernetes')
                break
        except OSError:
            continue

    return signals


def detect_databases(target):
    """Detect database-related signals."""
    signals = set()
    target = Path(target)

    if (target / 'prisma').is_dir() or (target / 'prisma' / 'schema.prisma').exists():
        signals.add('prisma')
    if (target / 'drizzle').is_dir():
        signals.add('drizzle')
    if (target / 'migrations').is_dir() or (target / 'alembic').is_dir():
        signals.add('sql')

    sql_files = list(target.glob('**/*.sql'))
    sql_files = [f for f in sql_files if not any(skip in str(f) for skip in SKIP_DIRS)]
    if len(sql_files) >= 2:
        signals.add('sql')

    return signals


def detect_mobile(target):
    """Detect mobile development signals."""
    signals = set()
    target = Path(target)

    if (target / 'ios').is_dir():
        signals.add('ios')
    if (target / 'android').is_dir():
        signals.add('android')
    if (target / 'pubspec.yaml').exists():
        signals.add('flutter')
    if (target / 'app.json').exists() and (target / 'node_modules' / 'expo').is_dir():
        signals.add('expo')
        signals.add('react-native')

    return signals


def detect_cloud_providers(target):
    """Detect cloud provider usage from config files."""
    signals = set()
    target = Path(target)

    # AWS
    if (target / 'serverless.yml').exists() or (target / 'template.yaml').exists() or (target / 'samconfig.toml').exists():
        signals.add('aws')
    if (target / 'cdk.json').exists():
        signals.add('aws')

    # Azure
    if (target / 'azure-pipelines.yml').exists() or (target / '.azure').is_dir():
        signals.add('azure')

    # Vercel
    if (target / 'vercel.json').exists():
        signals.add('vercel')

    # Firebase
    if (target / 'firebase.json').exists() or (target / '.firebaserc').exists():
        signals.add('firebase')

    # Supabase
    if (target / 'supabase').is_dir():
        signals.add('supabase')

    return signals


def detect_security_signals(target):
    """Detect auth/security related files."""
    signals = set()
    target = Path(target)

    auth_patterns = ['auth', 'oauth', 'jwt', 'passport', 'keycloak']
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        for f in files:
            f_lower = f.lower()
            for pattern in auth_patterns:
                if pattern in f_lower:
                    signals.add('auth')
                    return signals  # one signal is enough
    return signals


def analyze_project(target):
    """Run all detectors and build a ProjectContext."""
    ctx = ProjectContext()
    target = Path(target).resolve()

    if not target.is_dir():
        print(f"Error: {target} is not a directory")
        sys.exit(1)

    ctx.languages = detect_languages(target)
    ctx.frameworks = detect_from_package_json(target)
    ctx.frameworks |= detect_from_requirements(target)
    ctx.frameworks |= detect_from_cargo_toml(target)
    ctx.frameworks |= detect_from_go_mod(target)
    ctx.frameworks |= detect_from_composer_json(target)
    ctx.infrastructure = detect_infrastructure(target)
    ctx.databases = detect_databases(target)
    ctx.cloud_providers = detect_cloud_providers(target)
    ctx.mobile = detect_mobile(target)
    ctx.security_signals = detect_security_signals(target)

    # Normalize all signals
    ctx.languages = {normalize_signal(s) for s in ctx.languages}
    ctx.frameworks = {normalize_signal(s) for s in ctx.frameworks}
    ctx.infrastructure = {normalize_signal(s) for s in ctx.infrastructure}
    ctx.databases = {normalize_signal(s) for s in ctx.databases}
    ctx.cloud_providers = {normalize_signal(s) for s in ctx.cloud_providers}
    ctx.mobile = {normalize_signal(s) for s in ctx.mobile}
    ctx.security_signals = {normalize_signal(s) for s in ctx.security_signals}

    return ctx


# ---------------------------------------------------------------------------
# Phase 2: Skill Scoring
# ---------------------------------------------------------------------------

def load_catalog(catalog_path):
    """Load catalog.json skills list."""
    with open(catalog_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('skills', data) if isinstance(data, dict) else data


def load_common_skills(bundles_path):
    """Load the 'common' skills list from bundles.json."""
    try:
        with open(bundles_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return set(data.get('common', []))
    except (OSError, json.JSONDecodeError):
        return set()


def score_skills(context, catalog, common_skills):
    """Score each skill against the project context."""
    signals = context.all_signals
    if not signals:
        return []

    # Build reverse map: skill_id -> direct tech_map score
    tech_map_ids = {}
    for signal, skill_ids in TECH_TO_SKILLS.items():
        if signal in signals:
            for sid in skill_ids:
                tech_map_ids[sid] = tech_map_ids.get(sid, 0) + 15

    scored = []
    for skill in catalog:
        skill_id = skill.get('id', '')
        score = 0
        reasons = []

        # Layer 1: Tech map direct match (+15 per match)
        if skill_id in tech_map_ids:
            score += tech_map_ids[skill_id]
            reasons.append(f"tech_map:+{tech_map_ids[skill_id]}")

        # Layer 2: ID segment match (+10 per signal)
        id_parts = set(skill_id.split('-'))
        id_overlap = id_parts & signals
        if id_overlap:
            bonus = len(id_overlap) * 10
            score += bonus
            reasons.append(f"id:{','.join(sorted(id_overlap))}:+{bonus}")

        # Layer 3: Tag match (+8 per tag)
        skill_tags = set(t.lower() for t in skill.get('tags', []))
        tag_overlap = skill_tags & signals
        if tag_overlap:
            bonus = len(tag_overlap) * 8
            score += bonus
            reasons.append(f"tags:{','.join(sorted(tag_overlap))}:+{bonus}")

        # Layer 4: Trigger match (+2 per trigger, max 12)
        skill_triggers = set(t.lower() for t in skill.get('triggers', []))
        trigger_overlap = skill_triggers & signals
        if trigger_overlap:
            bonus = min(len(trigger_overlap) * 2, 12)
            score += bonus
            reasons.append(f"triggers:{len(trigger_overlap)}x:+{bonus}")

        # Layer 5: Common skills bonus (+5 if any signal matches)
        if skill_id in common_skills and score > 0:
            score += 5
            reasons.append("common:+5")

        if score > 0:
            scored.append(ScoredSkill(
                id=skill_id,
                score=score,
                reasons=reasons,
                name=skill.get('name', skill_id),
                description=skill.get('description', '')[:80],
            ))

    scored.sort(key=lambda s: s.score, reverse=True)
    return scored


# ---------------------------------------------------------------------------
# Phase 3: Activation / Deactivation
# ---------------------------------------------------------------------------

def get_filesystem_state():
    """Return sets of active and disabled skill IDs on disk."""
    active = set()
    if SKILLS_DIR.exists():
        active = {d.name for d in SKILLS_DIR.iterdir()
                  if d.is_dir() and not d.name.startswith('.')}

    disabled = set()
    if DISABLED_DIR.exists():
        disabled = {d.name for d in DISABLED_DIR.iterdir() if d.is_dir()}

    return active, disabled


def compute_changes(scored, threshold, max_skills, keep, skip, active, disabled):
    """Compute which skills to activate, deactivate, and leave unchanged."""
    # Target set: top N skills above threshold
    target_ids = set()
    for s in scored:
        if len(target_ids) >= max_skills:
            break
        if s.id not in skip and s.score >= threshold:
            target_ids.add(s.id)

    # Always keep pinned skills
    target_ids |= keep

    all_known = active | disabled

    to_activate = []    # skills to move from .disabled -> active
    to_deactivate = []  # skills to move from active -> .disabled
    unchanged = []

    score_map = {s.id: s for s in scored}

    for skill_id in sorted(all_known):
        in_target = skill_id in target_ids
        is_active = skill_id in active
        is_disabled = skill_id in disabled
        info = score_map.get(skill_id)

        if in_target and is_disabled:
            to_activate.append((skill_id, info))
        elif not in_target and is_active and skill_id not in keep:
            to_deactivate.append((skill_id, info))
        else:
            unchanged.append((skill_id, info))

    return to_activate, to_deactivate, unchanged


def apply_changes(to_activate, to_deactivate, dry_run):
    """Apply enable/disable changes after user confirmation."""
    if dry_run:
        return

    total_changes = len(to_activate) + len(to_deactivate)
    if total_changes == 0:
        return

    # Ask for confirmation
    print(f"  This will activate {len(to_activate)} and deactivate {len(to_deactivate)} skills.")
    try:
        answer = input("  Proceed? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n  Aborted.")
        return

    if answer not in ('y', 'yes'):
        print("  Aborted. No changes made.")
        return

    DISABLED_DIR.mkdir(exist_ok=True)

    for skill_id, _ in to_activate:
        enable_skill(skill_id)

    for skill_id, _ in to_deactivate:
        disable_skill(skill_id)

    print(f"\n  Done. {len(to_activate)} activated, {len(to_deactivate)} deactivated.")


def restore_all():
    """Re-enable all disabled skills."""
    if not DISABLED_DIR.exists():
        print("  No disabled skills found. Nothing to restore.")
        return

    disabled = [d for d in DISABLED_DIR.iterdir() if d.is_dir()]
    if not disabled:
        print("  No disabled skills found. Nothing to restore.")
        return

    print(f"  Found {len(disabled)} disabled skills to restore.")
    try:
        answer = input("  Restore all? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n  Aborted.")
        return

    if answer not in ('y', 'yes'):
        print("  Aborted.")
        return

    count = 0
    for d in disabled:
        target = SKILLS_DIR / d.name
        if not target.exists():
            d.rename(target)
            count += 1
            print(f"    + {d.name}")
        else:
            print(f"    ~ {d.name} (already exists, skipped)")

    print(f"\n  Restored {count} skills.")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_context(ctx, target):
    """Print detected project context."""
    print("=" * 60)
    print(f"  PROJECT ANALYSIS: {target}")
    print("=" * 60)

    sections = [
        ("Languages", ctx.languages),
        ("Frameworks", ctx.frameworks),
        ("Infrastructure", ctx.infrastructure),
        ("Databases", ctx.databases),
        ("Cloud", ctx.cloud_providers),
        ("CI/CD", ctx.ci_cd),
        ("Mobile", ctx.mobile),
        ("Security", ctx.security_signals),
        ("Stack", ctx.misc),
    ]

    for label, values in sections:
        if values:
            print(f"  {label:16s} {', '.join(sorted(values))}")

    print()


def print_report(to_activate, to_deactivate, unchanged, dry_run, scored, threshold):
    """Print activation plan."""
    print("=" * 60)
    print("  SKILL ACTIVATION PLAN")
    print("=" * 60)

    active_skills = [s for s in scored if s.score >= threshold]

    if to_activate:
        print(f"\n  To Activate ({len(to_activate)}):")
        for skill_id, info in to_activate[:30]:
            score_str = f"(score: {info.score})" if info else "(pinned)"
            print(f"    + {skill_id:45s} {score_str}")
        if len(to_activate) > 30:
            print(f"    ... and {len(to_activate) - 30} more")

    if to_deactivate:
        print(f"\n  To Deactivate ({len(to_deactivate)}):")
        shown = to_deactivate[:15]
        for skill_id, info in shown:
            score_str = f"(score: {info.score})" if info else "(score: 0)"
            print(f"    - {skill_id:45s} {score_str}")
        if len(to_deactivate) > 15:
            print(f"    ... and {len(to_deactivate) - 15} more")

    print(f"\n  Summary:")
    print(f"    Activated:   {len(to_activate)}")
    print(f"    Deactivated: {len(to_deactivate)}")
    print(f"    Unchanged:   {len(unchanged)}")
    print(f"    Total:       {len(to_activate) + len(to_deactivate) + len(unchanged)}")

    if active_skills:
        print(f"\n  Active Skills ({len(active_skills)}):")
        for s in active_skills:
            print(f"    * {s.id:45s} (score: {s.score})")

    if dry_run:
        print(f"\n  ** DRY RUN - No changes were made **")

    print()


def print_verbose_scores(scored, threshold):
    """Print detailed scoring for all scored skills."""
    print("\n  Detailed Scores (above threshold):")
    for s in scored:
        if s.score >= threshold:
            print(f"    {s.id:45s} score={s.score:3d}  [{', '.join(s.reasons)}]")
    print()


def write_json_report(path, target, ctx, to_activate, to_deactivate, unchanged):
    """Write machine-readable JSON report."""
    report = {
        "target": str(target),
        "timestamp": datetime.now().isoformat(),
        "context": {
            "languages": sorted(ctx.languages),
            "frameworks": sorted(ctx.frameworks),
            "infrastructure": sorted(ctx.infrastructure),
            "databases": sorted(ctx.databases),
            "cloud_providers": sorted(ctx.cloud_providers),
            "mobile": sorted(ctx.mobile),
            "security_signals": sorted(ctx.security_signals),
        },
        "activated": [{"id": sid, "score": info.score if info else 0, "reasons": info.reasons if info else []} for sid, info in to_activate],
        "deactivated": [{"id": sid, "score": info.score if info else 0} for sid, info in to_deactivate],
        "unchanged_count": len(unchanged),
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"  Report saved to: {path}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Analyze a target project and activate relevant skills automatically.'
    )
    parser.add_argument('command', nargs='?', default='focus',
                        choices=['focus', 'restore'],
                        help='focus (default): analyze project and manage skills. restore: re-enable all disabled skills.')
    parser.add_argument('--target', help='Path to the target project to analyze')
    parser.add_argument('--stack', nargs='+', default=[],
                        help='Declare technologies manually (e.g. --stack react typescript next docker)')
    parser.add_argument('--dry-run', action='store_true', help='Show plan without making changes')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--max-skills', type=int, default=50, help='Maximum skills to activate (default: 50)')
    parser.add_argument('--threshold', type=int, default=8, help='Minimum score to activate (default: 8)')
    parser.add_argument('--verbose', action='store_true', help='Show detailed scoring')
    parser.add_argument('--report-file', help='Write JSON report to file')
    parser.add_argument('--keep', nargs='+', default=[], help='Skills to always keep active')
    parser.add_argument('--skip', nargs='+', default=[], help='Skills to never activate')
    parser.add_argument('--catalog', help='Path to catalog.json (default: data/catalog.json)')

    args = parser.parse_args()

    # Handle restore command
    if args.command == 'restore':
        restore_all()
        return

    # Focus mode requires --target or --stack
    if not args.target and not args.stack:
        parser.error("--target or --stack is required for focus mode")

    # Resolve paths
    base_dir = Path(__file__).parent.parent
    catalog_path = Path(args.catalog) if args.catalog else base_dir / 'data' / 'catalog.json'
    bundles_path = base_dir / 'data' / 'bundles.json'
    target = Path(args.target).resolve() if args.target else None

    if not catalog_path.exists():
        # Fallback to skills_index.json
        catalog_path = base_dir / 'skills_index.json'
        if not catalog_path.exists():
            print(f"Error: catalog not found at {catalog_path}")
            sys.exit(1)

    # Phase 1: Analyze project and/or use declared stack
    if target:
        ctx = analyze_project(target)
    else:
        ctx = ProjectContext()

    # Merge --stack signals into context
    if args.stack:
        for tech in args.stack:
            normalized = normalize_signal(tech.lower())
            ctx.misc.add(normalized)

    label = str(target) if target else "(manual stack)"
    print_context(ctx, label)

    if ctx.is_empty():
        print("  No technologies detected. Nothing to do.")
        sys.exit(0)

    # Phase 2: Score
    catalog = load_catalog(catalog_path)
    common_skills = load_common_skills(bundles_path)
    scored = score_skills(ctx, catalog, common_skills)

    if args.verbose:
        print_verbose_scores(scored, args.threshold)

    # Phase 3: Apply
    active, disabled = get_filesystem_state()
    keep_set = set(args.keep)
    skip_set = set(args.skip)

    to_activate, to_deactivate, unchanged = compute_changes(
        scored, args.threshold, args.max_skills, keep_set, skip_set, active, disabled
    )

    print_report(to_activate, to_deactivate, unchanged, args.dry_run, scored, args.threshold)

    if args.report_file:
        write_json_report(args.report_file, target, ctx, to_activate, to_deactivate, unchanged)

    if args.yes:
        # Skip confirmation
        if not args.dry_run:
            DISABLED_DIR.mkdir(exist_ok=True)
            for skill_id, _ in to_activate:
                enable_skill(skill_id)
            for skill_id, _ in to_deactivate:
                disable_skill(skill_id)
            total = len(to_activate) + len(to_deactivate)
            if total > 0:
                print(f"  Done. {len(to_activate)} activated, {len(to_deactivate)} deactivated.")
    else:
        apply_changes(to_activate, to_deactivate, args.dry_run)


if __name__ == '__main__':
    main()
