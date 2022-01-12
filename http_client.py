from re import fullmatch
from socket import socket, AF_INET, SOCK_STREAM
from sys import argv, exit, stderr, stdout


def get_parsed_url() -> tuple:
    # program should take exactly one parameter
    if len(argv) != 2:
        exit(1)
    url = argv[1]

    # input url must start with 'http://'
    if url[:5] == "https":
        stderr.write("Program does not support HTTPS protocol.")
        exit(1)
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

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((url_host, url_port))
    req = f"GET {url_page} HTTP/1.0\r\nHost: {url_host}\r\n\r\n"
    s.sendall(req.encode())

    cont_len = 0
    cont_type = ""

    data = []
    is_body = False
    while True:
        buf = s.recv(1)  # receive one byte at a time
        if not buf:
            break
        data += buf.decode()

        # if two consecutive returns, then body starts
        if "".join(data[-4:]) == "\r\n\r\n":
            is_body = True

        # if body started and content length specified, break when content length bytes are received
        if is_body and cont_len:
            cont_len -= 1
            if cont_len == 0:
                break

        # if body not started, check for content length and content type info
        if not is_body and not cont_len and "".join(data[-16:]) == "Content-Length: ":
            cont_len = int(get_content_info(s, data))
        if not is_body and not cont_type and "".join(data[-14:]) == "Content-Type: ":
            cont_type = get_content_info(s, data)
            if cont_type[:9] != "text/html":
                return False

    stdout.write("".join(data))
    return True


def main():
    url_parts = get_parsed_url()
    if not make_get_request(url_parts):
        exit(1)
    exit(0)


if __name__ == "__main__":
    main()
