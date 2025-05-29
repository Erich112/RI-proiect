import string


def filter_special_characters(word):
    return ''.join([char for char in word if char in string.ascii_lowercase])


class TrieNode:

    def __init__(self):
        # Array for children nodes of each node
        self.children = [None] * 26

        # for end of word
        self.isEndOfWord = False


# Method to insert a key into the Trie
def insert(root, key):
    print("______DE INSERAT____:", key)
    # Initialize the curr pointer with the root node
    curr = root

    # Iterate across the length of the string
    for c in key:
        # Check if the node exists for the
        # current character in the Trie

        index = ord(c) - ord('a')
        if curr.children[index] is None:
            # If node for current character does
            # not exist then make a new node
            new_node = TrieNode()

            # Keep the reference for the newly
            # created node
            curr.children[index] = new_node

        # Move the curr pointer to the
        # newly created node
        curr = curr.children[index]

    # Mark the end of the word
    curr.isEndOfWord = True


# Method to search a key in the Trie
def search(root, key):
    print("______DE CAUTAT____:", key)

    # Initialize the curr pointer with the root node
    curr = root

    # Iterate across the length of the string
    for c in key:

        # Check if the node exists for the
        # current character in the Trie
        index = ord(c) - ord('a')
        if curr.children[index] is None:
            return False

        # Move the curr pointer to the
        # already existing node for the
        # current character
        curr = curr.children[index]

    # Return true if the word exists
    # and is marked as ending
    return curr.isEndOfWord


def insertWordsInTrie(root, arr):
    # arr = ["and", "ant", "do", "geek", "dad", "ball"]
    for s in arr:
        insert(root, s)


def partial_search(root, key):
    curr = root
    results = []

    # Navigate to the end of the prefix in the trie
    for c in key:
        index = ord(c) - ord('a')
        if curr.children[index] is None:
            return []  # No words with the given prefix
        curr = curr.children[index]

    # Helper function to perform DFS from the current node
    def dfs(node, path):
        if node.isEndOfWord:
            results.append(path)
        for i in range(26):
            if node.children[i] is not None:
                dfs(node.children[i], path + chr(i + ord('a')))

    # Start DFS from the last node of the prefix
    dfs(curr, key)
    return results


def searchWordsInTrie(root, search_keys):
    # search_keys = ["do", "gee", "bat"]
    wordsFound = 0
    for s in search_keys:
        # print(f"Key : {s}")
        if search(root, s):
            # print("Present")
            wordsFound += 1
        # else:
        # print("Not Present")
    return wordsFound
