def unpackData(data: str) -> str and list:
    """
    function gets data and unpacks it based on known opcodes and params protocols
    :param data: data to unpack
    :return: the opcode of the data and a list of all it's params
    """

    opcode = data[:2]
    params = []

    if opcode == "00" or opcode == "01":
        username_len = int(data[2])
        params.append(data[3:3 + username_len])
        params.append(data[3 + username_len:])
    elif opcode == "02" or opcode == "04" or opcode == "06":
        params.append(data[2:])

    return opcode, params


def pack_login_ans(authorized: bool) -> str:
    """
    function packs login ans based on the protocol
    :param authorized: True if login was authorized False otherwise
    :return: packed data based on protocol
    """
    return "000" if authorized else "001"


def pack_signup_ans(authorized: bool) -> str:
    """
    function packs signup ans based on the protocol
    :param authorized: True if signup was authorized False otherwise
    :return: packed data based on protocol
    """
    return "010" if authorized else "011"


def pack_typeuser_ans(authorized: bool) -> str:
    """
    function packs type user ans based on the protocol
    :param authorized: True if type user was authorized False otherwise
    :return: packed data based on protocol
    """
    return "020" if authorized else "021"


def pack_getcode_ans(authorized: bool, code: str) -> str:
    """
    function packs get code request ans based on the protocol
    :param authorized: True if get code req was authorized False otherwise
    :param code: code to send
    :return: packed data based on protocol
    """
    return "03" + code if authorized else "031"


def pack_expired_code() -> str:
    """
    function packs expired code msg based on the protocol
    :return: packed data based on protocol
    """
    return "032"


def pack_code_ans(authorized: bool) -> str:
    """
    function packs code given ans based on the protocol
    :param authorized: True if code gotten was authorized False otherwise
    :return: packed data based on protocol
    """
    return "040" if authorized else "041"


def pack_con_data(ip: str) -> str:
    """
    function packs connection data msg based on the protocol
    :param ip: ip to send
    :return: packed data based on protocol
    """
    return "05" + ip
