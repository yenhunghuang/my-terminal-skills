"""Install portable agent configuration. No credentials are exported from a source machine."""
from __future__ import annotations
import argparse
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import sys
import subprocess
import tempfile
import time
import uuid
from urllib.parse import urlsplit

import tomlkit
from ruamel.yaml import YAML

REPO = Path(__file__).resolve().parents[2]
PROFILE = REPO / 'agent-profile'
TOOLS = ('codex', 'claude', 'copilot', 'gemini', 'opencode', 'pi', 'omp', 'hermes')
ENTRIES = dict(zip(TOOLS, ('.codex/AGENTS.md', '.claude/CLAUDE.md', '.copilot/copilot-instructions.md', '.gemini/GEMINI.md', '.config/opencode/AGENTS.md', '.pi/agent/AGENTS.md', '.omp/agent/AGENTS.md', '.hermes/SOUL.md')))
SETTINGS = dict(zip(TOOLS, ('.codex/config.toml', '.claude/settings.json', '.copilot/settings.json', '.gemini/settings.json', '.config/opencode/opencode.json', '.pi/agent/settings.json', '.omp/agent/config.yml', '.hermes/config.yaml')))
TEMPLATES = dict(zip(TOOLS, ('codex.toml','claude.json','copilot.json','gemini.json','opencode.json','pi.json','omp.yaml','hermes.yaml')))
BEGIN, END = '<!-- terminal-agent-profile:start -->', '<!-- terminal-agent-profile:end -->'


def merge(dst, patch):
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            merge(dst[k], v)
        else:
            dst[k] = copy.deepcopy(v)
    return dst


def decode(text, suffix):
    if not text.strip():
        return {}
    if suffix == '.toml':
        data = tomlkit.parse(text)
    elif suffix in ('.yaml', '.yml'):
        data = YAML().load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError('Configuration must be an object/mapping')
    return data


def encode(data, suffix):
    if suffix == '.toml':
        return tomlkit.dumps(data)
    if suffix in ('.yaml', '.yml'):
        output = io.StringIO()
        YAML().dump(data, output)
        return output.getvalue()
    return json.dumps(data, ensure_ascii=False, indent=2) + '\n'


def load_machine(path):
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError('machine.json must be an object')
    gateway = data.get('custom_gateway', {})
    proxy = data.get('cliproxy', {})
    for cfg in (gateway, proxy):
        if not re.fullmatch(r'[A-Z][A-Z0-9_]*', cfg.get('key_env', '')):
            raise ValueError('key_env must name an environment variable, not contain a key')
    if gateway.get('enabled'):
        check_url(gateway.get('base_url', ''))
        models = gateway.get('models', [])
        if not models or not all(isinstance(m, dict) and isinstance(m.get('id'), str) and m['id'].strip() for m in models):
            raise ValueError('Supply exact gateway model IDs')
        ids = [m['id'] for m in models]
        if len(ids) != len(set(ids)) or gateway.get('default_model') not in ids:
            raise ValueError('Model IDs must be unique; default_model must occur in models')
        # Only metadata fields, not per-model credentials/headers or commands.
        allowed = {'id', 'name', 'reasoning', 'input', 'contextWindow', 'maxTokens', 'thinkingLevelMap'}
        if any(set(m) - allowed for m in models):
            raise ValueError('Unsupported model metadata field')
        for model in models:
            for key in ('contextWindow', 'maxTokens'):
                if key in model and (type(model[key]) is not int or model[key] <= 0):
                    raise ValueError('Model token limits must be positive integers')
    check_url(proxy.get('base_url', ''), loopback=True)
    if not proxy.get('model'):
        raise ValueError('cliproxy.model is required')
    for key in ('context_window_tokens','max_output_tokens'):
        v = proxy.get(key)
        if v is not None and (type(v) is not int or v <= 0):
            raise ValueError('Proxy token limits must be positive integers or null')
    overrides = data.get('overrides', {})
    if not isinstance(overrides, dict) or set(overrides) - set(TOOLS):
        raise ValueError('overrides must be keyed by a supported CLI name')
    return data


def check_url(url, loopback=False):
    u = urlsplit(url)
    local = u.hostname in ('localhost','127.0.0.1','::1')
    if u.username or u.password or u.query or u.fragment or not u.hostname:
        raise ValueError('Gateway URL must have a hostname and no credentials/query/fragment')
    if u.scheme != 'https' and not (u.scheme == 'http' and local):
        raise ValueError('Use HTTPS for remote gateways or HTTP on loopback')
    if loopback and not local:
        raise ValueError('CLIProxy wrappers require a loopback origin; use an SSH tunnel for a remote gateway')
    if 'example' in u.hostname or '<' in url:
        raise ValueError('Replace the example gateway URL')


