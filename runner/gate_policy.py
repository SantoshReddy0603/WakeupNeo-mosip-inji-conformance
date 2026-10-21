"""Independent reporting gates; official module outcomes are never modified."""


def apply_component_gates(report, components, diff=None, error=None):
    """Scope known regressions; an unscoped/comparison error fails every gate."""
    regressions = (diff or {}).get('component_regressions', {})
    unknown = bool(error or report.get('error') or report.get('diff_error'))
    if diff and diff.get('has_regressions'):
        unknown |= not regressions or bool(set(regressions) - {'certify', 'verify'})
    for component in components:
        if component not in report['runs']:
            continue
        summary = report['runs'][component]['summary']
        summary['regression_gate_met'] = not unknown and not bool(regressions.get(component))
        summary['gate_met'] = (summary.get('is_gated_pass') is True
                               and summary['regression_gate_met'])
    gate = bool(components) and all(
        report['runs'].get(c, {}).get('summary', {}).get('gate_met') is True for c in components)
    report['consolidated']['gate_met'] = gate
    report['consolidated']['status'] = (
        'BASELINE_ACCEPTED' if report['consolidated'].get('expected_failures') else 'PASSED') if gate else 'FAILED'
    report['gate_policy'] = 'independent-components-v1'
    return gate
