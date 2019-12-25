import nltk
from nltk import sent_tokenize,word_tokenize
from nltk.corpus import wordnet
from nltk import pos_tag
import spacy

#class CorpusReader:
def tokenizer(sentence_1):
    return (word_tokenize(sentence_1))

def extract_lemmas(synset):
    lemmas = set()
    for lemma in synset.lemmas():
        lemmas.add(lemma.name())
    return lemmas

def lemmatizer(tokens):
    lemmas = {}
    for token in tokens:
        lemmas[token] = []
        synsets = wordnet.synsets(token)
        for synset in synsets:
            temp_lemmas = extract_lemmas(synset) 
            for lemma in temp_lemmas:
                lemmas[token].append(lemma)
    return lemmas

def pos_tagger(tokens):
    return nltk.pos_tag(tokens)

def extract_hypernym_distance(synset):
    distance = {}
    for hypernym in synset.hypernym_distances():
        distance[hypernym[0]] = hypernym[1]
    return distance

def hypernyms(tokens):
    hypernyms = {}
    for token in tokens:
            hypernyms[token] = {}
            synsets = wordnet.synsets(token)
            for synset in synsets:
                hypernyms[token].update(extract_hypernym_distance(synset)) 
    return hypernyms

def hyponyms(tokens):
    hyponyms = {}
    for token in tokens:
            hyponyms[token] = []
            synsets = wordnet.synsets(token)
            for synset in synsets:
                hyponyms[token] += synset.hyponyms() 
    return hyponyms

def dependencyParseTree(string):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(string)
    for token in doc:
        print (str(token.text),  str(token.lemma_),  str(token.pos_),  str(token.dep_))


def holonyms(tokens):
    holonyms = {}
    for token in tokens:
            holonyms[token] = []
            synsets = wordnet.synsets(token)
            for synset in synsets:
                holonyms[token] += synset.part_holonyms()
                holonyms[token] += synset.substance_holonyms()
                holonyms[token] += synset.member_holonyms()
    return holonyms

def meronyms(tokens):
    meronyms = {}
    for token in tokens:
            meronyms[token] = []
            synsets = wordnet.synsets(token)
            for synset in synsets:
                meronyms[token] += synset.part_meronyms()
                meronyms[token] += synset.substance_meronyms()
                meronyms[token] += synset.member_meronyms()
    return meronyms

def main(string):
    tokens = tokenizer(string)
    print ("##########Tokens for the given string##########")
    print (tokens)
    print ("##########Lemmas for the sentence##########")
    lemma = lemmatizer(tokens)
    print (lemma)
    print ("##########Pos tags##########")
    pos_tagger_var = pos_tagger(tokens)
    print (pos_tagger_var)
    print ("##########Hypernyms##########")
    hypernyms_var = hypernyms(tokens)
    for hypernym in hypernyms_var.keys():
        print(hypernym)
        print(hypernyms_var[hypernym])
        print('\n')
    print("##########hyponyms##########")
    hyponyms_var = hyponyms(tokens)
    for hyponym in hyponyms_var.keys():
        print(hyponym)
        print(hyponyms_var[hyponym])
        print('\n');
    print ("##########holonyms##########")
    holonyms_var = holonyms(tokens)
    for holonym in holonyms_var.keys():
        print(holonym)
        print(holonyms_var[holonym])
        print('\n');
    print ("##########Meronyms##########")
    meronyms_var = meronyms(tokens)
    for meronym in meronyms_var.keys():
        print(meronym)
        print(meronyms_var[meronym])
        print('\n')
    print("#########Dependency Parse Tree##########")
    dependencyParseTree(string)

sentence = input("Enter a sentence on to obtain the relavant features")
main(sentence)
