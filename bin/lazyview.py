


class LazyView:

    def __init__(self, iterableFn):
        self.iterableFn = iterableFn
        self.memoized = None

    def filter(self, fn):
        return LazyView(lambda: filter(fn, self.iterableFn()))

    def map(self, fn):
        return LazyView(lambda: map(fn, self.iterableFn()))

    def flatmap(self, fn):
        return LazyView(lambda: map(fn, self.iterableFn()))

    def to_list(self) -> list:
        if self.memoized is None:
            self.memoized = list(self.iterableFn())
        return self.memoized

    def is_empty(self) -> bool:
        return len(self.to_list()) == 0

    def non_empty(self) -> bool:
        return not self.is_empty()

    def foreach(self, fn) -> None:
        for x in self.to_list():
            fn(x)

    def mk_str(self, sep) -> str:
        return sep.join(self.map(str).to_list())

    def __len__(self) -> int:
        return len(self.to_list())

    def __getitem__(self, index: int):
        return self.to_list()[index]

def from_iter(iterable) -> list:
    return LazyView(lambda: iterable)
