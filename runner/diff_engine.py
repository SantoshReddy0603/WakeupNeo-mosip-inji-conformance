"""
Result Diff Engine.
Detects regressions (PASS -> FAIL), fixes (FAIL -> PASS), additions, and removals across runs.
"""

from typing import Dict, Any, List


class DiffEngine:
    @staticmethod
    def compare_runs(baseline: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compares baseline results with current results.
        Returns categorization of differences including regressions, fixes, new tests, and removed tests.
        """
        base_results = baseline.get("consolidated", baseline).get("results", {})
        curr_results = current.get("consolidated", current).get("results", {})

        regressions: List[Dict[str, str]] = []
        fixes: List[Dict[str, str]] = []
        new_tests: List[Dict[str, str]] = []
        removed_tests: List[Dict[str, str]] = []
        unchanged: List[Dict[str, str]] = []
        status_changes = []
        review_changes = []
        unexpected_skips = []

        all_tests = set(base_results.keys()).union(set(curr_results.keys()))

        for test_name in sorted(all_tests):
            base_status = base_results.get(test_name)
            curr_status = curr_results.get(test_name)
            if base_status is not None and curr_status is not None and base_status != curr_status:
                change = {'test':test_name, 'previous':base_status, 'current':curr_status}
                status_changes.append(change)
                if 'REVIEW' in {base_status,curr_status}:
                    review_changes.append(change)
                if curr_status == 'SKIPPED':
                    unexpected_skips.append(change)

            if base_status is None:
                new_tests.append({"test": test_name, "status": curr_status})
            elif curr_status is None:
                removed_tests.append({"test": test_name, "previous": base_status})
            elif base_status in ["PASSED", "WARNING", "SUCCESS"] and curr_status not in ["PASSED", "WARNING", "SUCCESS"]:
                regressions.append({
                    "test": test_name,
                    "previous": base_status,
                    "current": curr_status
                })
            elif base_status in ["FAILED", "INTERRUPTED", "TIMEOUT", "ERROR", "REVIEW", "CANCELLED"] and curr_status in ["PASSED", "WARNING", "SUCCESS"]:
                fixes.append({
                    "test": test_name,
                    "previous": base_status,
                    "current": curr_status
                })
            elif base_status == curr_status:
                unchanged.append({
                    "test": test_name,
                    "status": curr_status
                })

        old = baseline.get('consolidated',baseline)
        new = current.get('consolidated',current)
        old_benchmark = baseline.get('benchmark',old.get('benchmark'))
        new_benchmark = current.get('benchmark',new.get('benchmark'))
        benchmark_available = old_benchmark is not None and new_benchmark is not None
        component_regressions = {}
        for change in regressions + removed_tests + unexpected_skips:
            component = change['test'].split('::')[0] if '::' in change['test'] else 'unscoped'
            if change not in component_regressions.setdefault(component,[]):
                component_regressions[component].append(change)
        return {
            "regressions_count": len(regressions),
            "fixes_count": len(fixes),
            "new_count": len(new_tests),
            "removed_count": len(removed_tests),
            "regressions": regressions,
            "fixes": fixes,
            "new_tests": new_tests,
            "removed_tests": removed_tests,
            'unchanged':unchanged,
            'status_changes':status_changes,
            'review_changes':review_changes,
            'unexpected_skips':unexpected_skips,
            'component_regressions':component_regressions,
            'benchmark_comparison_available':benchmark_available,
            'benchmark_changes':([{'previous':old_benchmark,'current':new_benchmark}]
                if benchmark_available and old_benchmark != new_benchmark else []),
            'gate_changes':([{'previous':old['gate_met'],'current':new['gate_met']}]
                if 'gate_met' in old and 'gate_met' in new and old['gate_met'] != new['gate_met'] else []),
            "has_regressions": bool(regressions or removed_tests or unexpected_skips)
        }
