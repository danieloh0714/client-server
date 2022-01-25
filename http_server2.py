from os.path import isfile
from queue import Empty, Queue
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from utils import get_port_input, status_code_msgs


def send_res(page: str, status_code: int) -> str:
    res = []
    res.append(
        f"HTTP/1.0 {status_code} {status_code_msgs[status_code]}\r\nConnection: close\r\n"
    )
    if status_code == 200:
        f = open(page, mode="r").read()
        res.append(f"Content-Length: {len(f)}\r\nContent-Type: text/html\r\n\r\n{f}")
    return "".join(res)


def handle_get_request(page: str) -> str:
    if not isfile(page):
        return send_res(page, status_code=404)
    if page.split(".")[1] not in ["htm", "html"]:
        return send_res(page, status_code=403)
    return send_res(page, status_code=200)


def run_server(port: int) -> None:
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setblocking(False)
    sock.bind(("", port))
    sock.listen(5)
    inputs, outputs = [sock], []
    message_queues = {}
    while inputs:
        readable, writable, exceptional = select(inputs, outputs, inputs)
        for s in readable:
            if s is sock:
                conn = s.accept()[0]
                conn.setblocking(False)
                inputs.append(conn)
                message_queues[conn] = Queue()
            else:
                buf = s.recv(1024)
                if buf:
                    message_queues[s].put(buf.decode())
                    if s not in outputs:
                        outputs.append(s)
                else:
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    del message_queues[s]
        for s in writable:
            try:
                page = message_queues[s].get_nowait().split(" ")[1][1:]
            except Empty:
                outputs.remove(s)
            else:
                s.sendall(
                    handle_get_request(page=page if page else "index.html").encode()
                )
        for s in exceptional:
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            del message_queues[s]


def main() -> None:
    run_server(port=get_port_input())


if __name__ == "__main__":
    main()
