def unpackData(data: str) -> str and list:
    """
    function gets data and unpacks it based on known opcodes and params protocols
    :param data: data to unpack
    :return: the opcode of the data and a list of all it's params
    """

    opcode = data[:2]
    params = []

    if opcode == "00" or opcode == "01" or opcode == "02" or opcode == "04":
        # 0 if authorized 1 if not
        params.append(True) if data[2:] == "0" else params.append(False)
    elif opcode == "03" or opcode == "05":
        params.append(data[2:])

    return opcode, params


def pack_mac_addr(macAddr: str) -> str:
    """
    function packs mac address based on the protocol
    :param macAddr: computer mac address to send
    :return: packed data based on protocol
    """
    return "06" + macAddr


def pack_login_info(username: str, password: str) -> str:
    """
    function packs login info
    :param username: username of user to send
    :param password: password of user to send
    :return: packed data based on protocol
    """
    return "00" + str(len(username)) + username + password


def pack_signup_info(username: str, password: str) -> str:
    """
    function packs signup info
    :param username: username of user to send
    :param password: password of user to send
    :return: packed data based on protocol
    """
    return "01" + str(len(username)) + username + password


def pack_type_user(typeUser: str) -> str:
    """
    function packs user type decided based on the protocol
    :param typeUser: user type wanted, 0-Helper 1-AssistanceSeeker
    :return: packed data based on protocol
    """
    return "02" + typeUser


def pack_code(code: str) -> str:
    """
    function packs code entered based on the protocol
    :param code: code entered by user
    :return: packed data based on protocol
    """
    return "04" + code
