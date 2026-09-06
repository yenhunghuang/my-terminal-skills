"""Thin launchers: native CLI tools plus per-process gateway credentials."""
from __future__ import annotations
import argparse
import getpass
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import subprocess
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError

TOOLS = ('codex','claude','copilot','gemini','opencode','pi','omp','hermes')


def profile_home():
    # Installed at HOME/.local/share/terminal-agents/runtime.py.
    return Path(__file__).resolve().parents[3]


def settings(home):
    # Machine edits take effect on install, so routing matches installed configs.
    return json.loads((home/'.local/share/terminal-agents/machine.json').read_text())


def read_key(home, name, env):
    if not re.fullmatch(r'[A-Z][A-Z0-9_]*', name):
        raise ValueError('Invalid credential environment-variable name')
    if env.get(name):
        return env[name]
    if os.name == 'nt':
        raise ValueError(f'Set {name} in the Windows process environment; file-based secrets use WSL/POSIX only')
    p = home/'.config/terminal-agents/secrets.json'
    if not p.exists():
        raise ValueError(f'Missing {name}; use agent-run secret {name} or export it in your shell')
    if not stat.S_ISREG(p.stat().st_mode) or p.is_symlink() or p.stat().st_mode & 0o077:
        raise ValueError('secrets.json must be a private regular file (chmod 600)')
    value = json.loads(p.read_text()).get(name)
    if not isinstance(value,str) or not value:
        raise ValueError(f'Missing {name}; use agent-run secret {name}')
    return value


def store_key(home, name):
    if os.name == 'nt':
        raise ValueError('On native Windows, use a session environment variable or credential manager; see BOOTSTRAP.md')
    if not re.fullmatch(r'[A-Z][A-Z0-9_]*', name):
        raise ValueError('Use an environment variable name for the secret')
    value = getpass.getpass(f'{name} (hidden): ')
    if not value:
        raise ValueError('Empty credential was not saved')
    p = home/'.config/terminal-agents/secrets.json'
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.is_symlink() or (p.exists() and p.stat().st_mode & 0o077):
        raise ValueError('Existing secrets.json must be a private regular file')
    d = json.loads(p.read_text()) if p.exists() else {}
    d[name] = value
    fd, tmp = tempfile.mkstemp(dir=p.parent)
    try:
        with os.fdopen(fd,'w') as f:
            json.dump(d,f,indent=2);f.write('\n')
        os.chmod(tmp,0o600);os.replace(tmp,p)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    print('Credential saved locally. No shell startup files or repository files changed.')


def valid_url(url, loopback=False):
    u = urlsplit(url)
    local = u.hostname in ('localhost','127.0.0.1','::1')
    if not u.hostname or u.username or u.password or u.query or u.fragment:
        raise ValueError('Invalid gateway URL')
    if (loopback and not local) or (u.scheme != 'https' and not (u.scheme == 'http' and local)):
        raise ValueError('Remote gateways require HTTPS; CLIProxy must be loopback')
    return url.rstrip('/')


def executable_prefix(tool, binary, env):
    if Path(binary).suffix.lower() not in ('.cmd','.bat'):
        return [binary]
    packages = {
        'codex':['@openai/codex'], 'copilot':['@github/copilot'], 'gemini':['@google/gemini-cli'],
        'claude':['@anthropic-ai/claude-code'], 'pi':['@earendil-works/pi-coding-agent','@mariozechner/pi-coding-agent'],
        'opencode':['opencode-ai'], 'omp':['@oh-my-pi/pi-coding-agent']
    }
    node = shutil.which('node',path=env.get('PATH'))
    for package in packages.get(tool,[]):
        root = Path(binary).parent/'node_modules'/package
        manifest = root/'package.json'
        if node and manifest.is_file():
            bins=json.loads(manifest.read_text()).get('bin',{})
            entry=bins.get(tool) if isinstance(bins,dict) else bins
            if isinstance(entry,str):
                script=(root/entry).resolve()
                if script.is_file() and script.is_relative_to(root.resolve()):
                    return [node,str(script)]
    raise ValueError('Unsupported Windows command shim; install a native executable or use WSL')


