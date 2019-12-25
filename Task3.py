from nltk import word_tokenize
from nltk import sent_tokenize
from nltk.corpus import wordnet as wn
import numpy as np
import math
import nltk
import os
os.chdir('C:/Users/Krishna/Desktop/data(1)/data/')

def extract_synsets(first_word, second_word):
    max_similarity = -1000000000000
    result = (None, None)
    first_word_sysnsets = wn.synsets(first_word)
    second_word_synsets = wn.synsets(second_word)
    for synset_1 in first_word_sysnsets:
        for synset_2 in second_word_synsets:
            similarity = wn.path_similarity(synset_1,synset_2)
            if(similarity == None):
                continue
            if(similarity > max_similarity):
                max_similarity = similarity
                result = (synset_1, synset_2)
    return result

def extract_lemmas(synset):
    lemmas = set()
    for lemma in synset.lemmas():
        lemmas.add(lemma.name())
    return lemmas

def find_length(synset_1, synset_2):
    length = 10000000000000
    if(synset_1 == synset_2):
        length = 0
    else:
        related_words_1 = extract_lemmas(synset_1)
        related_words_2 = extract_lemmas(synset_2)
        if(len(related_words_1.intersection(related_words_2)) > 0):
            length = 0
        else:
            length = synset_1.shortest_path_distance(synset_2)
            if(length == None):
                length = 0
    return math.exp(-0.25 * length)

def extract_hypernym_distance(synset):
    distance = {}
    for hypernym in synset.hypernym_distances():
        distance[hypernym[0]] = hypernym[1]
    return distance

def lca_depth(synset_1, synset_2):
    if(synset_1 is None or synset_2 is None):
        return 0
    hypernyms_1 = extract_hypernym_distance(synset_1)
    hypernyms_2 = extract_hypernym_distance(synset_2)
    common_ancestors = dict(hypernyms_1.items() & hypernyms_2.items())
    if(len(common_ancestors) == 0):
        depth = 0
    else:
        depth = common_ancestors[max(common_ancestors, key=common_ancestors.get)]
    return (math.exp(0.5 * depth) - math.exp(-0.5 * depth)) / (math.exp(0.5 * depth) + math.exp(-0.5 * depth))

def calculate_word_similarity(first_word, second_word):
    relavant_synsets = extract_synsets(first_word, second_word)
    length = find_length(relavant_synsets[0], relavant_synsets[1])
    lca_height = lca_depth(relavant_synsets[0], relavant_synsets[1])
    if(lca_height == 0):
        return length
    return length * lca_height

def semantic_similarity(sentence_1, sentence_2):
    tokens_1 = set(word_tokenize(sentence_1))
    tokens_2 = set(word_tokenize(sentence_2))
    common_words = list(tokens_1.union(tokens_2))
    semantic_vector_1 = np.zeros(len(common_words))
    semantic_vector_2 = np.zeros(len(common_words))
    current_index = 0
    for word in common_words:
        word_similarity_1 = 1
        word_similarity_2 = 1
        if word not in tokens_1:
            similarity = []
            for token in tokens_1:
                similarity.append(calculate_word_similarity(token, word))
            word_similarity_1 = max(similarity)
        if word not in tokens_2:
            similarity = []
            for token in tokens_2:
                similarity.append(calculate_word_similarity(token, word))
            word_similarity_2 = max(similarity)
        semantic_vector_1[current_index] = word_similarity_1
        semantic_vector_2[current_index] = word_similarity_2
        current_index += 1
    return 5 * np.dot(semantic_vector_1, semantic_vector_2) / (np.linalg.norm(semantic_vector_1) * np.linalg.norm(semantic_vector_2))

def extract_relavant_pos_tags(sentence):
    verb_tags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    noun_tags = ['NN', 'NNS', 'NNP', 'NNPS']
    adjective_tags = ['JJ', 'JJR', 'JJS']
    adverb_tags = ['RB', 'RBR', 'RBS']
    tokens = word_tokenize(sentence.lower())
    tokens = nltk.pos_tag(tokens)
    relavant_tokens = {'verbs' : [], 'nouns' : [], 'adjectives' : [], 'adverbs' : []}
    for token in tokens:
        if(token[1] in verb_tags):
            relavant_tokens['verbs'].append(token[0])
        elif(token[1] in noun_tags):
            relavant_tokens['nouns'].append(token[0])
        elif(token[1] in adjective_tags):
            relavant_tokens['adjectives'].append(token[0])
        elif(token[1] in adverb_tags):
            relavant_tokens['adverbs'].append(token[0])
    return relavant_tokens

def pos_similarity_tag(relavant_tokens_1, relavant_tokens_2, pos_tag):
    similarity = 1
    if(len(relavant_tokens_1[pos_tag]) == len((relavant_tokens_2[pos_tag]))):
        for pos in range(len(relavant_tokens_1[pos_tag])):
            similarity = similarity * calculate_word_similarity(relavant_tokens_1[pos_tag][pos], relavant_tokens_2[pos_tag][pos])
    return similarity

def find_pos_similarity(sentence_1, sentence_2):
    relavant_tokens_1 = extract_relavant_pos_tags(sentence_1)
    relavant_tokens_2 = extract_relavant_pos_tags(sentence_2)
    verb_similarity = pos_similarity_tag(relavant_tokens_1, relavant_tokens_2, 'verbs')
    noun_similarity = pos_similarity_tag(relavant_tokens_1, relavant_tokens_2, 'nouns')
    jj_similarity = pos_similarity_tag(relavant_tokens_1, relavant_tokens_2, 'adjectives')
    rb_similarity = pos_similarity_tag(relavant_tokens_1, relavant_tokens_2, 'adverbs')
    return 5 * verb_similarity * noun_similarity * jj_similarity * rb_similarity


def generate_train_file(data_file):
    sentence_1 = []
    sentence_2 = []
    similarity = []
    predicted_similarity = []
    text = open(data_file,'r',encoding='utf-8')
    data = text.read().split("\n")[1:]
    for line in data:
        record = line.split("\t")
        if(len(record) == 4):
            sentence_1.append(record[1].lower())
            sentence_2.append(record[2].lower())
            similarity.append(record[3])
            similarity_estimate = (semantic_similarity(record[1].lower(), record[2].lower()) + find_pos_similarity(record[1].lower(), record[2].lower())) / 2
            #predicted_similarity.append(semantic_similarity(record[1].lower(), record[2].lower()))
            #pos_similarity.append(find_pos_similarity(record[1].lower(), record[2].lower()))
            predicted_similarity.append(similarity_estimate)
    return sentence_1, sentence_2, similarity, predicted_similarity


def generate_training_data(sentence_1, sentence_2, similarity, predicted_similarity):
    training_data = open('train.csv', "wb")
    for position in range(len(sentence_1)):
        record =str(similarity[position]) + "," + str(round(predicted_similarity[position])) + "\n"
        training_data.write(record.encode('utf-8'))
    training_data.close()
    
def main(path):
    data_file = r"train-set.txt"
    sentence_1, sentence_2, similarity, predicted_similarity = generate_train_file(data_file)

