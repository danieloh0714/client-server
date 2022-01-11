from re import fullmatch
from sys import argv, exit


def get_page_url() -> str:
    args = argv
    # program should take exactly one parameter
    if len(args) != 2:
        exit(1)
    url = args[1]
    # input url must start with 'http://'
    if not fullmatch("http://.*", url):
        exit(1)
    return url


def make_get_request(url: str) -> bool:
    print(url)
    return True


def main():
    url = get_page_url()
    if not make_get_request(url):
        exit(1)
    exit()


if __name__ == "__main__":
    main()
