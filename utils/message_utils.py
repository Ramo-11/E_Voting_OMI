def construct_byte_message(base_message):
    message_len = len(base_message)
    message = message_len.to_bytes(4, "big") + base_message
    return message