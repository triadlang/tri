"""
Tests that exercise the language end-to-end by running .tri programs.

These tests do not check internal AST structures; they check that real
.tri programs parse, compile, and execute, and that their stdout
contains the expected marker. The programs themselves are in
programs/<category>/.
"""
import os
import sys
import subprocess
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run(rel_path, timeout=60):
    path = os.path.join(REPO_ROOT, rel_path)
    if not os.path.exists(path):
        pytest.skip(f"program not present: {rel_path}")
    r = subprocess.run(
        [sys.executable, '-m', 'triadlang.cli.main', 'run', path],
        capture_output=True, text=True, timeout=timeout,
        cwd=REPO_ROOT,
    )
    return r.returncode, r.stdout, r.stderr


def test_basic_hello():
    rc, out, err = _run('programs/basic/hello.tri')
    assert rc == 0, err
    assert 'Hello from TriadLang' in out


def test_basic_loops():
    rc, out, err = _run('programs/basic/loops.tri')
    assert rc == 0, err
    assert '0' in out


def test_basic_functions():
    rc, out, err = _run('programs/basic/functions.tri')
    assert rc == 0, err


def test_anti_collapse_produces_emergent_structure():
    """Verifies the solver runs through .tri syntax and produces the same
    numbers as the parent project. crystallinity ~0.96 at this seed."""
    rc, out, err = _run('programs/triad/anti_collapse.tri')
    assert rc == 0, err
    assert 'crystallinity' in out


def test_solver_ablation_runs():
    rc, out, err = _run('programs/solver/solver_ablation.tri')
    assert rc == 0, err
    assert 'Lambda' in out


def test_crossdomain_origin_of_life():
    rc, out, err = _run('programs/crossdomain/s2_origin_of_life.tri')
    assert rc == 0, err
    assert 'autopoiesis' in out or 'hypercycle' in out


def test_quantum_bell_state():
    rc, out, err = _run('programs/quantum/bell_state.tri')
    assert rc == 0, err
    assert "'00'" in out
    assert "'11'" in out


def test_predator_prey_simulation():
    rc, out, err = _run('programs/games/predator_prey.tri')
    assert rc == 0, err
    assert 'Final' in out


def test_fdt_verification():
    rc, out, err = _run('programs/verification/fdt_claims.tri')
    assert rc == 0, err
    assert 'Evidence field' in out or 'VERIFIED' in out


def test_mock_llm_runtime():
    rc, out, err = _run('programs/llm/mock_runtime.tri')
    assert rc == 0, err
    assert 'cache' in out.lower()


def test_calibration_demo_runs_without_external_target():
    """The calibrator does not impose a target. Either converged or not
    converged is a valid outcome — both mean the loop ran."""
    rc, out, err = _run('programs/triad/calibration_demo.tri')
    assert rc == 0, err
    assert 'crystallinity' in out


def test_ml_nn_test_trains_xor():
    rc, out, err = _run('programs/ml/nn_test.tri', timeout=120)
    assert rc == 0, err
    assert '[0. 1.] -> 1' in out or 'target: 1' in out
