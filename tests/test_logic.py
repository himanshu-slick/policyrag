from eval.score import answer_match, mrr, recall_at_k

from policyrag.answer import cited_hits, is_weak
from policyrag.chunk import _join, _split_long, parse_pdf
from policyrag.config import CORPUS_DIR
from policyrag.retrieve import Hit, or_query, rrf


def hit(doc="d", section="s", score=0.0, id=1):
    return Hit(id, doc, "T", 1, section, 1, "c", score)


def test_rrf_prefers_items_ranked_high_in_both_lists():
    assert rrf([[1, 2, 3], [3, 1, 4]])[:2] == [1, 3]


def test_rrf_includes_items_from_a_single_list():
    assert set(rrf([[1], [2]])) == {1, 2}


def test_or_query_dedupes_and_strips_punctuation():
    assert or_query("What's the waiting period? Waiting!") == "what | s | the | waiting | period"


def test_recall_and_mrr():
    qs = [{"doc": "a", "section": "x"}, {"doc": "b", "section": "y"}]
    hits = [[hit("z"), hit("a", "x")], [hit("q")]]
    assert recall_at_k(hits, qs, k=5) == 0.5
    assert recall_at_k(hits, qs, k=1) == 0.0
    assert mrr(hits, qs) == 0.25


def test_answer_match_is_case_insensitive():
    assert answer_match("Cover starts after 30 Days.", "30 days")


def test_join_merges_wrapped_lines_but_keeps_clauses():
    lines = ["1.1 First clause", "continues here", "1.2 Second"]
    assert _join(lines) == "1.1 First clause continues here\n1.2 Second"


def test_split_long_keeps_short_text_whole():
    assert _split_long("1.1 a\n1.2 b") == ["1.1 a\n1.2 b"]


def test_cited_hits_maps_numbers_and_ignores_out_of_range():
    hits = [hit(id=1), hit(id=2)]
    assert [h.id for h in cited_hits("Yes [2]. Also [9].", hits)] == [2]


def test_is_weak_when_empty_or_low_score():
    assert is_weak([])
    assert is_weak([hit(score=-10.0)])
    assert not is_weak([hit(score=5.0)])


def test_parse_pdf_extracts_seven_sections_with_metadata():
    chunks = parse_pdf(CORPUS_DIR / "shieldcare-health.pdf")
    assert [c.section_no for c in chunks] == [1, 2, 3, 4, 5, 6, 7]
    assert chunks[3].section == "Waiting Periods"
    assert "30 days" in chunks[3].content
    assert chunks[0].title == "ShieldCare Health Plus"
