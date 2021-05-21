import re
import gzip
import sys


doc = sys.argv[1]
begin = 0
size = 4
docid = 0
rev_ind = dict()
docid_dict = dict()
data = gzip.open(doc, 'rb').read()
rev_ind_file = open('rev_ind.txt', 'w')
urls = open('urls.txt', 'w')

while begin < len(data):
    text_size = int.from_bytes(data[begin:begin + size], 'little')
    offset = begin + size + 1
    url_size = int.from_bytes(data[offset:offset + 1], 'little')
    offset += 1

    url = data[offset:url_size + offset].decode('utf_8')
    offset += url_size + 3
    text = data[offset:text_size + begin + size].decode('utf-8', 'ignore')
    if text:
        text = re.findall(r'\w+', str(text.lower()))
        for word in set(text):
            rev_ind.setdefault(word, [])
            rev_ind[word].append(docid)

    begin += text_size + size
    docid_dict[docid] = url
    docid += 1

for word in rev_ind:
    print(word, file=rev_ind_file)
    print(*rev_ind[word], file=rev_ind_file)
for docid in docid_dict:
    print(docid, file=urls)
    print(docid_dict[docid], file=urls)
