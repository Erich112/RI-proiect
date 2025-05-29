import math
import os
import threading

import requests
from bs4 import BeautifulSoup
import spacy
# python -m spacy download en_core_web_sm
import stemming
import btree
import trie

urlFileHashDict = []
filenamesToSearch = []
# initializam trie-urile
noiseRoot = trie.TrieNode()
exceptRoot = trie.TrieNode()
idfRoot = trie.TrieNode()
allHashFiles = []
bplustree = btree.BplusTree(order=5)
wordsInHTML = []
stopwordsToInsert = []
en = spacy.load("en_core_web_sm")
stopwords = en.Defaults.stop_words
for word in stopwords:
    newword = trie.filter_special_characters(word)
    if newword:
        stopwordsToInsert.append(newword.lower())

trie.insertWordsInTrie(noiseRoot, stopwordsToInsert)

exceptWords = ["9/11", "erich21"]
exceptWordsToInsert = []
for word in exceptWords:
    newword = trie.filter_special_characters(word)
    if newword:
        exceptWordsToInsert.append(newword.lower())

trie.insertWordsInTrie(exceptRoot, exceptWordsToInsert)
inputDir = "input/"


def hash_str(s):
    hash = 0
    for i in range(0, len(s)):
        hash = (31 * hash + ord(s[i])) % 1000
    return hash


def getAllCurrentFiles(cwd=os.getcwd()):
    files = os.scandir(cwd)
    print("CWD ", cwd)
    for file in files:
        print("FILE ", file)
        filenamesToSearch.append(file.name)


