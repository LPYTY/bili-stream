import ctypes
from pathlib import Path

def bytes_to_hex_string(byte_array):
    return ''.join(f'{byte:02x}' for byte in byte_array)

def get_version_path(blive_path):
    path = Path(blive_path)
    if not path.exists():
        raise FileNotFoundError(f"Path {blive_path} does not exist.")
    if not path.is_dir():
        raise NotADirectoryError(f"Path {blive_path} is not a directory.")
    for item in path.iterdir():
        if item.is_dir() and item.name[0].isdigit():
            return item
    raise FileNotFoundError("No version directory found in the specified path.")

def get_version(version_path):
    return version_path.name

def get_build(version_path):
    return version_path.name.strip().split('.')[-1]

def get_target_dll_path(version_path):
    target_dll = version_path / 'bililive_secret.dll'
    if not target_dll.exists():
        raise FileNotFoundError(f"Target DLL {target_dll} does not exist.")
    return target_dll

def load_target_function(dll_path):
    dll_path = str(dll_path)  # Ensure the path is a string
    dll = ctypes.WinDLL(dll_path)
    # A random offset generated from my random generator
    offset = 0x1000
    dll_base = ctypes.cast(dll._handle, ctypes.c_void_p).value
    function_address = dll_base + offset
    # Define the function prototype
    function_type = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint)
    # Create a callable function
    return function_type(function_address)

def wrap_sign_function(target_function):
    def wrapped_function(input_string):
        result_buffer = ctypes.create_string_buffer(16)
        input_bytes = input_string.encode('ascii')
        input_length = ctypes.c_uint(len(input_bytes))
        target_function(result_buffer, input_bytes, input_length)
        return bytes_to_hex_string(result_buffer.raw)
    return wrapped_function

def get_dll_info(blive_path):
    version_path = get_version_path(blive_path)
    version = get_version(version_path)
    build = get_build(version_path)
    target_dll_path = get_target_dll_path(version_path)
    target_function = load_target_function(target_dll_path)
    wrapped_function = wrap_sign_function(target_function)
    
    return {
        'version': version,
        'build': build,
        'sign': wrapped_function
    }

def main():
    blive_path = 'D:/Programs/livehime'
    dll_info = get_dll_info(blive_path)
    print(f"Version: {dll_info['version']}, Build: {dll_info['build']}")
    string_to_encode = "access_key=&appkey=aae92bc66f3edfab&build=8803&page=1&page_size=100&platform=pc_link&room_id=26966999&ruid=1880315922&switch=contribution_rank&ts=1750765368&type=online_rank&version=7.9.2.8803"
    encoded_string = dll_info['sign'](string_to_encode)
    print(f"Encoded String: {encoded_string}")

if __name__ == "__main__":
    main()