import importlib_resources
import sys

def func():
    sys.path.insert(0, '..')
    text: str = importlib_resources.files("shared_resources/resources/connectives/connectives_de.txt").read_text()

if __name__ == "__main__":
    func()