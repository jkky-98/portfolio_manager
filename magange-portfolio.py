class ManagePortfolio:
    def __init__(self):
        self._cate = None

    def add(self, port):
        port._next = self._cate
        self._cate = port

    def check(self, name):
        self._cate = name
        return self._cate

    def remove(self):
        assert self._cate != None
        _port = self._cate
        self._cate = _port._next
        _port._next = None
        return _port

    def check_list(self, others):
        if self._cate == None:
            return self._cate
        else:
            _check = self._cate
            self._cate = _check._next
            if self._cate != others:
                return others
            else:
                return self._cate

    def change(self, name, old):
        self._cate = old
        self._cate = name
        return self._cate


class Port:
    def __init__(self, category):
        self._category = category
        self._portfolio = ManagePortfolio()
        self._next = None

    def lists(self):
        return self._portfolio

    def category(self):
        return self._category

    def next(self):
        return self._next


def main():
    command = input("Put the command\n")
    P = ManagePortfolio()
    if command == "추가":
        port = input("Please put the name of the category that you want to add\n")
        if P.check(port) != P.check_list(port):
            P.add(port)

    elif command == "삭제":
        port2 = input("Please put the name of the category that you want to remove\n")
        if P.check(port2) == P.check_list(port2):
            P.remove()

    elif command == "변경":
        old_name = input("Please put the name of the portfolio that you want to change.\n")
        port3 = input("Please put the new name.\n")
        P.change(port3, old_name)


main()
