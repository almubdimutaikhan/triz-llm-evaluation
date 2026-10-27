"""Regression checks for failures that can change the scientific conclusion."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from analyze import estimate, family, filter_votes, selection_results


def pair(**kwargs):
    r = dict(pair_id="001__m__s0", case_id="001", gen_model="openai/gpt-4o",
             judge_model="google/gemini-2.5-flash", persona="naive", order="ab",
             a_arm="triz", b_arm="control", pick="A", picked_arm="triz", error="")
    r.update(kwargs)
    return [r, {**r, "order": "ba", "a_arm": r["b_arm"], "b_arm": r["a_arm"],
                "pick": "B" if r["pick"] == "A" else "A"}]


class ScientificContract(unittest.TestCase):
    def test_deepseek_aliases_are_same_family(self):
        self.assertEqual(family("deepseek/deepseek-v3.1"), family("deepseek/deepseek-chat-v3.1"))
        kept, _ = filter_votes(pair(gen_model="deepseek/deepseek-v3.1", judge_model="deepseek/deepseek-chat-v3.1"))
        self.assertEqual(kept, [])

    def test_two_orders_count_once(self):
        kept, _ = filter_votes(pair())
        self.assertEqual(len(kept), 1)

    def test_order_flip_is_excluded(self):
        rows = pair(); rows[1].update(pick="A", picked_arm="control")
        self.assertFalse(filter_votes(rows)[0])

    def test_duplicate_order_is_not_confirmation(self):
        rows = pair()
        self.assertFalse(filter_votes([rows[0], rows[0]])[0])
        self.assertFalse(filter_votes(rows + [rows[0]])[0])

    def test_invalid_pick_mapping_and_errors_are_excluded(self):
        rows = pair(); rows[1]["picked_arm"] = "control"
        self.assertFalse(filter_votes(rows)[0])
        self.assertFalse(filter_votes(pair(error="timeout"))[0])

    def test_case_bootstrap_does_not_treat_votes_as_cases(self):
        # Two independent cases, with many correlated votes each, still give wide uncertainty.
        rows = ([dict(case_id="a", picked_arm="triz")] * 100 +
                [dict(case_id="b", picked_arm="control")] * 100)
        r = estimate(rows, "triz", reps=1000)
        self.assertEqual((r["cases"], r["votes"], r["p"]), (2, 200, .5))
        self.assertEqual((r["ci_low"], r["ci_high"]), (0., 1.))

    def test_bootstrap_is_repeatable(self):
        rows = [dict(case_id=str(i), picked_arm="triz" if i % 2 else "control") for i in range(20)]
        self.assertEqual(estimate(rows, "triz", reps=100), estimate(rows, "triz", reps=100))

    def test_two_failures_are_not_selection_agreement(self):
        rows = [dict(judge="m", condition="rank", set_id="s", shuffle=str(i), n="41",
                     parse_status="failed", presented_order=";".join(f"c{x}" for x in range(41)),
                     discard_candidate_id="", discard_position="") for i in range(2)]
        r = selection_results(rows, [])[0]
        self.assertEqual(r["slates"], 0)
        self.assertIsNone(r["shuffled_agreement"])


if __name__ == "__main__":
    unittest.main()
