import sys


class RequestTreeLeaf:
    def __init__(self, op_type, value, left=None, right=None):
        self.op_type = op_type
        self.value = value
        self.left = left
        self.right = right
        if self.op_type == 'op' and self.value == '!':
            self.docid = -1
            self.last_docid = -1
        elif self.value == '|':
            self.leftf = False
            self.rightf = False
        elif self.value == '&':
            self.last_docid = -1
        self.last_docid_ind = 0
        if op_type == 'term':
            self.docids = rev_ind[value]
            self.omega_id = self.docids[len(self.docids) - 1]
        else:
            self.docids = []
            self.omega_id = doc_num
            if self.value == '|':
                self.omega_id = max(self.left.omega_id, self.right.omega_id)

    def __goto_next__(self):
        self.last_docid_ind += self.last_docid_ind != len(self.docids) - 1

    def goto(self, docid):
        if self.op_type == 'term':
            while self.last_docid_ind != len(self.docids) - 1 and self.docids[self.last_docid_ind] < docid:
                self.__goto_next__()
        else:
            if self.value == '|':
                self.left.goto(docid)
                self.right.goto(docid)
            elif self.value == '&':
                self.left.goto(docid)
                self.right.goto(docid)
            else:
                if docid >= self.docid:
                    self.left.goto(docid)
                    self.docid = docid
                    left = self.left.evaluate()
                    while left != self.left.omega_id and self.docid < self.omega_id and left == self.docid:
                        self.left.goto(self.docid + 1)
                        self.docid += 1
                        left = self.left.evaluate()
                    if left == self.left.omega_id == self.docid:
                        self.docid += 1
                    if self.docid == self.omega_id:
                        self.omega_id = self.last_docid

    def evaluate(self):
        if self.op_type == 'term':
            return self.docids[self.last_docid_ind]

        if self.value == '|':
            left = self.left.evaluate()
            right = self.right.evaluate()
            if left is None:
                self.leftf = True
            if right is None:
                self.rightf = True
            if self.leftf and self.rightf:
                return None
            if self.leftf:
                return right
            if self.rightf:
                return left
            if left <= right and left == self.left.omega_id and not self.leftf:
                self.leftf = True
                return left
            if right <= left and right == self.right.omega_id and not self.rightf:
                self.rightf = True
                return right
            if right <= left:
                return right
            if left <= right:
                return left

        if self.value == '&':
            left = self.left.evaluate()
            right = self.right.evaluate()
            if left is None or right is None:
                return None
            while left != self.left.omega_id and right != self.right.omega_id and left != right:
                max_docid = max(left, right)
                self.left.goto(max_docid)
                self.right.goto(max_docid)
                left = self.left.evaluate()
                right = self.right.evaluate()
            if right == self.right.omega_id or left == self.left.omega_id:
                if right <= left == self.left.omega_id:
                    self.right.goto(self.left.omega_id)
                elif left <= right == self.right.omega_id:
                    self.left.goto(self.right.omega_id)
                left = self.left.evaluate()
                right = self.right.evaluate()
                if left == right:
                    self.omega_id = left
                    return self.omega_id
                self.omega_id = self.last_docid
                return None
            self.last_docid = left
            return left

        if self.value == '!':
            if self.docid == self.omega_id:
                return None
            self.last_docid = self.docid
            return self.docid


def brackets(inp, i):
    count = 1
    i -= 1
    while i >= -len(inp) and count > 0:
        if inp[i] == '(':
            count -= 1
        elif inp[i] == ')':
            count += 1
        i -= 1
    return i


def parser(inp):
    inp = inp.strip().lower()
    i = -1
    if inp[i] == ')':
        last_pr = brackets(inp, i)
        i = last_pr
    if i == -len(inp) - 1:
        return parser(inp[1:-1])

    if inp.find('|') == -1 and inp.find('&') == -1 and inp.find('!') == -1:
        term = []
        while i >= -len(inp) and inp[i].islower():
            term.append(inp[i])
            i -= 1
        return RequestTreeLeaf('term', ''.join(term[::-1]))

    while i >= -len(inp) and inp[i] != '|' and inp[i] != '&' and inp[i] != '!':
        i -= 1

    if inp[i] == '|':
        return RequestTreeLeaf('op', '|', parser(inp[:i]), parser(inp[i + 1:]))

    if inp[i] == '&':
        last_pr = i
        while i >= -len(inp) and inp[i] != '|':
            i -= 1
            if i >= -len(inp) and inp[i] == ')':
                i = brackets(inp, i)
        if i >= -len(inp) and inp[i] == '|':
            return RequestTreeLeaf('op', '|', parser(inp[:i]), parser(inp[i + 1:]))

        return RequestTreeLeaf('op', '&', parser(inp[:last_pr]), parser(inp[last_pr + 1:]))

    if inp[i] == '!':
        last_pr = i
        while i >= -len(inp) and inp[i] != '|':
            i -= 1
            if i >= -len(inp) and inp[i] == ')':
                i = brackets(inp, i)
        if i >= -len(inp) and inp[i] == '|':
            return RequestTreeLeaf('op', '|', parser(inp[:i]), parser(inp[i + 1:]))

        i = last_pr
        while i >= -len(inp) and inp[i] != '&':
            i -= 1
            if i >= -len(inp) and inp[i] == ')':
                i = brackets(inp, i)
        if i >= -len(inp) and inp[i] == '&':
            return RequestTreeLeaf('op', '&', parser(inp[:i]), parser(inp[i + 1:]))

        return RequestTreeLeaf('op', '!', parser(inp[last_pr + 1:]))


def process(request):
    root = parser(request)
    alpha_id = 0
    root.goto(alpha_id)
    cur = root.evaluate()
    result = []
    if cur is not None:
        result.append(cur)
    while cur is not None and cur < root.omega_id:
        root.goto(cur + 1)
        cur = root.evaluate()
        if cur is not None:
            result.append(cur)
    return result


rev_ind_file = open('rev_ind.txt', 'r')
urls = open('urls.txt', 'r')
rev_ind = dict()
docid_dict = dict()
for line in rev_ind_file:
    rev_ind[line.strip()] = list(map(int, rev_ind_file.readline().split()))
for line in urls:
    docid_dict[int(line)] = urls.readline().strip()
doc_num = len(docid_dict) - 1
requests = []
for line in sys.stdin:
    if not line:
        break
    requests.append(line.strip())
for request in requests:
    res = process(request)
    print(request)
    print(len(res))
    for ind in res:
        print(docid_dict[ind])
