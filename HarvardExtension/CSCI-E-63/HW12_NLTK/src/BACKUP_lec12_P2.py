import nltk
from nltk.corpus import inaugural
from nltk.corpus import wordnet as wn
from collections import defaultdict

#choose to lower-case all words to avoid casing issues
long_words = (w.lower() for w in inaugural.words() if len(w) > 7)
fdist = nltk.FreqDist(long_words)
#textbook indicated a FreqDist came sorted, with most frequent counts first, but I didn't see that
freq_long_words = sorted(fdist.keys(), key = lambda w: fdist[w], reverse = True)[:10]
long_words_with_counts = ['{0}: {1}'.format(k, fdist[k]) for k in freq_long_words]
print '\r\n'.join(long_words_with_counts)


syns = defaultdict(set)
for w in freq_long_words:
    for ss in wn.synsets(w):
        names = ss.lemma_names()
        syns[w].update(names)

most_synonyms = max(syns.keys(), key = lambda k: len(syns[k]))
print 'Word with most synonyms: "{0}", count: {1}'.format(most_synonyms, len(syns[most_synonyms]))

print
print '"WORD"'.ljust(15) + 'SYNONYMS'
for k,v in syns.items():
    print '"{0}"'.format(k).ljust(15) + ', '.join(v)
    print


hypo_dict = defaultdict(set)
for w in freq_long_words:
    for ss in wn.synsets(w):
        for hyp in ss.hyponyms():
            names = hyp.lemma_names()
            hypo_dict[w].update(names)

most_hyponyms = max(hypo_dict.keys(), key = lambda k: len(hypo_dict[k]))
print 'Word with most hyponyms: "{0}", count: {1}'.format(most_hyponyms, len(hypo_dict[most_hyponyms]))

print
for k,v in hypo_dict.items():
    print 'WORD: "{0}"'.format(k)
    print 'HYPONYMS: '
    for i in range(0, len(v), 5):
        print ''.ljust(5) + ', '.join(list(v)[i:i+5])
    print
        
