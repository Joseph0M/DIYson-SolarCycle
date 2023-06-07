def serialize(multi: bool, function_name, *args):
    serialized_data = []
    if not multi:
        serialized_data.append(1)
    serialized_data.extend(ord(char) for char in function_name)
    serialized_data.append(0)  # Data break
    for arg in args:
        if isinstance(arg, str):
            serialized_data.extend(ord(char) for char in arg)
        elif isinstance(arg, float):
            serialized_data.extend(ord(char) for char in str(arg))
        elif isinstance(arg, int):
            serialized_data.extend(ord(char) for char in str(arg))
        elif isinstance(arg, bool):
            serialized_data.extend([ord('T' if arg else 'F')])
        serialized_data.append(0)  # Data break
    if not multi:
        serialized_data.append(4)
    return serialized_data
def deserialize(serialized_data):
    if serialized_data[0] == 1:
        serialized_data = serialized_data[1:]
    if serialized_data[-1] == 4:
        serialized_data = serialized_data[:-1]
    function_name = ''
    args = []
    current_arg = ''
    array = []
    multi_func = False
    for ascii_int in serialized_data:
        if ascii_int == 0:
            if not function_name:
                function_name = current_arg
            else:
                args.append(current_arg)
            current_arg = ''
        elif ascii_int == 23:
            multi_func = True
            array.append([function_name, args])
            function_name = ''
            args = []
            current_arg = ''
        else:
            current_arg += chr(ascii_int)
    array.append([function_name, args])
    deserialized_array = []
    for function in array:
        deserialized_args = []
        for arg in function[1]:
            if arg.isdigit():
                deserialized_args.append(int(arg))
            elif arg.replace('.', '', 1).isdigit():
                deserialized_args.append(float(arg))
            elif arg == 'True':
                deserialized_args.append(True)
            elif arg == 'False':
                deserialized_args.append(False)
            else:
                deserialized_args.append(arg)
        deserialized_array.append([function[0], deserialized_args])
    return deserialized_array
def multi_function_serial(serialized_data):
    buffer = [1]
    for i, individual_func in enumerate(serialized_data):
        if individual_func[0] == '' and individual_func[1] == []:
            continue
        buffer += individual_func
        if i < len(serialized_data) - 1:
            buffer.append(23)
    buffer.append(4)
    return buffer