def instruction_text(old, new):
    if old.count(BEGIN) != old.count(END) or old.count(BEGIN) > 1:
        raise ValueError('Malformed managed instruction block')
    if BEGIN in old:
        return old[:old.index(BEGIN)] + BEGIN + '\n' + new.rstrip() + '\n' + END + old[old.index(END) + len(END):]
    # Migrate only the known stock SuperClaude router, preserving other custom text.
    stock = {'# SuperClaude Entry Point', '@COMMANDS.md','@FLAGS.md','@PRINCIPLES.md','@RULES.md','@MCP.md','@PERSONAS.md','@ORCHESTRATOR.md','@MODES.md'}
    if old.strip() == new.strip() or set(old.splitlines()) - {''} == stock:
        old = ''
    prefix = old.rstrip() + '\n\n' if old.strip() else ''
    return prefix + BEGIN + '\n' + new.rstrip() + '\n' + END + '\n'


def fingerprint(path):
    if path.is_symlink():
        return 'link:' + os.readlink(path)
    if not path.exists():
        return 'absent'
    if path.is_dir():
        parts = [(str(p.relative_to(path)), fingerprint(p)) for p in sorted(path.rglob('*'))]
        return 'dir:' + hashlib.sha256(json.dumps(parts).encode()).hexdigest()
    return 'file:' + hashlib.sha256(path.read_bytes()).hexdigest()


def checked_parent(path, home):
    if not path.is_relative_to(home):
        raise ValueError('Target must be inside the selected home')
    for parent in path.parents:
        if parent == home:
            break
        if parent.is_symlink():
            raise ValueError(f'Parent directory is a symlink; configure this target separately: {parent}')


def operation(path, data=None, link=None, mode=0o600):
    return {'path': path, 'data': data, 'link': link, 'mode': mode, 'before': fingerprint(path)}


def build_plan(home, machine, selected):
    ops = []
    share = home / '.local/share/terminal-agents'
    common = (PROFILE/'AGENTS.md').read_text()
    for source in (PROFILE/'skills').rglob('*'):
        if source.is_file():
            ops.append(operation(share/'skills'/source.relative_to(PROFILE/'skills'), source.read_bytes(), mode=source.stat().st_mode & 0o777))
    ops.append(operation(share/'runtime.py', (REPO/'scripts/profile/runtime.py').read_bytes()))
    ops.append(operation(share/'machine.json', (json.dumps(machine, indent=2)+'\n').encode()))
    for tool in selected:
        path = home/ENTRIES[tool]
        new = (PROFILE/'hermes/SOUL.md').read_text() if tool == 'hermes' else common
        old = path.read_text() if path.exists() else ''
        # Keep identity outside the managed policy block, including on repeated installs.
        if tool == 'hermes':
            if not old.strip():
                old = new.split('# Personal working preferences', 1)[0].rstrip() + '\n'
            elif BEGIN not in old and common.strip() in old:
                old = old.replace(common.strip(), '').rstrip() + '\n'
            new = common
        ops.append(operation(path, instruction_text(old, new).encode()))
        dest = home/SETTINGS[tool]
        source = PROFILE/'settings'/TEMPLATES[tool]
        patch = decode(source.read_text(), source.suffix)
        if machine.get('custom_gateway', {}).get('enabled') and tool in ('pi','omp','opencode','hermes'):
            gateway_patch(tool, home, machine['custom_gateway'], patch, ops)
        merge(patch, machine.get('overrides', {}).get(tool, {}))
        current = decode(dest.read_text(), dest.suffix) if dest.exists() else {}
        merge(current, patch)
        if tool == 'claude':
            for k in ('components', 'framework'):
                # Remove only the known SuperClaude metadata.
                if k in current and 'core' in json.dumps(current[k]) and 'commands' in json.dumps(current[k]):
                    del current[k]
        ops.append(operation(dest, encode(current, dest.suffix).encode()))
        skills_root = {
            'codex':'.agents/skills', 'claude':'.claude/skills', 'copilot':'.copilot/skills',
            'gemini':'.gemini/skills', 'opencode':'.config/opencode/skills', 'pi':'.pi/agent/skills',
            'omp':'.omp/agent/skills', 'hermes':'.hermes/skills'
        }[tool]
        for skill in (PROFILE/'skills').iterdir():
            if os.name == 'nt':
                # Windows user accounts need no symlink privileges: install managed copies.
                for source in skill.rglob('*'):
                    if source.is_file():
                        ops.append(operation(home/skills_root/skill.name/source.relative_to(skill), source.read_bytes()))
            else:
                ops.append(operation(home/skills_root/skill.name, link=str(share/'skills'/skill.name)))
    if 'claude' in selected:
        for source in (PROFILE/'claude/commands/sc').glob('*.md'):
            ops.append(operation(home/'.claude/commands/sc'/source.name, source.read_bytes()))
    for name, arg in [('agent-run',''),('claude-via-cliproxy','claude-proxy'),('copilot-via-cliproxy','copilot-proxy')]:
        if name.startswith('claude') and 'claude' not in selected:
            continue
        if name.startswith('copilot') and 'copilot' not in selected:
            continue
        if os.name == 'nt':
            # The interpreter installed by uv is explicit; shell startup files are not edited.
            script = f'@echo off\r\n"{sys.executable}" "{share / "runtime.py"}" {arg} %*\r\n'
            ops.append(operation(home/'.local/bin'/(name+'.cmd'), script.encode(), mode=0o700))
        else:
            script = f'#!/bin/sh\nexec python3 {shlex.quote(str(share/"runtime.py"))} {arg} "$@"\n'
            ops.append(operation(home/'.local/bin'/name, script.encode(), mode=0o700))
    for op in ops:
        checked_parent(op['path'], home)
        if op['data'] is not None and op['path'].is_dir():
            raise ValueError(f'Expected file, found directory: {op["path"]}')
    # Target duplication indicates an installer bug, not a merge policy.
    assert len({op['path'] for op in ops}) == len(ops)
    return [op for op in ops if not (op['link'] is not None and op['before'] == 'link:'+op['link']) and not (op['data'] is not None and not op['path'].is_symlink() and op['path'].is_file() and op['path'].read_bytes() == op['data'] and (os.name == 'nt' or op['path'].stat().st_mode & 0o777 == op['mode']))]


