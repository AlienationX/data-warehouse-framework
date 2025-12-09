import fire


class Calculator(object):
    """A simple calculator class."""

    def add(self, a, b):
        return a + b

    def double(self, number):
        return 2 * number


if __name__ == "__main__":
    fire.Fire(Calculator)
