import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.dsa.trie import build_trie_from_words
from app.dsa.heap import LeaderboardEntry, build_leaderboard
from app.dsa.graph import TopicGraph, TOPIC_DEPENDENCIES


def test_trie_prefix_search_returns_correct_matches():
    trie = build_trie_from_words(["Two Sum", "Two Pointers Basics", "Trie Search", "Binary Search"])
    assert trie.search_prefix("Tw") == ["Two Pointers Basics", "Two Sum"]
    assert trie.search_prefix("Tri") == ["Trie Search"]


def test_trie_prefix_search_no_match_returns_empty():
    trie = build_trie_from_words(["Two Sum"])
    assert trie.search_prefix("Zzz") == []


def test_trie_is_case_insensitive():
    trie = build_trie_from_words(["Binary Search"])
    assert trie.search_prefix("bin") == ["Binary Search"]


def test_heap_orders_by_score_descending():
    entries = [
        LeaderboardEntry(user_id=1, user_name="Alice", score=5, last_submission_ts=100),
        LeaderboardEntry(user_id=2, user_name="Bob", score=8, last_submission_ts=200),
        LeaderboardEntry(user_id=4, user_name="Dan", score=3, last_submission_ts=90),
    ]
    top = build_leaderboard(entries, top_n=3)
    assert [e.user_name for e in top] == ["Bob", "Alice", "Dan"]


def test_heap_breaks_ties_by_earlier_timestamp():
    entries = [
        LeaderboardEntry(user_id=2, user_name="Bob", score=8, last_submission_ts=200),
        LeaderboardEntry(user_id=3, user_name="Carol", score=8, last_submission_ts=150),
    ]
    top = build_leaderboard(entries, top_n=2)
    assert top[0].user_name == "Carol"  # earlier timestamp wins the tie


def test_topic_graph_topological_order_respects_dependencies():
    graph = TopicGraph(TOPIC_DEPENDENCIES)
    order = graph.topological_order()
    assert order.index("Arrays") < order.index("Strings")
    assert order.index("Recursion") < order.index("Trees")
    assert order.index("Two Pointers") < order.index("Sliding Window")


def test_topic_graph_unlocked_topics_requires_all_prerequisites():
    graph = TopicGraph(TOPIC_DEPENDENCIES)
    unlocked = graph.unlocked_topics({"Arrays"})
    assert "Strings" in unlocked
    assert "Hashing" in unlocked
    assert "Sliding Window" not in unlocked  # needs Two Pointers first, not just Arrays
