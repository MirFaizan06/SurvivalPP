#!/usr/bin/env python
"""Eclipsed Realms developer CLI.

    python tools/dev.py setup       # one-time: fetch Mojang bedrock-samples + npm typings/validators into .ref/
    python tools/dev.py build       # regenerate every texture / model / JSON / script into build/out
    python tools/dev.py lint        # cross-reference lint + official JSON-schema validation
    python tools/dev.py typecheck   # type-check tools/scripts against the real @minecraft/server typings
    python tools/dev.py test        # runtime smoke test of the scripts against a fake game (tools/test/mock_run.mjs)
    python tools/dev.py package     # zip build/out into releases/<name>.mcaddon
    python tools/dev.py all         # build + lint + typecheck + test + package

Environment overrides: BEDROCK_SAMPLES (path to Mojang/bedrock-samples), SPP_NPM (dir containing node_modules).
"""
import os, subprocess, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / 'tools' / 'gen'
REF = ROOT / '.ref'
os.environ.setdefault('SPP_ROOT', str(ROOT))


def run(cmd, **kw):
    print('>', ' '.join(str(c) for c in cmd))
    r = subprocess.run(cmd, **kw)
    if r.returncode:
        sys.exit(r.returncode)


def setup():
    REF.mkdir(exist_ok=True)
    samples = Path(os.environ.get('BEDROCK_SAMPLES') or REF / 'bedrock-samples')
    if not samples.exists():
        run(['git', 'config', '--global', 'core.longpaths', 'true'])
        run(['git', 'clone', '--depth', '1', 'https://github.com/Mojang/bedrock-samples.git', str(samples)])
    npm = Path(os.environ.get('SPP_NPM') or REF / 'npm')
    npm.mkdir(parents=True, exist_ok=True)
    if not (npm / 'package.json').exists():
        run(['npm', 'init', '-y'], cwd=npm, shell=os.name == 'nt')
    run(['npm', 'install', '--no-audit', '--no-fund', 'typescript@5', 'ajv@8', '@minecraft/server@2.6.0', '@minecraft/server-ui@2.0.0', '@minecraft/common@1'], cwd=npm, shell=os.name == 'nt')
    print('setup complete')


def build():
    run([sys.executable, str(GEN / 'build.py'), '--no-package'], cwd=GEN)


def lint():
    run([sys.executable, str(GEN / 'lint.py')], cwd=GEN)
    run([sys.executable, str(GEN / 'lint2.py')], cwd=GEN)
    run([sys.executable, str(GEN / 'lint3.py')], cwd=GEN)
    run([sys.executable, str(GEN / 'lint4.py')], cwd=GEN)
    run([sys.executable, str(GEN / 'lint5.py')], cwd=GEN)


def test():
    """runtime smoke test: loads the packaged scripts against a fake @minecraft/server and fires events through every module"""
    build_dir = Path(os.environ.get('SPP_BUILD') or ROOT / 'build')
    run(['node', str(ROOT / 'tools' / 'test' / 'mock_run.mjs'), str(build_dir / 'out' / 'ECR_BP' / 'scripts'), str(build_dir / 'mock')])


def typecheck():
    npm = Path(os.environ.get('SPP_NPM') or REF / 'npm')
    nm = npm / 'node_modules' / '@minecraft'
    cfg = {'compilerOptions': {
        'allowJs': True, 'checkJs': True, 'noEmit': True, 'target': 'ES2022', 'module': 'ES2022', 'moduleResolution': 'node',
        'strict': False, 'skipLibCheck': True, 'lib': ['ES2022', 'DOM'], 'baseUrl': '.',
        'paths': {'@minecraft/server': [(nm / 'server' / 'index.d.ts').as_posix()],
                  '@minecraft/server-ui': [(nm / 'server-ui' / 'index.d.ts').as_posix()],
                  '@minecraft/common': [(nm / 'common' / 'index.d.ts').as_posix()]}},
        'include': [(ROOT / 'tools' / 'scripts' / '*.js').as_posix()]}
    out = Path(os.environ.get('SPP_BUILD') or ROOT / 'build') / 'tsconfig.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(cfg, indent=1))
    run(['npx', 'tsc', '-p', str(out)], cwd=npm, shell=os.name == 'nt')
    print('typecheck clean')


def package():
    sys.path.insert(0, str(GEN))
    import build as b
    print(b.package())


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    steps = {'setup': [setup], 'build': [build], 'lint': [lint], 'typecheck': [typecheck], 'test': [test], 'package': [package],
             'all': [build, lint, typecheck, test, package]}
    for fn in steps[cmd]:
        fn()


if __name__ == '__main__':
    main()
