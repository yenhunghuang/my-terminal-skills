import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]

def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts/profile'/f'{name}.py')
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

M=module('manage');R=module('runtime')

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='terminal profile ')
        self.home=Path(self.temp.name).resolve()
        self.config=json.loads((ROOT/'agent-profile/machine.example.json').read_text())
    def tearDown(self):self.temp.cleanup()
    def put(self,path,text):
        p=self.home/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);return p
    def apply(self,tools=M.TOOLS):
        ops=M.build_plan(self.home,self.config,tools)
        with contextlib.redirect_stdout(io.StringIO()):M.apply_plan(ops,self.home,list(tools))
        return ops
    def manifest(self):
        return next((self.home/'.local/state/terminal-agents').glob('*/manifest.json'))
    def enable_gateway(self):
        self.config['custom_gateway'].update(enabled=True,base_url='https://gateway.invalid/v1')
    def test_clean_install_all_tools_is_idempotent(self):
        self.apply()
        self.assertEqual(M.build_plan(self.home,self.config,M.TOOLS),[])
        for tool in M.TOOLS:
            self.assertIn('GPT-5.6 Luna/Sol',(self.home/M.ENTRIES[tool]).read_text())
            self.assertIsInstance(M.decode((self.home/M.SETTINGS[tool]).read_text(),Path(M.SETTINGS[tool]).suffix),dict)
        if os.name != 'nt':
            self.assertEqual((self.home/'.local/bin/agent-run').stat().st_mode&0o777,0o700)
        else:
            self.assertTrue((self.home/'.local/bin/agent-run.cmd').is_file())
        self.assertTrue((self.home/'.pi/agent/skills/pdf').is_dir())
    def test_existing_settings_auth_and_instructions_preserved(self):
        original={'permissions':{'allow':['Read']},'env':{'TEST_LOCAL_SECRET':'do-not-replace'},'effortLevel':'low'}
        self.put('.pi/agent/settings.json',json.dumps(original))
        self.put('.pi/agent/AGENTS.md','Use the company build server.\n')
        self.put('.codex/config.toml','# preserve this comment\nmodel="old"\n[model_providers.company]\nbase_url="https://company.invalid/v1"\n')
        self.put('.hermes/config.yaml','providers:\n  company:\n    key_env: ORIGINAL_KEY\nmemory:\n  memory_enabled: false\n')
        self.put('.hermes/SOUL.md','You are my custom assistant.\n')
        self.apply()
        data=json.loads((self.home/'.pi/agent/settings.json').read_text())
        self.assertEqual(data['permissions'],original['permissions']);self.assertEqual(data['env'],original['env'])
        self.assertIn('Use the company build server.',(self.home/'.pi/agent/AGENTS.md').read_text())
        self.assertIn('# preserve this comment',(self.home/'.codex/config.toml').read_text())
        self.assertIn('ORIGINAL_KEY',(self.home/'.hermes/config.yaml').read_text())
        self.assertIn('my custom assistant',(self.home/'.hermes/SOUL.md').read_text())
        self.assertEqual(M.build_plan(self.home,self.config,M.TOOLS),[])
    def test_gateway_adapters_and_environment_references(self):
        self.enable_gateway();self.apply()
        p=json.loads((self.home/'.pi/agent/models.json').read_text())['providers']['terminal-gateway']
        self.assertEqual(p['apiKey'],'$TERMINAL_AGENTS_GATEWAY_KEY')
        omp=M.decode((self.home/'.omp/agent/models.yml').read_text(),'.yml')['providers']['terminal-gateway']
        self.assertEqual(omp['apiKey'],'TERMINAL_AGENTS_GATEWAY_KEY')
        dsh=M.decode((self.home/'.dsh/settings.yaml').read_text(),'.yaml')
        self.assertEqual(dsh['llm-pi-ai']['providers']['terminal-gateway']['apiKeyEnv'],'TERMINAL_AGENTS_GATEWAY_KEY')
        self.assertEqual(dsh['agent-default-model']['model'],self.config['custom_gateway']['default_model'])
        hermes=M.decode((self.home/'.hermes/config.yaml').read_text(),'.yaml')
        self.assertEqual(hermes['model']['provider'],'custom:terminal-gateway')
        self.assertEqual(hermes['providers']['terminal-gateway']['key_env'],'TERMINAL_AGENTS_GATEWAY_KEY')
        self.assertEqual(M.build_plan(self.home,self.config,M.TOOLS),[])
    def test_template_defaults_preserve_existing_model_selection(self):
        originals = {
            'codex': {'model': 'gpt-5.6-sol', 'model_reasoning_effort': 'high'},
            'pi': {'defaultProvider': 'my-provider', 'defaultModel': 'my-model', 'defaultThinkingLevel': 'high'},
            'omp': {'modelRoles': {'default': 'my-provider/my-model', 'advisor': 'my-provider/advisor'}},
            'hermes': {'delegation': {'model': 'my-child', 'provider': 'my-provider'}, 'agent': {'reasoning_effort': 'high'}},
        }
        for tool, original in originals.items():
            suffix = Path(M.SETTINGS[tool]).suffix
            self.put(M.SETTINGS[tool], M.encode(original, suffix))
        self.apply()
        for tool, original in originals.items():
            actual = M.decode((self.home/M.SETTINGS[tool]).read_text(encoding='utf-8'), Path(M.SETTINGS[tool]).suffix)
            for key, value in original.items():
                if isinstance(value, dict):
                    for child_key, child_value in value.items():
                        self.assertEqual(actual[key][child_key], child_value)
                else:
                    self.assertEqual(actual[key], value)
        codex = M.decode((self.home/M.SETTINGS['codex']).read_text(encoding='utf-8'), '.toml')
        self.assertEqual(codex['personality'], 'pragmatic')

    def test_explicit_gateway_and_overrides_replace_existing_defaults(self):
        self.put('.omp/agent/config.yml', 'modelRoles:\n  default: old-provider/old-model\n  advisor: old-provider/advisor\n')
        self.put('.codex/config.toml', 'model = "old-model"\n')
        self.enable_gateway()
        self.config['overrides']['codex'] = {'model': 'gpt-5.6-sol'}
        self.apply(('codex', 'omp'))
        omp = M.decode((self.home/M.SETTINGS['omp']).read_text(encoding='utf-8'), '.yml')
        self.assertEqual(omp['modelRoles']['default'], 'terminal-gateway/'+self.config['custom_gateway']['default_model'])
        self.assertEqual(omp['modelRoles']['advisor'], 'old-provider/advisor')
        codex = M.decode((self.home/M.SETTINGS['codex']).read_text(encoding='utf-8'), '.toml')
        self.assertEqual(codex['model'], 'gpt-5.6-sol')
    def test_invalid_config_fails_before_mutation(self):
        self.put('.pi/agent/settings.json','invalid json')
        with self.assertRaises(ValueError):M.build_plan(self.home,self.config,M.TOOLS)
        self.assertFalse((self.home/'.codex/AGENTS.md').exists())
    def test_subset_does_not_install_other_clients(self):
        self.apply(('codex',))
        self.assertFalse((self.home/'.pi').exists())
        self.assertFalse((self.home/'.dsh').exists())
    @unittest.skipIf(os.name == "nt", "POSIX permissions/symlinks; Windows installs skill copies and uses environment secrets")
    def test_restore_preserves_previous_symlink_and_directory(self):
        target=self.put('private-original.md','Original personal instructions\n')
        p=self.home/'.pi/agent/AGENTS.md';p.parent.mkdir(parents=True);p.symlink_to(target)
        self.put('.pi/agent/skills/pdf/custom.txt','Keep my original resource')
        before=M.fingerprint(self.home/'.pi/agent/skills/pdf')
        self.apply(('pi',))
        self.assertEqual(target.read_text(),'Original personal instructions\n')
        with contextlib.redirect_stdout(io.StringIO()):M.restore(self.manifest(),self.home)
        self.assertTrue(p.is_symlink());self.assertEqual(p.resolve(),target)
        self.assertEqual(M.fingerprint(self.home/'.pi/agent/skills/pdf'),before)
    def test_restore_refuses_post_install_edits(self):
        self.apply(('codex',))
        self.put('.codex/AGENTS.md','New user work')
        with self.assertRaisesRegex(ValueError,'Changed since install'):M.restore(self.manifest(),self.home)
        self.assertEqual((self.home/'.codex/AGENTS.md').read_text(),'New user work')
    @unittest.skipIf(os.name == "nt", "POSIX permissions/symlinks; Windows installs skill copies and uses environment secrets")
    def test_parent_symlink_refused(self):
        (self.home/'elsewhere').mkdir();(self.home/'.pi').symlink_to(self.home/'elsewhere')
        with self.assertRaisesRegex(ValueError,'Parent directory'):M.build_plan(self.home,self.config,('pi',))
    @unittest.skipUnless(os.name == 'nt', 'Windows junctions')
    def test_parent_junction_refused(self):
        target = self.home/'elsewhere'
        target.mkdir()
        junction = self.home/'.codex'
        subprocess.run(['cmd', '/d', '/c', 'mklink', '/J', str(junction), str(target)], check=True, capture_output=True)
        try:
            with self.assertRaisesRegex(ValueError, 'Parent directory'):
                M.build_plan(self.home, self.config, ('codex',))
            self.assertEqual(list(target.iterdir()), [])
        finally:
            junction.rmdir()

    def test_updates_restore_in_reverse_order(self):
        original = 'model = "original-model"\n'
        target = self.put('.codex/config.toml', original)
        self.apply(('codex',))
        first = self.manifest()
        self.config['overrides']['codex'] = {'model': 'gpt-5.6-sol'}
        self.apply(('codex',))
        second = next(path for path in first.parent.parent.glob('*/manifest.json') if path != first)
        with self.assertRaisesRegex(ValueError, 'Changed since install'):
            M.restore(first, self.home)
        with contextlib.redirect_stdout(io.StringIO()):
            M.restore(second, self.home)
            M.restore(first, self.home)
        self.assertEqual(target.read_text(), original)
        self.assertFalse((self.home/'.codex/AGENTS.md').exists())
    def test_transaction_rolls_back_after_write_failure(self):
        p=self.put('.codex/config.toml','model = "before"\n')
        ops=M.build_plan(self.home,self.config,('codex',));real=M.write_op;counter=0
        def broken(op):
            nonlocal counter
            counter+=1
            if counter==4:raise OSError('simulated disk failure')
            real(op)
        with patch.object(M,'write_op',broken), self.assertRaises(OSError):M.apply_plan(ops,self.home,['codex'])
        self.assertEqual(p.read_text(),'model = "before"\n')
        for op in ops:self.assertEqual(M.fingerprint(op['path']),op['before'])
    def test_manifest_write_failure_rolls_back_install(self):
        self.put('.codex/config.toml', 'model = "before"\n')
        ops = M.build_plan(self.home, self.config, ('codex',))
        real = Path.write_text

        def fail_manifest(path, *args, **kwargs):
            if path.name == 'manifest.json':
                real(path, '{', encoding='utf-8')
                raise OSError('simulated manifest write failure')
            return real(path, *args, **kwargs)

        with patch.object(Path, 'write_text', fail_manifest), self.assertRaises(OSError):
            M.apply_plan(ops, self.home, ['codex'])
        for op in ops:
            self.assertEqual(M.fingerprint(op['path']), op['before'])
        self.assertEqual(list((self.home/'.local/state/terminal-agents').glob('*/manifest.json')), [])

    def test_restore_validates_all_backups_before_mutation(self):
        self.put('.codex/AGENTS.md', 'Original instructions\n')
        self.put('.codex/config.toml', 'model = "before"\n')
        self.apply(('codex',))
        manifest_path = self.manifest()
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        row = next(row for row in manifest['files'] if row['before'].startswith('file:'))
        saved = manifest_path.parent/row['saved']
        original = saved.read_bytes()
        for corrupt in (False, True):
            with self.subTest(corrupt=corrupt):
                if corrupt:
                    saved.write_bytes(b'corrupted backup')
                else:
                    saved.unlink()
                with self.assertRaisesRegex(ValueError, 'backup'):
                    M.restore(manifest_path, self.home)
                for entry in manifest['files']:
                    self.assertEqual(M.fingerprint(Path(entry['path'])), entry['after'])
                saved.write_bytes(original)

    def test_restore_rejects_unsafe_backup_paths(self):
        self.put('.codex/config.toml', 'model = "before"\n')
        self.apply(('codex',))
        manifest_path = self.manifest()
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        row = next(row for row in manifest['files'] if row['before'].startswith('file:'))
        outside = self.put('outside-backup', 'model = "before"\n')
        for saved in ('../outside-backup', str(outside)):
            with self.subTest(saved=saved):
                row['saved'] = saved
                manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
                with self.assertRaises(ValueError):
                    M.restore(manifest_path, self.home)
                for entry in manifest['files']:
                    self.assertEqual(M.fingerprint(Path(entry['path'])), entry['after'])

    def test_target_paths_cannot_escape_home(self):
        for path in (self.home, self.home/'..'/'outside', Path('relative-target')):
            with self.subTest(path=path), self.assertRaises(ValueError):
                M.checked_parent(path, self.home)

    def test_reversed_instruction_markers_fail_before_mutation(self):
        original = M.END+'\nKeep this policy\n'+M.BEGIN+'\n'
        path = self.put('.codex/AGENTS.md', original)
        with self.assertRaisesRegex(ValueError, 'Malformed'):
            M.build_plan(self.home, self.config, ('codex',))
        self.assertEqual(path.read_text(), original)
        self.assertFalse((self.home/'.local').exists())

    def test_utf8_files_work_without_utf8_locale(self):
        config_path = self.put('machine.json', json.dumps(self.config))
        original = '使用繁體中文；保留既有設定。\n'
        entry = self.home/'.codex/AGENTS.md'
        entry.parent.mkdir(parents=True)
        entry.write_text(original, encoding='utf-8')
        self.config['desktop_commands'] = {'hermes': ['C:/應用程式/Hermes.exe']}
        config_path.write_text(json.dumps(self.config, ensure_ascii=False), encoding='utf-8')
        script = '''
import contextlib, io, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import manage, runtime
home = Path(sys.argv[2])
machine = manage.load_machine(home/'machine.json')
with contextlib.redirect_stdout(io.StringIO()):
    manage.apply_plan(manage.build_plan(home, machine, ('codex',)), home, ['codex'])
assert runtime.settings(home) == machine
assert manage.build_plan(home, machine, ('codex',)) == []
'''
        env = dict(os.environ, LC_ALL='C', PYTHONCOERCECLOCALE='0', PYTHONIOENCODING='utf-8')
        result = subprocess.run(
            [sys.executable, '-X', 'utf8=0', '-c', script, str(ROOT/'scripts/profile'), str(self.home)],
            env=env, capture_output=True, text=True, encoding='utf-8',
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(original.strip(), entry.read_text(encoding='utf-8'))

    def test_utf8_bom_is_supported_in_native_configuration(self):
        path = self.put('machine.json', '')
        path.write_text(json.dumps(self.config), encoding='utf-8-sig')
        self.assertEqual(M.load_machine(path), self.config)
        for tool, content in (('pi', '{"theme":"中文"}'), ('codex', 'model = "existing"')):
            dest = self.home/M.SETTINGS[tool]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding='utf-8-sig')
        self.apply(('pi', 'codex'))
    @unittest.skipIf(os.name == 'nt', 'POSIX private file semantics')
    def test_secret_permissions_and_native_auth_isolation(self):
        self.enable_gateway()
        p=self.put('.config/terminal-agents/secrets.json',json.dumps({'TERMINAL_AGENTS_GATEWAY_KEY':'fixture-key'}));p.chmod(0o600)
        env={'PATH':'/bin','NATIVE_LOGIN':'keep'}
        with patch.object(R.shutil,'which',return_value='/bin/true'):
            argv,out=R.launch_spec('pi',['hello world'],self.home,self.config,env)
            self.assertEqual(out['TERMINAL_AGENTS_GATEWAY_KEY'],'fixture-key')
            self.assertNotIn('fixture-key',str(argv));self.assertNotIn('TERMINAL_AGENTS_GATEWAY_KEY',env)
            _,native=R.launch_spec('codex-cli',[],self.home,self.config,env)
            self.assertEqual(native,env)
        p.chmod(0o644)
        with self.assertRaisesRegex(ValueError,'private'):R.read_key(self.home,'TERMINAL_AGENTS_GATEWAY_KEY',{})
    def test_desktop_and_cli_are_distinct(self):
        self.config['desktop_commands']={'codex':['/apps/codex-desktop','--native'],'hermes':['/apps/hermes-desktop']}
        with patch.object(R.shutil,'which',side_effect=lambda x,**kw:x):
            argv,_=R.launch_spec('codex',['literal ; $(text)'],self.home,self.config,{'PATH':'fixture'})
            self.assertEqual(argv,['/apps/codex-desktop','--native','literal ; $(text)'])
            argv,_=R.launch_spec('codex-cli',[],self.home,self.config,{'PATH':'fixture'})
            self.assertEqual(argv,['codex'])
            argv,_=R.launch_spec('hermes',[],self.home,self.config,{'PATH':'fixture'})
            self.assertEqual(argv,['/apps/hermes-desktop'])
    def test_only_selected_agents_are_shipped(self):
        self.assertEqual(set(M.TOOLS),{'codex','pi','omp','dsh','hermes'})
        self.assertEqual(set(M.TEMPLATES.values()),{p.name for p in (ROOT/'agent-profile/settings').iterdir()})
        self.assertEqual({p.name for p in (ROOT/'agent-profile/skills').iterdir()},{'pdf','ui-ux-pro-max','refactor-agent-instructions'})
    def test_desktop_command_validation(self):
        self.config['desktop_commands']={'dsh':'not an argument array'}
        p=self.put('machine.json',json.dumps(self.config))
        with self.assertRaisesRegex(ValueError,'desktop_commands'):M.load_machine(p)
        with patch.object(R.sys,'platform','linux'):
            with self.assertRaisesRegex(ValueError,'desktop_commands'):R.desktop_prefix('dsh',{}, {})
    def test_dsh_preserves_plugin_settings_and_maps_reasoning(self):
        self.put('.dsh/settings.yaml','# keep\nother-plugin:\n  enabled: true\n')
        self.enable_gateway()
        self.config['custom_gateway']['models'][0]['thinkingLevelMap']={'off':'none','high':'high','max':'ultra','low':None}
        self.apply(('dsh',))
        data=M.decode((self.home/'.dsh/settings.yaml').read_text(),'.yaml')
        self.assertTrue(data['other-plugin']['enabled'])
        model=data['llm-pi-ai']['providers']['terminal-gateway']['models'][0]
        self.assertEqual(model['reasoningEfforts'],{'off':'none','high':'high','max':'ultra'})
        self.assertIn('# keep',(self.home/'.dsh/settings.yaml').read_text())
    def test_remote_cleartext_and_embedded_url_credentials_rejected(self):
        for url in ['http://remote.invalid/v1','https://user:pass@remote.invalid/v1','https://remote.invalid/v1?key=secret']:
            with self.assertRaises(ValueError):M.check_url(url)
        with self.assertRaises(ValueError):M.check_url('https://remote.invalid',loopback=True)
    def test_windows_npm_shim_uses_node_without_a_command_shell(self):
        binary=self.put('npm/pi.cmd','@echo off')
        root=self.home/'npm/node_modules/@earendil-works/pi-coding-agent'
        root.mkdir(parents=True)
        (root/'package.json').write_text(json.dumps({'bin':{'pi':'dist/cli.js'}}))
        (root/'dist').mkdir();(root/'dist/cli.js').write_text('// fixture')
        with patch.object(R.shutil,'which',return_value='node'):
            prefix=R.executable_prefix('pi',str(binary),{'PATH':'fixture'})
        self.assertEqual(prefix,['node',str((root/'dist/cli.js').resolve())])

if __name__=='__main__':unittest.main()
