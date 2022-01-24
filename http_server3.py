from json import dumps
from socket import socket, AF_INET, SOCK_STREAM
from utils import get_port_input, status_code_msgs


def parse_params(params: list) -> list:
    operands = []
    for param in params:
        try:
            _, operand = param.split("=")
            if not operand.lstrip("-").replace(".", "", 1).isdigit():
                return []
            operands.append(float(operand))
        except:
            return []
    return operands


def get_operands_product(operands: list) -> float | str:
    ans = 1
    for operand in operands:
        ans *= float(operand)
    if ans == float("inf"):
        return "inf"
    if ans == float("-inf"):
        return "-inf"
    return ans


def send_res(conn: socket, params: list, status_code: int) -> None:
    operands = parse_params(params)
    real_status_code = 400 if (status_code == 200 and not operands) else status_code
    conn.sendall(
        f"HTTP/1.0 {real_status_code} {status_code_msgs[real_status_code]}\r\nConnection: close\r\n".encode()
    )
    if real_status_code == 200:
        conn.sendall(f"Content-Type: application/json\r\n\r\n".encode())
        body = dumps(
            {
                "operation": "product",
                "operands": operands,
                "result": get_operands_product(operands),
            }
        )
        conn.sendall(f"{body}\r\n".encode())


def handle_get_request(conn: socket, query: str) -> None:
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
        handle_get_request(conn=conn, query=query)
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
