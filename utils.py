from sys import argv, exit, stderr


status_code_messages = {
    200: "OK",
    403: "Forbidden",
    404: "Not Found",
}


def get_input() -> str:
    # program should take exactly one parameter
    if len(argv) != 2:
        exit(1)
    return argv[1]


def get_port_input() -> int:
    inp = get_input()
    if not inp.isdigit():
        stderr.write("Port number must be a natural number.\n")
        exit(1)
    port = int(inp)
    if port < 1024:
        stderr.write("Port number must be >= 1024.\n")
        exit(1)
    return port
