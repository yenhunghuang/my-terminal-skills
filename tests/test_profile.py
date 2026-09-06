import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
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
        self.put('.claude/settings.json',json.dumps(original))
        self.put('.claude/CLAUDE.md','Use the company build server.\n')
        self.put('.codex/config.toml','# preserve this comment\nmodel="old"\n[model_providers.company]\nbase_url="https://company.invalid/v1"\n')
        self.put('.hermes/config.yaml','providers:\n  company:\n    key_env: ORIGINAL_KEY\nmemory:\n  memory_enabled: false\n')
        self.put('.hermes/SOUL.md','You are my custom assistant.\n')
        self.apply()
        data=json.loads((self.home/'.claude/settings.json').read_text())
        self.assertEqual(data['permissions'],original['permissions']);self.assertEqual(data['env'],original['env'])
        self.assertIn('Use the company build server.',(self.home/'.claude/CLAUDE.md').read_text())
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
        op=json.loads((self.home/'.config/opencode/opencode.json').read_text())
        self.assertEqual(op['small_model'],op['model'])
        hermes=M.decode((self.home/'.hermes/config.yaml').read_text(),'.yaml')
        self.assertEqual(hermes['model']['provider'],'custom:terminal-gateway')
        self.assertEqual(hermes['providers']['terminal-gateway']['key_env'],'TERMINAL_AGENTS_GATEWAY_KEY')
        self.assertEqual(M.build_plan(self.home,self.config,M.TOOLS),[])
    def test_invalid_config_fails_before_mutation(self):
        self.put('.copilot/settings.json','invalid json')
        with self.assertRaises(ValueError):M.build_plan(self.home,self.config,M.TOOLS)
        self.assertFalse((self.home/'.codex/AGENTS.md').exists())
    def test_subset_does_not_install_other_clients(self):
        self.apply(('codex',))
        self.assertFalse((self.home/'.claude').exists())
        self.assertFalse((self.home/'.local/bin/claude-via-cliproxy').exists())
    @unittest.skipIf(os.name == "nt", "POSIX permissions/symlinks; Windows installs skill copies and uses environment secrets")
    def test_restore_preserves_previous_symlink_and_directory(self):
        target=self.put('private-original.md','Original personal instructions\n')
        p=self.home/'.claude/CLAUDE.md';p.parent.mkdir(parents=True);p.symlink_to(target)
        self.put('.claude/skills/pdf/custom.txt','Keep my original resource')
        before=M.fingerprint(self.home/'.claude/skills/pdf')
        self.apply(('claude',))
        self.assertEqual(target.read_text(),'Original personal instructions\n')
        with contextlib.redirect_stdout(io.StringIO()):M.restore(self.manifest(),self.home)
        self.assertTrue(p.is_symlink());self.assertEqual(p.resolve(),target)
        self.assertEqual(M.fingerprint(self.home/'.claude/skills/pdf'),before)
    def test_restore_refuses_post_install_edits(self):
        self.apply(('codex',))
        self.put('.codex/AGENTS.md','New user work')
        with self.assertRaisesRegex(ValueError,'Changed since install'):M.restore(self.manifest(),self.home)
        self.assertEqual((self.home/'.codex/AGENTS.md').read_text(),'New user work')
    @unittest.skipIf(os.name == "nt", "POSIX permissions/symlinks; Windows installs skill copies and uses environment secrets")
    def test_parent_symlink_refused(self):
        (self.home/'elsewhere').mkdir();(self.home/'.claude').symlink_to(self.home/'elsewhere')
        with self.assertRaisesRegex(ValueError,'Parent directory'):M.build_plan(self.home,self.config,('claude',))
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
    @unittest.skipIf(os.name == "nt", "POSIX permissions/symlinks; Windows installs skill copies and uses environment secrets")
    def test_secret_permissions_and_native_auth_isolation(self):
        self.config['cliproxy'].update(context_window_tokens=100000,max_output_tokens=10000)
        p=self.put('.config/terminal-agents/secrets.json',json.dumps({'TERMINAL_AGENTS_CLIPROXY_KEY':'fixture-key'}));p.chmod(0o600)
        env={'PATH':'/bin','ANTHROPIC_API_KEY':'native-auth'}
        with patch.object(R.shutil,'which',return_value='/bin/true'):
            argv,out=R.launch_spec('claude-proxy',['hello world'],self.home,self.config,env)
            self.assertNotIn('ANTHROPIC_API_KEY',out);self.assertEqual(out['ANTHROPIC_AUTH_TOKEN'],'fixture-key')
            self.assertEqual(out['CLAUDE_CODE_SUBAGENT_MODEL'],'gpt-5.6-sol')
            self.assertNotIn('fixture-key',str(argv));self.assertEqual(env['ANTHROPIC_API_KEY'],'native-auth')
            _,native=R.launch_spec('claude',[],self.home,self.config,env)
            self.assertEqual(native,env)
        p.chmod(0o644)
        with self.assertRaisesRegex(ValueError,'private'):R.read_key(self.home,'TERMINAL_AGENTS_CLIPROXY_KEY',{})
    def test_changed_model_requires_its_own_metadata(self):
        self.config['cliproxy'].update(context_window_tokens=100000,max_output_tokens=10000)
        with patch.object(R.shutil,'which',return_value='/bin/true'):
            with self.assertRaisesRegex(ValueError,'metadata'):
                R.launch_spec('claude-proxy',[],self.home,self.config,{'PATH':'/bin','CLIPROXY_MODEL':'gpt-6-astra'})
    def test_copilot_keeps_args_and_removes_pinned_child_routing(self):
        self.config['cliproxy'].update(context_window_tokens=100000,max_output_tokens=10000)
        env={'PATH':'/bin','TERMINAL_AGENTS_CLIPROXY_KEY':'fixture-key','COPILOT_PROVIDER_MODEL_ID':'old','COPILOT_PROVIDER_BEARER_TOKEN':'old-native'}
        with patch.object(R.shutil,'which',return_value='/bin/true'):
            argv,out=R.launch_spec('copilot-proxy',['-p','a ; $(b)'],self.home,self.config,env)
        self.assertEqual(argv[-2:],['-p','a ; $(b)']);self.assertNotIn('COPILOT_PROVIDER_MODEL_ID',out)
        self.assertNotIn('COPILOT_PROVIDER_BEARER_TOKEN',out);self.assertNotIn('TERMINAL_AGENTS_CLIPROXY_KEY',out)
        self.assertIn('--secret-env-vars=COPILOT_PROVIDER_API_KEY',argv)
    def test_remote_cleartext_and_embedded_url_credentials_rejected(self):
        for url in ['http://remote.invalid/v1','https://user:pass@remote.invalid/v1','https://remote.invalid/v1?key=secret']:
            with self.assertRaises(ValueError):M.check_url(url)
        with self.assertRaises(ValueError):M.check_url('https://remote.invalid',loopback=True)
    def test_superclaude_router_is_replaced_without_imports(self):
        old='# SuperClaude Entry Point\n\n'+''.join('@'+n+'.md\n' for n in ['COMMANDS','FLAGS','PRINCIPLES','RULES','MCP','PERSONAS','ORCHESTRATOR','MODES'])
        value=M.instruction_text(old,'New policy')
        self.assertNotIn('@PERSONAS',value);self.assertIn('New policy',value)

    def test_windows_npm_shim_uses_node_without_a_command_shell(self):
        binary=self.put('npm/pi.cmd','@echo off')
        root=self.home/'npm/node_modules/@earendil-works/pi-coding-agent'
        root.mkdir(parents=True)
        (root/'package.json').write_text(json.dumps({'bin':{'pi':'dist/cli.js'}}))
        (root/'dist').mkdir();(root/'dist/cli.js').write_text('// fixture')
        with patch.object(R.shutil,'which',return_value='node'):
            prefix=R.executable_prefix('pi',str(binary),{'PATH':'fixture'})
        self.assertEqual(prefix,['node',str((root/'dist/cli.js').resolve())])
    def test_copilot_npm_shim_options_follow_script_entry(self):
        self.config['cliproxy'].update(context_window_tokens=100000,max_output_tokens=10000)
        with patch.object(R.shutil,'which',return_value='copilot.cmd'), patch.object(R,'executable_prefix',return_value=['node','cli.js']):
            argv,_=R.launch_spec('copilot-proxy',['-p','hello'],self.home,self.config,{'PATH':'fixture','TERMINAL_AGENTS_CLIPROXY_KEY':'fixture-key'})
        self.assertEqual(argv,['node','cli.js','--secret-env-vars=COPILOT_PROVIDER_API_KEY','-p','hello'])

if __name__=='__main__':unittest.main()
