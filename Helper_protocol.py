def unpackData(data: str) -> str and list:
    """
    function gets data and unpacks it based on known opcodes and params protocols
    :param data: data to unpack
    :return: the opcode of the data and a list of all it's params
    """

    opcode = data[:2]
    params = []

    img_params = data[2:]
    new_str = ""
    for i in range(1, len(img_params) + 1):
        new_str += img_params[i - 1]
        if i % 4 == 0:
            params.append(new_str)
            new_str = ""

    return opcode, params


def pack_key_click(unicode_key: str) -> str:
    """
    function packs unicode key based on the protocol
    :param unicode_key: unicode_key clicked
    :return: packed data based on protocol
    """
    return "01" + unicode_key


def pack_key_release(unicode_key: str) -> str:
    """
    function packs unicode key based on the protocol
    :param unicode_key: unicode_key clicked
    :return: packed data based on protocol
    """
    return "02" + unicode_key