def gateway_patch(tool, home, gateway, patch, ops):
    models = copy.deepcopy(gateway['models'])
    base, key, default = gateway['base_url'].rstrip('/'), gateway['key_env'], gateway['default_model']
    provider = {'baseUrl':base, 'api':'openai-completions', 'models':models, 'compat':gateway.get('compat',{})}
    if tool in ('pi','omp'):
        provider['apiKey'] = '$'+key if tool == 'pi' else key
        if tool == 'omp':
            provider['authHeader'] = True
        dest = home/('.pi/agent/models.json' if tool == 'pi' else '.omp/agent/models.yml')
        current = decode(dest.read_text(), dest.suffix) if dest.exists() else {}
        merge(current, {'providers':{'terminal-gateway':provider}})
        ops.append(operation(dest, encode(current,dest.suffix).encode()))
        if tool == 'pi':
            patch.update(defaultProvider='terminal-gateway', defaultModel=default)
        else:
            patch['modelRoles']['default'] = 'terminal-gateway/'+default
    elif tool == 'opencode':
        entries = {}
        for m in models:
            value = {'name':m.get('name',m['id'])}
            limits = {dest:m[src] for src,dest in [('contextWindow','context'),('maxTokens','output')] if src in m}
            if limits:
                value['limit'] = limits
            entries[m['id']] = value
        patch.update(model='terminal-gateway/'+default, small_model='terminal-gateway/'+default)
        patch['provider'] = {'terminal-gateway':{'npm':'@ai-sdk/openai-compatible','name':'Personal gateway','options':{'baseURL':base,'apiKey':'{env:'+key+'}'},'models':entries}}
    else:
        patch['model'] = {'provider':'custom:terminal-gateway','default':default}
        patch['providers'] = {'terminal-gateway':{'base_url':base,'key_env':key,'default_model':default,'api_mode':'chat_completions'}}


