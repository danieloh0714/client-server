import socket

from re import fullmatch
from sys import argv, exit


def get_parsed_url() -> tuple:
    args = argv
    # program should take exactly one parameter
    if len(args) != 2:
        exit(1)
    url = args[1]
    # input url must start with 'http://'
    if not fullmatch("http://.*", url):
        exit(1)
    return url, url, url


def get_content_info(s, data: list) -> str:
    ans = []
    while True:
        buf = s.recv(1)
        buf_decoded = buf.decode()
        if buf_decoded == "\r":
            data.append("\r")
            break
        ans.append(buf_decoded)
        data.append(buf_decoded)
    return "".join(ans)


def make_get_request(url_parts: tuple) -> bool:
    url_host, url_page, url_port = url_parts
    # example values for now
    url_host = "insecure.stevetarzia.com"
    url_page = "/basic.html"
    url_port = 80

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((url_host, url_port))
    req = f"GET {url_page} HTTP/1.0\r\nHost: {url_host}\r\n\r\n"
    s.sendall(req.encode())

    content_length = 0
    content_type = ""

    data = []
    is_body_start = False
    count = 0
    while True:
        buf = s.recv(1)  # receive one byte at a time
        if not buf:
            break
        data.append(buf.decode())

        # if last four chars are two returns, then body begins
        if "".join(data[-4:]) == "\r\n\r\n":
            is_body_start = True

        # if body started and content length specified, break when content length bytes are received
        if is_body_start and content_length:
            count += 1
            if count == content_length:
                break

        # if body not started, check for content length and content type info
        if (
            not is_body_start
            and not content_length
            and "".join(data[-16:]) == "Content-Length: "
        ):
            content_length = int(get_content_info(s, data))
        if (
            not is_body_start
            and not content_type
            and "".join(data[-14:]) == "Content-Type: "
        ):
            content_type = get_content_info(s, data)
            if content_type[:9] != "text/html":
                exit(1)

    print("".join(data))
    return True


def main():
    url_parts = get_parsed_url()
    if not make_get_request(url_parts):
        exit(1)
    exit()


if __name__ == "__main__":
    main()
