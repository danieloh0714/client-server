from os.path import getsize, isfile
from socket import socket, AF_INET, SOCK_STREAM
from sys import argv, exit, stderr


status_code_messages = {
    200: "OK",
    403: "Forbidden",
    404: "Not Found",
}


def get_port_input() -> int:
    # program should take exactly one parameter
    if len(argv) != 2:
        exit(1)
    if not argv[1].isdigit():
        stderr.write("Port number must be a natural number.\n")
        exit(1)
    port = int(argv[1])
    if port < 1024:
        stderr.write("Port number must be >= 1024.\n")
        exit(1)
    return port


def send_res(conn: socket, page: str, status_code: int) -> None:
    res = [f"HTTP/1.0 {status_code} {status_code_messages[status_code]}\r\n"]
    if status_code == 200:
        res.append(f"Content-Length: {getsize(page)}\r\n")
        res.append(f"Connection: close\r\n")
        res.append(f"Content-Type: text/html\r\n")

        res.append("\r\n")
        res.append(open(page, mode="r").read())

    for c in "".join(res):
        conn.sendall(c.encode())


def handle_get_request(conn: socket, page: str) -> None:
    if not isfile(page):
        send_res(conn, page, status_code=404)
    elif page.split(".")[1] not in ["htm", "html"]:
        send_res(conn, page, status_code=403)
    else:
        send_res(conn, page, status_code=200)


def handle_client(conn: socket) -> None:
    data = []
    while True:
        buf = conn.recv(1)
        if buf.decode() == "\r":
            break
        data.append(buf.decode())
    page = "".join(data).split(" ")[1][1:]
    handle_get_request(conn=conn, page=page if page else "index.html")
    conn.close()


def run_server(port: int) -> None:
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(("", port))
    s.listen()
    while True:
        handle_client(conn=s.accept()[0])


def main() -> None:
    run_server(port=get_port_input())


if __name__ == "__main__":
    main()
