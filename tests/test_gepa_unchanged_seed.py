"""Advisory GEPA unchanged-seed / zero-gain detection (no network needed)."""

import superoptix  # noqa: F401  (import superoptix before dspy)
import dspy
from superoptix.optimizers.holdout import (
    gain_report,
    predictor_instructions,
    read_holdout_record,
    split_holdout,
    unchanged_seed_report,
    write_holdout_record,
)


class _Prog(dspy.Module):
    def __init__(self):
        super().__init__()
        self.answer = dspy.Predict("question -> answer")


def _with_instructions(prog, text):
    out = prog.deepcopy()
    out.answer.signature = out.answer.signature.with_instructions(text)
    return out


def test_identical_program_flags_unchanged_seed():
    seed = _Prog()
    gains = gain_report(0.5, 0.5, 0.4, 0.4)
    report = unchanged_seed_report(seed, seed.deepcopy(), gains)
    assert report["unchanged_seed"] is True
    assert report["instructions_compared"] is True
    assert report["zero_gain"] is True
    assert report["gain_source"] == "heldout"
    assert "unchanged seed" in report["warning"]


def test_changed_instructions_with_gain_has_no_warning():
    seed = _Prog()
    opt = _with_instructions(seed, "Answer carefully and concisely.")
    assert (
        predictor_instructions(opt)["answer"] != predictor_instructions(seed)["answer"]
    )
    report = unchanged_seed_report(seed, opt, gain_report(0.5, 0.7, 0.4, 0.6))
    assert report["unchanged_seed"] is False
    assert report["changed_predictors"] == ["answer"]
    assert report["zero_gain"] is False
    assert report["warning"] is None


def test_changed_instructions_but_zero_heldout_gain_warns():
    seed = _Prog()
    opt = _with_instructions(seed, "Different text.")
    report = unchanged_seed_report(seed, opt, gain_report(0.5, 0.8, 0.4, 0.4))
    assert report["unchanged_seed"] is False
    assert report["zero_gain"] is True
    assert "no heldout gain" in report["warning"]


def test_falls_back_to_train_gain_without_heldout():
    seed = _Prog()
    opt = _with_instructions(seed, "Other.")
    report = unchanged_seed_report(seed, opt, gain_report(0.5, 0.5, None, None))
    assert report["gain_source"] == "train" and report["zero_gain"] is True


def test_non_dspy_objects_are_not_flagged_unchanged():
    report = unchanged_seed_report(object(), object(), {})
    assert report["instructions_compared"] is False
    assert report["unchanged_seed"] is False
    assert report["warning"] is None


def test_flag_is_written_to_holdout_record(tmp_path):
    ex = [dspy.Example(q=f"q{i}", a=f"a{i}").with_inputs("q") for i in range(10)]
    split = split_holdout(ex, 0.2, seed=1)
    seed = _Prog()
    gains = gain_report(0.5, 0.5, 0.4, 0.4)
    gains["gepa"] = unchanged_seed_report(seed, seed.deepcopy(), gains)
    path = tmp_path / "holdout.json"
    write_holdout_record(path, split, gains)
    assert read_holdout_record(path)["gepa"]["unchanged_seed"] is True
