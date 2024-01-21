def unpackData(data: str) -> tuple:
    """
    function gets data and unpacks it based on known opcodes and params protocols
    :param data: data to unpack
    :return: the opcode of the data and the param of the opcode
    """

    return data[:2], data[2:]


def pack_part_image(left: str, top: str, right: str, bottom: str, img_data_size) -> str:
    """
    function packs part image header
    :param left: left value of image place
    :param top: top value of image place
    :param right: right value of image place
    :param bottom: bottom value of image place
    :param img_data_size: length of data of img
    :return: packed string of part image header
    """
    return "01" + left + top + right + bottom + img_data_size


def pack_full_image(img_data_size) -> str:
    """
    function packs full image header
    :param img_data_size: length of data of img
    :return: packed string of full image header
    """
    return "02" + img_data_size
