import socket


def get_ip():  # sourcery skip: raise-specific-error
    """
    This function is used to get the IP address of the device running the program.

    :return: The IP address of the device running the program.
    """
    try:
        return (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [
            [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
             [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
    except:
        raise Exception("Unable to get IP address")
