class BinarySearchList(list):
    def __init__(self, criteria, *args, **kwargs):
        super(BinarySearchList, self).__init__(*args, **kwargs)
        self.criteria = criteria

    def binary_search(self, value, start, end):
        if end - start <= 1:
            return start
        ind = (start + end) // 2
        ind_el = self.criteria(self[ind])
        if ind_el == value:
            return ind
        if ind_el > value:
            return self.binary_search(value=value,
                                      start=start,
                                      end=ind)
        return self.binary_search(value, ind, end)

    def append(self, __object) -> None:
        ind = self.binary_search(self.criteria(__object), 0, len(self))
        self.insert(ind, __object)
