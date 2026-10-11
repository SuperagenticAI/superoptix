"""superoptix.bdd.minimal@1 scoring: JSON punctuation and expected_keywords."""

from superoptix.cli.commands.agent import _MinimalDSPyBDDEvaluator as E


class _Pred:
    def __init__(self, data):
        self._data = data

    def toDict(self):
        return dict(self._data)


def _ev():
    return E.__new__(E)


def test_short_answer_with_expected_keywords_passes():
    expected = {"answer": "Paris", "expected_keywords": ["Paris"]}
    actual = E._actual_to_text(_Pred({"answer": "Paris"}))
    assert actual == "Paris"
    assert _ev()._evaluate(actual, expected)["passed"] is True


def test_wrong_answer_and_echo_baseline_fail():
    expected = {"answer": "Paris", "expected_keywords": ["Paris"]}
    assert _ev()._evaluate("Lyon", expected)["passed"] is False
    echo = "What is the capital city of France? Answer with the city name only."
    assert _ev()._evaluate(echo, expected)["passed"] is False


def test_missing_required_keyword_fails_with_reason():
    expected = {"expected_keywords": ["phase", "rollout"]}
    res = _ev()._evaluate("phase one then phase two", expected)
    assert res["passed"] is False
    assert "rollout" in res["failure_reason"]


def test_json_punctuation_does_not_break_tokens():
    assert E._tokens('{"answer": "Paris"}') == {"answer", "paris"}
