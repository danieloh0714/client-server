from re import findall
from socket import socket, AF_INET, SOCK_STREAM
from sys import argv, exit, stderr, stdout


REDIRECT_LIMIT = 10


def get_url_input() -> str:
    # program should take exactly one parameter
    if len(argv) != 2:
        exit(1)
    return argv[1]


def get_url_parts(url: str) -> tuple:
    # input url must start with 'http://'
    if url[:5] == "https":
        stderr.write("Program does not support HTTPS protocol.\n")
        exit(1)
    if url[:7] != "http://":
        exit(1)

    host_and_port, page = findall("http://([^/]+)(/.+)?", url)[0]
    host, port = findall("([^:]+):?(.+)?", host_and_port)[0]

    return host, 80 if port == "" else int(port), "/" if page == "" else page


def get_header_info(s: socket, data: list) -> str:
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


def make_get_request(input_url: str) -> bool:
    url = input_url
    data = []
    status_code = 0
    for attempt in range(REDIRECT_LIMIT + 1):
        if data:
            break

        if attempt > 0:
            stderr.write(f"Redirected to: {url}\n")

        host, port, page = get_url_parts(url)

        s = socket(AF_INET, SOCK_STREAM)
        s.connect((host, port))
        req = f"GET {page} HTTP/1.0\r\nHost: {host}\r\n\r\n"
        s.sendall(req.encode())

        content_len = 0
        content_type = ""
        is_body = False
        while True:
            # receive one byte at a time; break when no more
            buf = s.recv(1)
            if not buf:
                s.close()
                break
            data.append(buf.decode())

            # get response status code
            if len(data) == 12:
                status_code = int("".join(data[-3:]))

            # if two consecutive returns, then body starts
            if "".join(data[-4:]) == "\r\n\r\n":
                is_body = True

            # if body started and content length specified, break when content length bytes are received
            if is_body and content_len:
                content_len -= 1
                if content_len == 0:
                    s.close()
                    break

            # if body not started, check for header info
            if not is_body:
                if not content_len and "".join(data[-16:]) == "Content-Length: ":
                    content_len = int(get_header_info(s, data))
                if not content_type and "".join(data[-14:]) == "Content-Type: ":
                    content_type = get_header_info(s, data)
                    if content_type[:9] != "text/html":
                        return False
                if status_code in [301, 302] and "".join(data[-10:]) == "Location: ":
                    url = get_header_info(s, data)
                    data = []
                    status_code = 0
                    s.close()
                    break

    # redirect limit reached
    if not data:
        return False

    stdout.write(f"{''.join(data)}\n")
    return status_code < 400


def main() -> None:
    if not make_get_request(get_url_input()):
        exit(1)
    exit(0)


if __name__ == "__main__":
    main()
