#order the counting results by the decreasing count. 
#Present the portion of your final result which does not contain so called stop words (the, a, and, or, ...) in your report.
#Submit top 200 words in separate .txt file with your report.


from nltk.corpus import stopwords
wds = stopwords.words('english')
stop_words = ''
stop_words = [stop_words +  str(wd)  for wd in wds]


import os
import operator

stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']

word_counts = []
# found_stop_words as a sanity check, inspect contents while debugging to make sure 
#   nothing unusual - looks like 126 of 127 stop words were found in the file
found_stop_words = set()
file_path = os.path.join(os.getcwd(), 'data/counter_contents.txt')
for line in open(file_path):
    #file is tab separated, 50094 lines with 50094 tabs, split into two 
    word, count = line.strip().split('\t')
    if word.lower() in stop_words:
        found_stop_words.add(word)
        continue
    word_counts.append((word, int(count)))
    


sorted_word_counts = sorted(word_counts, key=operator.itemgetter(1), reverse = True)
output_word_counts = ['{0}\t{1}\r\n'.format(word, count) for (word, count) in sorted_word_counts[:200]]
with open('sorted_word_counts.txt', 'w') as f:
    f.writelines(output_word_counts)


