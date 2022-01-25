from json import dumps
from socket import socket, AF_INET, SOCK_STREAM
from utils import get_port_input, status_code_msgs


def parse_params(params: list) -> list:
    ops = []
    for param in params:
        try:
            _, op = param.split("=")
            if not op.lstrip("-").replace(".", "", 1).isdigit():
                return []
            ops.append(float(op))
        except:
            return []
    return ops


def get_ops_prod(ops: list) -> float | str:
    ans = 1
    for op in ops:
        ans *= float(op)
    if ans == float("inf"):
        return "inf"
    if ans == float("-inf"):
        return "-inf"
    return ans


def send_res(conn: socket, params: list, status_code: int) -> None:
    ops = parse_params(params)
    real_status_code = 400 if (status_code == 200 and not ops) else status_code
    conn.sendall(
        f"HTTP/1.0 {real_status_code} {status_code_msgs[real_status_code]}\r\nConnection: close\r\n".encode()
    )
    if real_status_code == 200:
        conn.sendall(f"Content-Type: application/json\r\n\r\n".encode())
        body = dumps(
            {
                "operation": "product",
                "operands": ops,
                "result": get_ops_prod(ops),
            }
        )
        conn.sendall(f"{body}\r\n".encode())


def handle_get_req(conn: socket, query: str) -> None:
    if query[:7] != "product":
        send_res(conn, [], 404)
    else:
        send_res(conn, query[8:].split("&"), 200)


def handle_client(conn: socket) -> None:
    try:
        data = []
        while True:
            buf = conn.recv(1)
            if buf.decode() == "\r":
                break
            data.append(buf.decode())
        query = "".join(data).split(" ")[1][1:]
        handle_get_req(conn=conn, query=query)
    finally:
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
