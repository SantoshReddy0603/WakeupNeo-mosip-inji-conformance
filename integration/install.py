"""Install into actual Inji api-test modules, which consume mosip-functional-tests commons."""
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--verify-repo', type=Path)
parser.add_argument('--certify-repo', type=Path)
args = parser.parse_args()
template = (Path(__file__).parent / 'OpenIDConformanceTest.java.in').read_text()
def write_changed(path, content):
    if not path.exists() or path.read_text() != content:
        path.write_text(content)

for component, repo in [('verify', args.verify_repo), ('certify', args.certify_repo)]:
    if repo is None:
        continue
    module = 'inji' + component
    root = repo.resolve() / 'api-test'
    if not (root / 'pom.xml').is_file():
        raise SystemExit(f'Not an actual Inji api-test module: {root}')
    java = root / f'src/main/java/io/inji/testrig/apirig/{module}/testscripts/OpenIDConformanceTest.java'
    java.parent.mkdir(parents=True, exist_ok=True)
    write_changed(java, template.replace('@MODULE@', module).replace('@COMPONENT@', component))
    reporter = (Path(__file__).parent / 'ConformanceReporterMain.java.in').read_text()
    write_changed(java.parent / 'ConformanceReporterMain.java', reporter.replace('@MODULE@', module))
    suites = root / 'testNgXmlFiles'
    name = module + 'ConformanceSuite.xml'
    write_changed(suites / name, f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="{module} OpenID conformance"><test name="OpenID {component}"><classes>
<class name="io.inji.testrig.apirig.{module}.testscripts.OpenIDConformanceTest"/>
</classes></test></suite>
''')
    master = suites / (module + 'MasterTestSuite.xml')
    content = master.read_text()
    content = content.replace('io.mosip.testrig.apirig.report.EmailableReport',
        'io.inji.testrig.apirig.' + module + '.testscripts.ConformanceReporterMain$PreservingReporter')
    entry = f'<suite-file path="{name}" />'
    if entry not in content:
        content = content.replace('</suite-files>', '\t' + entry + '\n\t</suite-files>')
    write_changed(master, content)
    print(f'Integrated {component}: {java}')
