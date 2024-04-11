import getopt
import sys
import lief
import os

#https://github.com/lief-project/LIEF
'''
修改so函数名称
'''
MODIFY_SO_FILE = True
def modify_function_name(file_path, new_file_path, from_str, to_str, modify):
    print("+++++++++++++++++++++++++++++++++")
    binary: lief.ELF.Binary = lief.ELF.parse(file_path)
    for s in binary.symbols:
        if from_str in s.name:
            original_name = s.name
            if to_str != None and len(to_str) > 0:
                s.name = s.name.replace(from_str, to_str)
                print(original_name + " -> " + s.name)
            else:
                print(s.name)
    print("---------------------------------")
    if to_str != None and len(to_str) > 0 and modify:
        binary.write(new_file_path)
    return new_file_path

def show_modify_result(new_file_path, to_string, modify):
    if to_string != None and len(to_string) > 0 and modify:
        print("\nOutput the modify function name : {}".format(new_file_path))
        print("+++++++++++++++++++++++++++++++++")
        binary  = lief.parse(new_file_path)
        for item in binary.symbols:
            if to_string in item.name:
                print(item.name)
        print("---------------------------------")

def generate_new_file(src_file):
    so_dir = os.path.dirname(src_file)
    so_name = os.path.basename(src_file)
    name, ext = os.path.splitext(so_name)
    new_so_name = "{}-mod{}".format(name, ext)
    new_file_path = os.path.join(so_dir, new_so_name)
    return new_file_path

def modify_elf_so(from_string, to_string, from_file, modify):
    from_file_name = os.path.basename(from_file)
    to_file = generate_new_file(from_file)

    new_file_path_64 = modify_function_name(from_file_name, to_file, from_string, to_string, modify)
    show_modify_result(new_file_path_64, to_string, modify)


if __name__ == '__main__':
    from_string = None
    to_string = None
    from_file = None
    modify = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:t:m")
        for op, value in opts:
            if op == "-s":
                from_string = value
            elif op == "-t":
                to_string = value
            elif op == "-m":
                modify = True
        from_file = os.path.abspath(args[0]) if args != None and len(args) > 0 else None
    except getopt.GetoptError as err:
        print("error : {}".format(err))
        sys.exit()

    print("modify : {}, from string : {}, to string : {}, file : {}".format(modify, from_string, to_string, from_file))
    if from_file == None or to_string == None or (from_file == None or not os.path.exists(from_file)):
        sys.exit()
    modify_elf_so(from_string, to_string, from_file, modify)