from json import dumps
from socket import socket, AF_INET, SOCK_STREAM
from utils import get_port_input, status_code_messages


def get_operands_product(operands: list) -> float | str:
    ans = 1
    for operand in operands:
        ans *= float(operand)
    if ans == float("inf"):
        return "inf"
    if ans == float("-inf"):
        return "-inf"
    return ans


def parse_operands(params: list) -> list:
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


def send_res(conn: socket, params: list, status_code: int) -> None:
    res = [f"HTTP/1.0 {status_code} {status_code_messages[status_code]}\r\n"]
    if status_code == 200:
        operands = parse_operands(params)
        if not operands:
            conn.sendall(f"HTTP/1.0 {400} {status_code_messages[400]}\r\n".encode())
            return

        res.append(f"Connection: close\r\n")
        res.append(f"Content-Type: application/json\r\n")

        res.append("\r\n")
        res.append(
            dumps(
                {
                    "operation": "product",
                    "operands": operands,
                    "result": get_operands_product(operands),
                }
            )
        )
        res.append("\r\n")
    conn.sendall("".join(res).encode())


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
