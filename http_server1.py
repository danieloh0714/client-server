from os.path import isfile
from socket import socket, AF_INET, SOCK_STREAM
from sys import argv, exit, stderr


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


def send_res(conn, status_code: int) -> None:
    print(status_code)
    res = "Thank you!"
    conn.sendall(res.encode())


def handle_get_request(conn, page: str) -> None:
    print(page)
    if not isfile(page):
        send_res(conn, status_code=404)
    elif page.split(".")[1] not in ["htm", "html"]:
        send_res(conn, status_code=403)
    else:
        send_res(conn, status_code=200)


def handle_client(conn) -> None:
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
        conn, _ = s.accept()
        handle_client(conn)


def main() -> None:
    run_server(port=get_port_input())


if __name__ == "__main__":
    main()