def remove(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def write_op(op):
    p = op['path']
    p.parent.mkdir(parents=True, exist_ok=True)
    if op['link'] is not None:
        remove(p)
        p.symlink_to(op['link'], target_is_directory=True)
    else:
        fd, name = tempfile.mkstemp(dir=p.parent)
        try:
            with os.fdopen(fd,'wb') as f:
                f.write(op['data'])
            os.chmod(name, op['mode'])
            os.replace(name,p)
        finally:
            if os.path.exists(name):
                os.unlink(name)


def restore_entry(row, backup):
    p = Path(row['path'])
    remove(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    if row['before'].startswith('link:'):
        p.symlink_to(row['before'][5:], target_is_directory=True)
    elif row['before'].startswith('dir:'):
        shutil.copytree(backup/row['saved'], p, symlinks=True)
    elif row['before'].startswith('file:'):
        shutil.copy2(backup/row['saved'], p)


def apply_plan(ops, home, selected):
    if not ops:
        print('Already up to date; no files changed.')
        return
    # Refuse concurrent modifications observed since the plan was built.
    for op in ops:
        if fingerprint(op['path']) != op['before']:
            raise ValueError('Target changed during planning; rerun install')
    state = home/'.local/state/terminal-agents'
    state.mkdir(parents=True,exist_ok=True); state.chmod(0o700)
    if os.name == 'nt':
        account = subprocess.check_output(['whoami'],text=True).strip()
        subprocess.run(['icacls',str(state),'/inheritance:r','/grant:r',account+':(OI)(CI)F'],check=True,stdout=subprocess.DEVNULL)
    backup = state/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8])
    backup.mkdir(mode=0o700)
    rows = []
    for i, op in enumerate(ops):
        p = op['path']; saved = str(i)
        if op['before'].startswith('file:'):
            shutil.copy2(p,backup/saved)
        elif op['before'].startswith('dir:'):
            shutil.copytree(p,backup/saved,symlinks=True)
        rows.append({'path':str(p),'before':op['before'],'saved':saved})
    touched = []
    try:
        for row, op in zip(rows,ops):
            touched.append(row)
            write_op(op)
            row['after'] = fingerprint(op['path'])
    except Exception:
        for row in reversed(touched):
            restore_entry(row,backup)
        raise
    manifest = {'home':str(home),'agents':selected,'files':rows}
    (backup/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Applied {len(rows)} changes. Restore manifest: {backup/"manifest.json"}')


def restore(manifest_path, home):
    manifest_path = manifest_path.resolve()
    expected = home/'.local/state/terminal-agents'
    if not manifest_path.is_relative_to(expected):
        raise ValueError('Restore manifest must belong to this home profile')
    manifest = json.loads(manifest_path.read_text())
    if manifest['home'] != str(home):
        raise ValueError('Manifest belongs to another home')
    for row in manifest['files']:
        checked_parent(Path(row['path']),home)
        if fingerprint(Path(row['path'])) != row['after']:
            raise ValueError(f'Changed since install; preserve/resolve it before restore: {row["path"]}')
    for row in reversed(manifest['files']):
        restore_entry(row,manifest_path.parent)
    print('Restored files from this installation; unrelated files were not removed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['init','install','doctor','restore'])
    parser.add_argument('--home',type=Path,default=Path.home(),help='Target account home (also useful for isolated tests)')
    parser.add_argument('--machine',type=Path,help='Machine JSON; default ~/.config/terminal-agents/machine.json')
    parser.add_argument('--agents',default=','.join(TOOLS),help='Comma-separated CLI names')
    parser.add_argument('--apply',action='store_true',help='Write files; install previews by default')
    parser.add_argument('--manifest',type=Path,help='Restore manifest printed by an install')
    args=parser.parse_args()
    home=args.home.expanduser().resolve()
    path=args.machine or home/'.config/terminal-agents/machine.json'
    selected=args.agents.split(',')
    if not selected or set(selected)-set(TOOLS) or len(set(selected))!=len(selected):
        raise ValueError('Invalid/duplicate CLI names')
    if args.command=='init':
        if path.exists():
            print('Machine settings already exist; kept unchanged.');return
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes((PROFILE/'machine.example.json').read_bytes());path.chmod(0o600)
        print(f'Created {path}; configure your gateway here, then run install.');return
    if args.command=='restore':
        if not args.manifest:
            raise ValueError('--manifest is required')
        restore(args.manifest,home);return
    if not path.exists():
        raise ValueError('Run init first or supply --machine')
    machine=load_machine(path)
    ops=build_plan(home,machine,selected)
    if args.command=='doctor':
        failed=False
        for tool in selected:
            binary=shutil.which(tool)
            print(f'{tool}: binary={"found" if binary else "MISSING"}; instruction={"present" if (home/ENTRIES[tool]).exists() else "MISSING"}')
            failed |= not bool(binary)
        print(f'Profile drift: {len(ops)} pending file changes')
        print('Authentication and live model/tool support are NOT inferred from file checks.')
        if not machine['custom_gateway'].get('enabled'):
            print('Custom gateway disabled: Pi/Hermes/OpenCode keep their native or existing model selection.')
        else:
            for model in machine['custom_gateway']['models']:
                if not {'contextWindow','maxTokens'} <= model.keys():
                    print(f'Metadata incomplete for {model["id"]}; the CLI may use its own token-budget defaults.')
        if any(machine['cliproxy'].get(k) is None for k in ('context_window_tokens','max_output_tokens')):
            print('Proxy wrappers require explicit token limits before inference.')
        if ops or failed:
            raise SystemExit(1)
    else:
        for op in ops:
            print(('LINK ' if op['link'] is not None else 'WRITE ')+str(op['path']))
        if args.apply:
            apply_plan(ops,home,selected)
        else:
            print(f'Preview only: {len(ops)} changes. Add --apply to install with backups.')


if __name__=='__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        # Do not dump parsed configuration content or secret values on errors.
        print(f'Profile error ({type(exc).__name__}): {exc}',file=sys.stderr)
        raise SystemExit(1)
