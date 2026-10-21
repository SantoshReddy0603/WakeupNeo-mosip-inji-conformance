"""Controlled reporting inputs; never official conformance evidence."""
import pytest
from gate_policy import apply_component_gates


def report(certify=True, verify=True):
    return {'runs': {c: {'summary': {'is_gated_pass': passed},
                        'results': {'test': 'PASSED' if passed else 'REVIEW'}}
                     for c, passed in [('certify', certify), ('verify', verify)]},
            'consolidated': {}}


@pytest.mark.parametrize('certify,verify', [(True, False), (False, True), (True, True), (False, False)])
def test_independent_gate_truth_table(certify, verify):
    data = report(certify, verify)
    assert apply_component_gates(data, ['certify', 'verify']) == (certify and verify)
    assert data['runs']['certify']['summary']['gate_met'] == certify
    assert data['runs']['verify']['summary']['gate_met'] == verify
    assert data['runs']['verify']['results']['test'] == ('PASSED' if verify else 'REVIEW')


@pytest.mark.parametrize('component', ['certify', 'verify'])
def test_regression_is_scoped(component):
    data = report()
    diff = {'has_regressions': True, 'component_regressions': {component: [{'test': component + '::removed'}]}}
    assert not apply_component_gates(data, ['certify', 'verify'], diff)
    for c in data['runs']:
        assert data['runs'][c]['summary']['gate_met'] == (c != component)
        assert data['runs'][c]['summary']['is_gated_pass'] is True


@pytest.mark.parametrize('diff,error', [({'has_regressions': True}, None),
    ({'has_regressions': True, 'component_regressions': {'unscoped': [{}]}}, None), (None, 'invalid baseline')])
def test_unknown_or_failed_comparison_fails_closed(diff, error):
    data = report()
    assert not apply_component_gates(data, ['certify', 'verify'], diff, error)
    assert all(not r['summary']['gate_met'] for r in data['runs'].values())


def test_missing_component_fails_combined_without_contaminating_present_component():
    data = report()
    del data['runs']['verify']
    assert not apply_component_gates(data, ['certify', 'verify'])
    assert data['runs']['certify']['summary']['gate_met']
