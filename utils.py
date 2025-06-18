import os

def load_instruction_from_file(file:str, default_instruction:str = "Do nothing"):
    """
    This function takes a file_path and tries to read the text within it.
    If the file doesn't exist, default instruction is used instead.

    :param file:
    :param default_instruction:
    :return: Instructions present in the file
    """
    instruction = default_instruction

    try:
        file_path = os.path.join(os.path.dirname(__file__), file)
        with open(file_path) as f:
            instruction = f.read()
            print(f"Successfully read the file - {file}")
    except FileNotFoundError:
        print(f"{file} couldn't be found")
    except Exception as e:
        print(f"Error reading {file}: {e}")
    return instruction


