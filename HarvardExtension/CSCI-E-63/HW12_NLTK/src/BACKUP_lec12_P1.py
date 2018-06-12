import nltk
from nltk.corpus import gutenberg as gut

modals = ['can', 'could', 'may', 'might', 'will', 'would', 'should']
books = gut.fileids() #[:2]
cfd = nltk.ConditionalFreqDist(
    (book, word)
    for book in books
    for word in gut.words(fileids=book) ) # if word in modals)

width = max(len(book) for book in cfd.iterkeys()) + 5
print ''.ljust(width) + ''.join(modal.ljust(9) for modal in modals)
for book in cfd.iterkeys():
    print book.ljust(width)  + ' '.join(['{0:.6f}'.format(cfd[book].freq(modal)) for modal in modals])

#sanity check
emma = gut.words('austen-emma.txt')
fdist_emma = nltk.FreqDist(emma)
print fdist_emma.freq('can')
print cfd['austen-emma.txt'].freq('can')
print cfd['austen-emma.txt']['can']/(len(emma) * 1.0)


rng_lookup = {}
for modal in modals:
    max_modal_book = max(cfd.iterkeys(), key = (lambda key: cfd[key].freq(modal)))
    min_modal_book = min(cfd.iterkeys(), key = (lambda key: cfd[key].freq(modal)))
    rng = cfd[max_modal_book].freq(modal) - cfd[min_modal_book].freq(modal)
    rng_lookup[modal] = (rng, min_modal_book, max_modal_book )
    print 'modal: "{0}" range, max - min: {1:.6f}'.format(
        modal, rng)
    print '\t {0} only has {1} relative freq'.format(min_modal_book, cfd[min_modal_book].freq(modal))
    print '\t {0} has most used relative freq, at {1}'.format(max_modal_book, cfd[max_modal_book].freq(modal))

print
print 'Two modals with with the largest span of relative frequencies:'
for k in sorted(rng_lookup, key = (lambda key: rng_lookup[key][0]), reverse = True)[:2]:
    print '{0}: {1}'.format(k, rng_lookup[k])

# modal = 'will', highest relative frequency difference across gutenberg corpus: 0.0046345
word = 'will'
poems = nltk.Text(gut.words('blake-poems.txt'))
caesar = nltk.Text(gut.words('shakespeare-caesar.txt'))

books = [poems, caesar]
for book in books:
    print '>>> Concordance for "{0}" in {1}'.format(word, book)
    book.concordance(word, lines=10)

print
#can't really modularize since can't capture output of .similar() w/o redirecting stdout... not worth the trouble
print '>>> words in {0} with similar context to "{1}"'.format(poems, word)
poems.similar(word)
sim = 'have'
print '>>> context of word in {0} with similar context to "{1}"'.format(poems, sim)
poems.common_contexts([word, sim])

print
print '>>> words in {0} with similar context to "{1}"'.format(caesar, word)
caesar.similar(word)
sim = 'shall'
print '>>> context of word in {0} with similar context to "{1}"'.format(caesar, sim)
caesar.common_contexts([word, sim])

# modal = 'could', 2nd highest relative frequency difference across gutenberg corpus: 0.00435946
(0.004359459937684319, u'bible-kjv.txt', u'austen-persuasion.txt')

word = 'could'
bible = nltk.Text(gut.words('bible-kjv.txt'))
persuasion = nltk.Text(gut.words('austen-persuasion.txt'))

books = [bible, persuasion]
for book in books:
    print '>>> Concordance for "{0}" in {1}'.format(word, book)
    book.concordance(word, lines=10)

print
#can't really modularize since can't capture output of .similar() w/o redirecting stdout... not worth the trouble
print '>>> words in {0} with similar context to "{1}"'.format(bible, word)
bible.similar(word)
sim = 'have'
print '>>> context of word in {0} with similar context to "{1}"'.format(bible, sim)
bible.common_contexts([word, sim])

print
print '>>> words in {0} with similar context to "{1}"'.format(persuasion, word)
persuasion.similar(word)
sim = 'would'
print '>>> context of word in {0} with similar context to "{1}"'.format(persuasion, sim)
persuasion.common_contexts([word, sim])
