def unpackData(data: str) -> str and list:
    """
    function gets data and unpacks it based on known opcodes and params protocols
    :param data: data to unpack
    :return: the opcode of the data and a list of all it's params
    """

    opcode = data[:2]
    params = []
    if opcode == "01":
        params.append(data[2:6])
        params.append(data[6:10])
        params.append(data[10:14])
        params.append(data[14:18])
        params.append(data[18:])
    elif opcode == "02":
        params.append(data[2:])

    return opcode, params


def pack_key_click(unicode_key: str) -> str:
    """
    function packs unicode key based on the protocol
    :param unicode_key: unicode_key clicked
    :return: packed data based on protocol
    """
    return "01" + unicode_key.zfill(7)


def pack_key_release(unicode_key: str) -> str:
    """
    function packs unicode key based on the protocol
    :param unicode_key: unicode_key clicked
    :return: packed data based on protocol
    """
    return "02" + unicode_key.zfill(7)
