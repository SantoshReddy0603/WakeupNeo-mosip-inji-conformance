"""Filesystem contract fixture; no product or conformance results are synthesized."""
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

def test_installer_preserves_master_suites_and_is_idempotent(tmp_path):
    root=Path(__file__).resolve().parents[1]
    for component in ['certify','verify']:
        repo=tmp_path/component
        api=repo/'api-test'
        suites=api/'testNgXmlFiles'
        suites.mkdir(parents=True)
        (api/'pom.xml').write_text('<project/>')
        master=suites/('inji'+component+'MasterTestSuite.xml')
        master.write_text('<suite><listeners><listener class-name="io.mosip.testrig.apirig.report.EmailableReport"/></listeners>'
                          '<suite-files><suite-file path="existing-functional-suite.xml"/></suite-files></suite>')
        command=[sys.executable,str(root/'integration/install.py'),'--'+component+'-repo',str(repo)]
        subprocess.run(command,check=True,capture_output=True)
        before={p.relative_to(api).as_posix():(p.read_bytes(),p.stat().st_mtime_ns) for p in api.rglob('*') if p.is_file()}
        subprocess.run(command,check=True,capture_output=True)
        assert before=={p.relative_to(api).as_posix():(p.read_bytes(),p.stat().st_mtime_ns) for p in api.rglob('*') if p.is_file()}
        tree=ET.parse(master)
        assert tree.find('.//listener').get('class-name').endswith('ConformanceReporterMain$PreservingReporter')
        assert [n.get('path') for n in tree.findall('.//suite-file')]==[
            'existing-functional-suite.xml','inji'+component+'ConformanceSuite.xml']
