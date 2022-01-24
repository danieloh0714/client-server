from os.path import isfile
from socket import socket, AF_INET, SOCK_STREAM
from utils import get_port_input, status_code_msgs


def send_res(conn: socket, page: str, status_code: int) -> None:
    conn.sendall(
        f"HTTP/1.0 {status_code} {status_code_msgs[status_code]}\r\nConnection: close\r\n".encode()
    )
    if status_code == 200:
        f = open(page, mode="r").read()
        conn.sendall(
            f"Content-Length: {len(f)}\r\nContent-Type: text/html\r\n\r\n".encode()
        )

        for c in f:
            conn.sendall(c.encode())


def handle_get_request(conn: socket, page: str) -> None:
    if not isfile(page):
        send_res(conn, page, status_code=404)
    elif page.split(".")[1] not in ["htm", "html"]:
        send_res(conn, page, status_code=403)
    else:
        send_res(conn, page, status_code=200)


def handle_client(conn: socket) -> None:
    try:
        data = []
        while True:
            buf = conn.recv(1)
            if buf.decode() == "\r":
                break
            data.append(buf.decode())
        page = "".join(data).split(" ")[1][1:]
        handle_get_request(conn=conn, page=page if page else "index.html")
    finally:
        conn.close()


def run_server(port: int) -> None:
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(("", port))
    sock.listen()
    while True:
        handle_client(conn=sock.accept()[0])


def main() -> None:
    run_server(port=get_port_input())


if __name__ == "__main__":
    main()
