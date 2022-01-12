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


def handle_client(conn) -> None:
    data = []
    while True:
        buf = conn.recv(1)
        data.append(buf.decode())
        if "".join(data[-4:]) == "\r\n\r\n":
            break
    print("".join(data))
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