def launch_spec(tool, args, home, config, env=None):
    env = dict(os.environ if env is None else env)
    proxy = tool in ('claude-proxy','copilot-proxy')
    native = tool.removesuffix('-proxy') if proxy else tool
    if native not in TOOLS:
        raise ValueError('Unsupported CLI')
    binary = shutil.which(native, path=env.get('PATH'))
    if not binary:
        raise ValueError(f'{native} is not installed/on PATH; see BOOTSTRAP.md')
    argv = executable_prefix(native,binary,env) + list(args)
    if proxy:
        cfg=config['cliproxy'];base=valid_url(cfg['base_url'],loopback=True)
        if urlsplit(base).path not in ('','/'):
            raise ValueError('CLIProxy base_url must be an origin without /v1')
        model=env.get('CLIPROXY_MODEL') or cfg['model']
        # Metadata must be supplied for the selected model, not guessed from another model.
        values=[]
        changed_model=model != cfg['model']
        for variable,key in [('CLIPROXY_CONTEXT_WINDOW_TOKENS','context_window_tokens'),('CLIPROXY_MAX_OUTPUT_TOKENS','max_output_tokens')]:
            value=env.get(variable) or (None if changed_model else cfg.get(key))
            if value is None or not str(value).isdigit() or int(value)<=0:
                raise ValueError(f'Set {variable} from metadata for the selected model')
            values.append(str(value))
        context,output=values
        key=read_key(home,cfg['key_env'],env)
        if native=='claude':
            for name in ('ANTHROPIC_API_KEY','CLAUDE_CODE_OAUTH_TOKEN'):
                env.pop(name,None)
            env.update(ANTHROPIC_BASE_URL=base,ANTHROPIC_AUTH_TOKEN=key,ANTHROPIC_MODEL=model,
                ANTHROPIC_DEFAULT_OPUS_MODEL=model,ANTHROPIC_DEFAULT_SONNET_MODEL=model,
                ANTHROPIC_DEFAULT_HAIKU_MODEL=env.get('CLIPROXY_FAST_MODEL',model),
                ANTHROPIC_SMALL_FAST_MODEL=env.get('CLIPROXY_FAST_MODEL',model),
                CLAUDE_CODE_SUBAGENT_MODEL=env.get('CLIPROXY_SUBAGENT_MODEL',model),
                CLAUDE_CODE_MAX_CONTEXT_TOKENS=context,CLAUDE_CODE_MAX_OUTPUT_TOKENS=output)
        else:
            for name in ('COPILOT_PROVIDER_BEARER_TOKEN','COPILOT_PROVIDER_MODEL_ID','COPILOT_PROVIDER_WIRE_MODEL'):
                env.pop(name,None)
            env.update(COPILOT_PROVIDER_TYPE='openai',COPILOT_PROVIDER_BASE_URL=base+'/v1',
                COPILOT_PROVIDER_API_KEY=key,COPILOT_PROVIDER_WIRE_API='responses',COPILOT_MODEL=model,
                COPILOT_PROVIDER_MAX_PROMPT_TOKENS=context,COPILOT_PROVIDER_MAX_OUTPUT_TOKENS=output)
            argv.insert(len(argv)-len(args), '--secret-env-vars=COPILOT_PROVIDER_API_KEY')
        # Avoid passing a second copy of the secret under a generic variable.
        if cfg['key_env'] not in ('ANTHROPIC_AUTH_TOKEN','COPILOT_PROVIDER_API_KEY'):
            env.pop(cfg['key_env'],None)
    elif native in ('pi','omp','hermes','opencode') and config['custom_gateway'].get('enabled'):
        cfg=config['custom_gateway'];valid_url(cfg['base_url'])
        env[cfg['key_env']]=read_key(home,cfg['key_env'],env)
    # Native Codex/Claude/Copilot/Gemini keep native auth and provider selection.
    return argv,env


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        return None


def probe(home,config,route):
    cfg=config['cliproxy' if route=='cliproxy' else 'custom_gateway']
    if route=='custom' and not cfg.get('enabled'):
        raise ValueError('Custom gateway is disabled')
    base=valid_url(cfg['base_url'],loopback=route=='cliproxy')
    url=base+('/v1/models' if route=='cliproxy' else '/models')
    key=read_key(home,cfg['key_env'],os.environ)
    request=Request(url,headers={'Authorization':'Bearer '+key})
    with build_opener(NoRedirect).open(request,timeout=15) as response:
        data=json.loads(response.read(4*1024*1024))
    ids={item.get('id') for item in data.get('data',[]) if isinstance(item,dict)}
    wanted=[cfg['model']] if route=='cliproxy' else [m['id'] for m in cfg['models']]
    missing=[m for m in wanted if m not in ids]
    print(f'Model catalog reachable. Configured models present: {len(wanted)-len(missing)}/{len(wanted)}')
    for model in missing:
        print('Missing configured model: '+model)
    print('Catalog check only; streaming, tools, subagent routing and token limits require separate verification.')
    return not missing


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tool',choices=TOOLS+('claude-proxy','copilot-proxy','secret','probe'))
    parser.add_argument('args',nargs=argparse.REMAINDER)
    ns=parser.parse_args();home=profile_home();args=ns.args
    if args[:1]==['--']:args=args[1:]
    if ns.tool=='secret':
        if len(args)!=1:raise ValueError('Usage: agent-run secret ENV_VARIABLE_NAME')
        store_key(home,args[0]);return
    config=settings(home)
    if ns.tool=='probe':
        if len(args)!=1 or args[0] not in ('cliproxy','custom'):
            raise ValueError('Usage: agent-run probe cliproxy|custom')
        if not probe(home,config,args[0]):raise SystemExit(1)
        return
    argv,env=launch_spec(ns.tool,args,home,config)
    if os.name == 'nt':
        raise SystemExit(subprocess.run(argv,env=env,shell=False).returncode)
    os.execve(argv[0],argv,env)


if __name__=='__main__':
    try:
        main()
    except (ValueError,OSError,KeyError,TypeError,HTTPError,URLError) as exc:
        # Provider error bodies, URLs and credential values are deliberately omitted.
        detail=str(exc) if isinstance(exc,ValueError) and not isinstance(exc,json.JSONDecodeError) else type(exc).__name__
        print('agent-run: '+detail,file=sys.stderr)
        raise SystemExit(1)
