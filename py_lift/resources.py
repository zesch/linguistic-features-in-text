import importlib_resources
import sys

def func():
    sys.path.insert(0, '..')
    my_resources = importlib_resources.files("shared_resources")

    text = (my_resources / "connectives/connectives_de.txt").read_text()
    print(text)

if __name__ == "__main__":
    func()