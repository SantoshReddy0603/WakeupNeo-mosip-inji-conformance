"""Independent reporting gates; official module outcomes are never modified.

Unknown comparison failures reject all selected components. Known regressions
reject only their component, while the combined gate requires every component."""


def apply_component_gates(report, components, diff=None, error=None):
    """Combine each official result gate with its scoped regression decision; fail closed on unknown errors."""
    regressions = (diff or {}).get('component_regressions', {})
    # Without a trustworthy component attribution, no component can be qualified.
    unknown = bool(error or report.get('error') or report.get('diff_error'))
    if diff and diff.get('has_regressions'):
        unknown |= not regressions or bool(set(regressions) - {'certify', 'verify'})
    for component in components:
        if component not in report['runs']:
            continue
        summary = report['runs'][component]['summary']
        # Keep a Verify regression from overriding Certify's independent decision.
        summary['regression_gate_met'] = not unknown and not bool(regressions.get(component))
        summary['gate_met'] = (summary.get('is_gated_pass') is True
                               and summary['regression_gate_met'])
    # Missing components and empty selections cannot produce a combined success.
    gate = bool(components) and all(
        report['runs'].get(c, {}).get('summary', {}).get('gate_met') is True for c in components)
    report['consolidated']['gate_met'] = gate
    report['consolidated']['status'] = (
        'BASELINE_ACCEPTED' if report['consolidated'].get('expected_failures') else 'PASSED') if gate else 'FAILED'
    report['gate_policy'] = 'independent-components-v1'
    return gate
