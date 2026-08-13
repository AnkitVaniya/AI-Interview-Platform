"""
Trie (prefix tree) for fast autocomplete on question titles and topic names.
Insert is O(k), search-by-prefix is O(k + m) where k = prefix length,
m = number of matches — much faster than a SQL LIKE '%prefix%' scan at scale.
"""


class TrieNode:
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end_of_word = False
        self.full_words: set[str] = set()  # store originals at this node for quick suggestion lookup


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        normalized = word.lower()
        for char in normalized:
            node = node.children.setdefault(char, TrieNode())
            node.full_words.add(word)
        node.is_end_of_word = True

    def search_prefix(self, prefix: str, limit: int = 10) -> list[str]:
        node = self.root
        normalized = prefix.lower()
        for char in normalized:
            if char not in node.children:
                return []
            node = node.children[char]
        # full_words at this node = every original word passing through this prefix path
        return sorted(node.full_words)[:limit]


def build_trie_from_words(words: list[str]) -> Trie:
    trie = Trie()
    for w in words:
        trie.insert(w)
    return trie