def findWordCountInHTML(file):
    file = inputDir + file
    print("COUNTING WORDS IN ", file)
    with open(file, 'r', encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        textlist = [text for text in soup.stripped_strings]
        print("CURRENT PHRASES FOUND ", textlist)
        filterTextList = []
        for phrase in textlist:
            for word in phrase.split():
                filterTextList.append(word)
        return len(filterTextList)


def findWordsInHTML(file):
    file = inputDir + file
    print("SEARCHING WORDS IN ", file)
    with open(file, 'r', encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        textlist = [text for text in soup.stripped_strings]
        print("CURRENT PHRASES FOUND ", textlist)
        filterTextList = []
        for phrase in textlist:
            for word in phrase.split():
                filterTextList.append(word)
        print("WORDS FOUND ", filterTextList)
        return filterTextList


def findLinksInHTML(file):
    file = inputDir + file
    with open(file, 'r', encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True)]
        print(links)
        return links


def stamWord(word):
    p = stemming.PorterStemmer()
    print("STAMMING WORD ", word)
    newword = p.stem(word, 0, len(word) - 1)
    print("STAMMED WORD: ", newword)
    return newword


def FileToBtreeAndTrie(inputFile):
    wordsInHTML = findWordsInHTML(inputFile)
    # extragem cuvintele din fisier
    wordsToInsertAfterStemming = []
    for word in wordsInHTML:
        word = trie.filter_special_characters(word)
        if trie.search(noiseRoot, word):
            print("found noise word, skipping")
            continue
        elif trie.search(exceptRoot, word):
            print("found exception word, inserting as is")
            wordsToInsertAfterStemming.append(word)
        else:
            print("found normal word, stamming first then inserting")
            wordsToInsertAfterStemming.append(stamWord(word))

    for word in wordsToInsertAfterStemming:
        key = str(hash_str(inputFile))
        value = str(word)
        bplustree.insert(value, key)

    print("the final btree is")
    btree.printTree(bplustree)


def crawlBot(baseurl="https://www.robotstxt.org"):
    print("LAB 8")
    Q = [baseurl]
    visitedPages = []

    r = requests.get(baseurl + "/robots.txt")
    print(r.status_code)
    if r.status_code == 200:
        # print(r.text)
        if "Disallow: /" in r.text:
            print("server prohibited all robots, cannot do anything")
            return
    while len(Q) != 0:
        link = Q.pop()
        try:
            r = requests.get(link)
            print(r.status_code)
            visitedPages.append(link)
            print("visiting ", link)
            if r.status_code == 200:
                # print(r.text)
                filename = link.split('/')[-1]
                if len(filename) <= 1:
                    filename = filename + "page"
                print(filename)
                foundHTML = open(inputDir + filename, "w+")
                foundHTML.write(r.text)
                foundHTML.close()
                links = findLinksInHTML(filename)
                for link in links:
                    if "https://" in link or "http://" in link:
                        print(link)
                        Q.append(link)
                        urlFileHashDict.append([filename, str(hash_str(filename)), link])
                    elif baseurl + link not in visitedPages:
                        print(baseurl + link)
                        Q.append(baseurl + link)
                        urlFileHashDict.append([filename, str(hash_str(filename)), baseurl + link])
        except:
            print("error visiting")
            return


def startSearchinginfiles():
    print("lab 5")
    getAllCurrentFiles("input\\")
    print("CURRENT FILES")
    print(filenamesToSearch)
    for file in filenamesToSearch:
        temp = findWordsInHTML(file)
        for w in temp:
            wordsInHTML.append(w)
        FileToBtreeAndTrie(file)

    # lab 6
    wordsDocAppsAndIdf = []
    temp = btree.treeToList(bplustree)
    print("LAB 6")

    wordsToProcessFromBtree = []
    for arr in temp:
        for word in arr:
            wordsToProcessFromBtree.append(word)

    print(wordsToProcessFromBtree)
    finalListOfRepeats = []
    for file in filenamesToSearch:
        tempWords = findWordsInHTML(file)
        filehash = str(hash_str(file))
        allHashFiles.append(filehash)
        print("current file hash " + filehash)
        for word in tempWords:
            keys = btree.getKeysForValue(bplustree, word)
            if keys is not None:
                print("keys are ", keys)
                for key in keys:
                    if filehash in key:
                        print("word " + word + " from file in the btree")
                        if trie.search(idfRoot, word) is False:
                            print("word is not in the idf trie, inserting")
                            trie.insert(idfRoot, word)
                            finalListOfRepeats.append([word, filehash, 1])
                        else:
                            print("word is in the idf trie, lets see")
                            for items in finalListOfRepeats:
                                if word in items[0]:
                                    print("current:", items[0], ", ", items[1], ", ", items[2])
                                    print("word ", word, " found in file of hash ", filehash,
                                          " exists already, count++")
                                    items[2] += 1

    print("Done processing, here")
    print(finalListOfRepeats)
    idfDict = {}
    for word, hash, count in finalListOfRepeats:
        if word in idfDict:
            idfDict[word] += count
        else:
            idfDict[word] = count

    idfArr = []
    print(idfDict)
    for item in idfDict.items():
        idfArr.append([item[0], max(math.log(2 / (1 + item[1]), 2), 0)])

    print(idfArr)
    dArr = []
    for word, hash, count in finalListOfRepeats:
        for entry in urlFileHashDict:
            if hash in entry[1]:
                print(entry)
                d = {word: (count / findWordCountInHTML(entry[0])) * idfDict[word]}
                print(d)
                dArr.append(d)
    print(dArr)

    print("LAB 7")
    inputterms = input("introdu cuvantul pe care vrei sa-l cauti: ")
    searchWord = inputterms.split(' ')

    for term in searchWord:
        print("cautare binara")
        print(term)
        foundHash = []
        NotFoundHash = []
        for word, chash, count in finalListOfRepeats:
            if term in word:
                if chash not in foundHash:
                    foundHash.append(chash)

        print("cautare vectoriala")
        for entry in dArr:
            for key in entry.keys():
                if term in key:
                    if entry[term] >= 0:
                        print("found word")

        for hash in allHashFiles:
            if hash not in foundHash:
                NotFoundHash.append(hash)

        print("word found in docs: ", foundHash, "and not in: ", NotFoundHash)
        for entry in urlFileHashDict:
            for hash in foundHash:
                if hash in str(entry[1]):
                    print(entry[2])


if __name__ == "__main__":
    print("send help")
    threads = []
    links = [
        "https://www.robotstxt.org"
    ]
    for link in links:
        # Using `args` to pass positional arguments and `kwargs` for keyword arguments
        t = threading.Thread(target=crawlBot, args=(link,), kwargs={})
        threads.append(t)

    # Start each thread
    for t in threads:
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    print(urlFileHashDict)
    startSearchinginfiles()
    print("Done!")
