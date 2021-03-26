import datetime
import traceback
import os
import re
from time import sleep

FIRST_MFT = {}
SECOND_MFT = set()
first_end = 0
second_end = 0

def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

def start():
    global FIRST_MFT, SECOND_MFT, first_end, second_end
    with open("filesystem", "a+b") as root:
        if is_non_zero_file("filesystem"):
            if os.path.getsize("filesystem") >= 20000000:
                print("DATOTEKA JE PREVELIKA")
                input("Press any key to exit...")
                exit()
            else:
                root.seek(0)
        temp = root.readline()
        entry = temp.strip().decode("utf-8").split(",")
        first_end = root.tell()
        for item in entry:
            if "." in item:
                FIRST_MFT.update({item:"file"})
            elif item != '':
                FIRST_MFT.update({item:"folder"})
        temp = root.readline()
        if len(temp) != 0:
            SECOND_MFT = eval('{' + temp.decode("utf-8") + '}')
        second_end = root.tell()

def create(path_list):
    global FIRST_MFT, SECOND_MFT, first_end, second_end
    content = ''
    if "." not in path_list[-1]:
        print(f"Funkcija 'create' kreira datoteku koja mora imati ekstenziju u imenu. Provjerite '{path_list[-1]}'")
    else:
        if len(path_list) == 2:
            if path_list[0] in FIRST_MFT and FIRST_MFT[path_list[0]] == "folder":
                if (path_list[0],path_list[1]) not in SECOND_MFT:
                    SECOND_MFT.add((path_list[0],path_list[1]))
                    with open("filesystem", "a+b") as root:
                        root.seek(second_end)
                        content = root.read()
                    update_file(content)
                else:
                    print(f"Datoteka '{path_list[1]}' vec postoji u '{path_list[0]}'.")
            else:
                print(f"Direktorijum '{path_list[0]}' ne postoji, pa se ne moze kreirati datoteka '{path_list[1]}' u njemu.")
        elif len(path_list) == 1:
            if path_list[0] not in FIRST_MFT:
                FIRST_MFT.update({path_list[0]:"file"})
                with open("filesystem", "rb+") as root:
                        root.seek(second_end)
                        content = root.read()
                update_file(content)
            else:
                print(f"Datoteka '{path_list[0]}' vec postoji u 'root\'.")
    
def mkdir(path_list):
    global FIRST_MFT, SECOND_MFT, second_end
    content = ''
    if len(path_list) == 1:
        if len(path_list[0]) != 0:
            if "." not in path_list[0]:
                if path_list[0] not in FIRST_MFT:
                    FIRST_MFT.update({path_list[0]:"folder"})
                    with open("filesystem", "rb+") as root:
                        root.seek(second_end)
                        content = root.read()
                    update_file(content)
                else:
                    print(f"Direktorijum '{path_list[0]}' vec postoji u 'root\'.")
            else:
                print(f"Funkcija 'mkdir' kreira direktorijume koji nemaju ekstenziju u imenu. Provjerite '{path_list[0]}'")
    elif len(path_list) == 2:
        if path_list[0] in FIRST_MFT and FIRST_MFT[path_list[0]] == "folder":
            if "." not in path_list[1]:
                if (path_list[0],path_list[1]) not in SECOND_MFT:
                    SECOND_MFT.add((path_list[0],path_list[1]))
                    with open("filesystem", "a+b") as root:
                        root.seek(second_end)
                        content = root.read()
                    update_file(content)
                else:
                        print(f"Direktorijum '{path_list[1]}' vec postoji u '{path_list[0]}'.")
            else:
                print(f"Funkcija 'mkdir' kreira direktorijume koji nemaju ekstenziju u imenu. Provjerite '{path_list[1]}'")
        else:
            print(f"Direktorijum '{path_list[0]}' ne postoji ili je u pitanju datoteka, pa se ne moze kreirati direktorijum '{path_list[1]}' u njemu.")

def update_file(content):
    global FIRST_MFT, SECOND_MFT, first_end, second_end
    temp1 = 0
    temp2 = 0
    with open('filesystem', 'wb+') as root:
        for item in FIRST_MFT:
            temp1 += 1
            root.write(str(item).encode())
            if temp1 != len(FIRST_MFT):
                root.write(b',')
        first_end = root.tell()
        root.write(b'\n')
        for item in SECOND_MFT:
            temp2 += 1
            root.write(str(item).encode())
            if temp2 != len(SECOND_MFT):
                root.write(b',')
        second_end = root.tell()
        if isinstance(content, bytes):
            if len(content) > 0 and content[0] == b'\n':
                root.write(content)
            elif len(content) == 0:
                root.write(b'')
            elif len(content) > 0 and content[0] != b'\n':
                root.write(b'\n'+content)
        else:
            if len(content) > 0 and content[0] == b'\n':
                root.write(content.encode())
            elif len(content) == 0:
                root.write(b'')
            elif len(content) > 0 and content[0] != b'\n':
                root.write(b'\n' + content.encode())

def rename(old, new):
    global FIRST_MFT, SECOND_MFT, second_end
    if len(old) == 2:
        if old[0] in FIRST_MFT and FIRST_MFT[old[0]] == "folder":
            if (old[0], old[1]) in SECOND_MFT:
                SECOND_MFT.remove((old[0],old[1]))
                SECOND_MFT.add((old[0],new))
            else:
                print(f"'{old[1]}' ne postoji u '{old[0]}'")
        else:
            print(f"Ne postoji folder '{old[0]}'")
    elif len(old) == 1:
        if len(old[0]) != 0:
            if old[0] in FIRST_MFT:
                FIRST_MFT[new] = FIRST_MFT.pop(old[0])
                temp_set1 = set()
                temp_set2 = set()
                for item in SECOND_MFT:
                    if item[0] == old[0]:
                        temp_set1.add(item)
                        temp_set2.add((new, item[1]))
                SECOND_MFT -= temp_set1
                for item in temp_set2:
                    SECOND_MFT.add(item)
            else:
                print(f"Datoteka '{old[0]}' ne postoji.")
    else:
        print("Nepotpuna putanja, provjerite komandu ili pogledajte help().")
    with open("filesystem", "rb+") as root:
        root.seek(second_end)
        content = root.read()
    update_file(content.replace(old[-1].encode(), new.encode()))

def echo(path_list, text):
    global FIRST_MFT, SECOND_MFT, second_end
    date = str(datetime.datetime.now())
    size = len(text)
    if len(path_list) == 2:
        if path_list[0] in FIRST_MFT and FIRST_MFT[path_list[0]] == "folder":
            if (path_list[0], path_list[1]) in SECOND_MFT and "." in path_list[1]:
                with open("filesystem", "ab+") as root:
                    root.seek(second_end)
                    tmp1 = root.read()
                    tmp2 = path_list[1].encode()
                    tmp3 = re.findall(tmp2, tmp1)
                    if len(tmp3) < 1:
                        root.seek(0,2)
                        root.write(b'\n')
                        root.write(path_list[0].encode() + b'>' + path_list[1].encode())
                        root.write(b'\n')
                        root.write(str(size).encode())
                        root.write(b'\n')
                        root.write(date.encode())
                        root.write(b'\n')
                        root.write(b'~#~\n')
                        root.write(text.encode())
                        root.write(b'\n~~~')
                    else:
                        print("Datoteka ima vec sadrzaj. Nemate privilegije da promijenite sadrzaj.")
            else:
                print(f"Datoteka '{path_list[1]}' ne postoji ili je direktorijum.")
        else:
            print(f"Direktorijum '{path_list[0]}' ne postoji.")
    elif len(path_list) == 1:
        if path_list[0] in FIRST_MFT and FIRST_MFT[path_list[0]] == 'file':
             with open("filesystem", "ab+") as root:
                    root.seek(second_end)
                    tmp1 = root.read()
                    tmp2 = path_list[0].encode()
                    tmp3 = re.findall(tmp2, tmp1)
                    if len(tmp3) < 1:
                        root.seek(0,2)
                        root.write(b'\n')
                        root.write(path_list[0].encode())
                        root.write(b'\n')
                        root.write(str(size).encode())
                        root.write(b'\n')
                        root.write(date.encode())
                        root.write(b'\n')
                        root.write(b'~#~\n')
                        root.write(text.encode())
                        root.write(b'\n~~~')
                    else:
                        print("Datoteka ima vec sadrzaj. Nemate privilegije da promijenite sadrzaj.")
        else:
            print(f"Datoteka '{path_list[0]}' ne postoji ili je direktorijum.")

def ls(path_list):
    global FIRST_MFT, SECOND_MFT
    if len(path_list[0]) == 0:
        print()
        for item in FIRST_MFT:
            print(item)
    elif len(path_list) == 1:
        print()
        if path_list[0] in FIRST_MFT and FIRST_MFT[path_list[0]] == "folder":
            for element in SECOND_MFT:
                if path_list[0] in element:
                    print(element[1])
        else:
            print("Direktorijum ne postoji ili se radi o datoteci.")
    print()

def cat(path_list):
    global FIRST_MFT, SECOND_MFT, second_end
    if len(path_list) == 1:
        if path_list[0] in FIRST_MFT and FIRST_MFT[path_list[0]] == "file":
            with open("filesystem", "rb+") as root:
                root.seek(second_end)
                if path_list[0].encode() in root.read():
                    root.seek(second_end)
                    tmp = root.read().decode("utf-8")
                    position_start = tmp.find(path_list[0])
                    position_start += tmp[position_start:].find("~#~")
                    position_end = tmp[position_start:].find("~~~")
                    print(tmp[position_start + 4:position_start + position_end])
                else:
                    print(f"Datoteka '{path_list[0]}' je prazna.")
        else:
            print(f"Datoteka '{path_list[0]}' ne postoji ili je u pitanju direktorijum.")
    elif len(path_list) == 2:
        if path_list[0] in FIRST_MFT and FIRST_MFT[path_list[0]] == "folder":
            if (path_list[0], path_list[1]) in SECOND_MFT and "." in path_list[1]:
                with open("filesystem", "rb+") as root:
                    root.seek(second_end)
                    name_of_file = (path_list[0] + '>' + path_list[1]).encode()
                    if name_of_file in root.read():
                        root.seek(second_end)
                        tmp = root.read().decode("utf-8")
                        position_start = tmp.find(name_of_file.decode("utf-8"))
                        position_start += tmp[position_start:].find("~#~")
                        position_end = tmp[position_start:].find("~~~")
                        print(tmp[position_start+4:(position_start + position_end)])
                    else:
                        print(f"Datoteka '{path_list[1]}' je prazna.")
            else:
                print(f"Datoteka '{path_list[1]}' ne postoji ili je u pitanju direktorijum.")
        else:
            print(f"Nepoznata datoteka '{path_list[0]}' ili je u pitanju direktorijum.")

def stat(path_list):
    global FIRST_MFT, SECOND_MFT, second_end
    flag = False
    if len(path_list) == 1:
        if path_list[0] in FIRST_MFT and FIRST_MFT[path_list[0]] == "file":
            with open("filesystem", "rb+") as root:
                root.seek(second_end)
                for line in root:
                    if line.strip() == path_list[0].encode():
                        flag = True
                        size = root.readline().decode("utf-8").strip()
                        date = root.readline().decode("utf-8").strip()
                        print(f"STAT:\nroot\\{path_list[0]}:\nSIZE: {size}B\nDATE&TIME: {date}")
            if flag == False:
                print(f"Datoteka root\\{path_list[0]} je kreirana ali nije nikada inicijalizovana. Velicina datoteke je 0B")
        else:
            print(f"Datoteka '{path_list[0]}' ne postoji ili je u pitanju direktorijum.")
    elif len(path_list) == 2:
        flag = False
        if path_list[0] in FIRST_MFT and FIRST_MFT[path_list[0]] == "folder":
            if (path_list[0], path_list[1]) in SECOND_MFT and "." in path_list[1]:
                with open("filesystem", "rb+") as root:
                    root.seek(second_end)
                    for line in root:
                        if line.strip() == (path_list[0] + '>' + path_list[1]).encode():
                            flag = True
                            size = root.readline().decode("utf-8").strip()
                            date = root.readline().decode("utf-8").strip()
                            print(f"STAT:\nroot\\{path_list[0]}\\{path_list[1]}:\nSIZE: {size}B\nDATE&TIME: {date}")
                if flag == False:
                    print(f"Datoteka root\\{path_list[0]}\\{path_list[1]} je kreirana ali nije nikada inicijalizovana. Velicina datoteke je 0B")
            else:
                print(f"Datoteka '{path_list[1]}' ne postoji ili je u pitanju direktorijum.")
        else:
            print(f"Nepoznata datoteka '{path_list[0]}' ili je u pitanju direktorijum.")

def dir():
    global FIRST_MFT, SECOND_MFT
    print("\nroot\\")
    for item in FIRST_MFT:
        if FIRST_MFT[item] == 'folder':
            print("|----" + item + "\\")
        else:
            print("|----" + item)
        for element in SECOND_MFT:
            if element[0] == item:
                if len(element) == 2:
                    print("|     |--" + element[1])
    print()

def mv(source_path_list, destination_path_list):
    global FIRST_MFT, SECOND_MFT, second_end
    content = ''
    replace = ''
    replace_with = ''
    if len(source_path_list) == 1:
        if source_path_list[0] in FIRST_MFT and FIRST_MFT[source_path_list[0]] == "file":
            if len(destination_path_list) == 1:
                if len(destination_path_list[0]) != 0:
                    if destination_path_list[0] in FIRST_MFT and FIRST_MFT[destination_path_list[0]] == "folder":
                        SECOND_MFT.add((destination_path_list[0], source_path_list[0]))
                        FIRST_MFT.pop(source_path_list[0])
                        replace = source_path_list[0]
                        replace_with = destination_path_list[0] + ">" + source_path_list[0]
                    else:
                        print(f"Direktorijum '{destination_path_list[0]}' ne postoji ili je u pitanju datoteka.")
        else:
            print(f"Datoteka '{source_path_list[0]}' ne postoji ili je u pitanju direktorijum.")
    elif len(source_path_list) == 2:
        if source_path_list[0] in FIRST_MFT and FIRST_MFT[source_path_list[0]] == "folder":
            if (source_path_list[0], source_path_list[1]) in SECOND_MFT and "." in source_path_list[1]:
                if len(destination_path_list) == 1 and source_path_list[0] != destination_path_list[0]:
                    if len(destination_path_list[0]) == 0:
                        FIRST_MFT.update({source_path_list[1]:"file"})
                        SECOND_MFT.remove((source_path_list[0], source_path_list[1]))
                        replace = source_path_list[0] + ">" + source_path_list[1]
                        replace_with = source_path_list[1]
                    else:
                        if destination_path_list[0] in FIRST_MFT and FIRST_MFT[destination_path_list[0]] == "folder":
                            SECOND_MFT.add((destination_path_list[0], source_path_list[1]))
                            SECOND_MFT.remove((source_path_list[0], source_path_list[1]))
                            replace = source_path_list[0] + ">" + source_path_list[1]
                            replace_with = destination_path_list[-1] + ">" + source_path_list[1]
                        else:
                            print(f"Direktorijum '{destination_path_list[0]}' ne postoji ili je u pitanju datoteka.")
            else:
                print(f"Izvorisna datoteka '{source_path_list[0]}\\{source_path_list[1]}' ne postoji ili je u pitanju direktorijum.")
        else:
            print(f"Direktorijum '{source_path_list[0]}' ne postoji ili je u pitanju datoteka.")
    with open("filesystem", "rb+") as root:
        root.seek(second_end)
        content = root.read()
    update_file(content.replace(replace.encode(), replace_with.encode()))

def cp(source_path_list, destination_path_list):
    global FIRST_MFT, SECOND_MFT, second_end
    content = ''
    file_content = ''
    if len(source_path_list) == 1:
        if source_path_list[0] in FIRST_MFT and FIRST_MFT[source_path_list[0]] == "file":
            if len(destination_path_list) == 1:
                if len(destination_path_list[0]) != 0:
                    if destination_path_list[0] in FIRST_MFT and FIRST_MFT[destination_path_list[0]] == "folder":
                        SECOND_MFT.add((destination_path_list[0], source_path_list[0]))
                        with open("filesystem", "rb+") as root:
                            root.seek(second_end)
                            name_of_file = source_path_list[0].encode()
                            if name_of_file in root.read():
                                root.seek(second_end)
                                tmp = root.read().decode("utf-8")
                                position_start = tmp.find(name_of_file.decode("utf-8"))
                                position_start += tmp[position_start:].find("~#~")
                                position_end = tmp[position_start:].find("~~~")
                                file_content = tmp[position_start + 4:position_start + position_end]
                                size = len(file_content)
                                date = str(datetime.datetime.now())
                                file_content = "\n"+destination_path_list[0]+">"+source_path_list[0]+"\n"+str(size)+"\n"+date+"\n"+"~#~\n"+file_content+"~~~"
                    else:
                        print(f"Direktorijum '{destination_path_list[0]}' ne postoji ili je u pitanju datoteka.")
        else:
            print(f"Datoteka '{source_path_list[0]}' ne postoji ili je u pitanju direktorijum.")
    elif len(source_path_list) == 2:
        if source_path_list[0] in FIRST_MFT and FIRST_MFT[source_path_list[0]] == "folder":
            if (source_path_list[0], source_path_list[1]) in SECOND_MFT and "." in source_path_list[1]:
                if len(destination_path_list) == 1:
                    if len(destination_path_list[0]) == 0:
                        FIRST_MFT.update({source_path_list[1]:"file"})
                        with open("filesystem", "rb+") as root:
                            root.seek(second_end)
                            name_of_file = (source_path_list[0] + '>' + source_path_list[1]).encode()
                            if name_of_file in root.read():
                                root.seek(second_end)
                                tmp = root.read().decode("utf-8")
                                position_start = tmp.find(name_of_file.decode("utf-8"))
                                position_start += tmp[position_start:].find("~#~")
                                position_end = tmp[position_start:].find("~~~")
                                file_content = tmp[position_start + 4:position_start + position_end]
                                size = len(file_content)
                                date = str(datetime.datetime.now())
                                file_content = "\n"+source_path_list[1]+"\n"+str(size)+"\n"+date+"\n"+"~#~\n"+file_content+"~~~"
                    else:
                        if destination_path_list[0] in FIRST_MFT and FIRST_MFT[destination_path_list[0]] == "folder":
                            SECOND_MFT.add((destination_path_list[0], source_path_list[1]))
                            with open("filesystem", "rb+") as root:
                                root.seek(second_end)
                                name_of_file = (source_path_list[0] + '>' + source_path_list[1]).encode()
                                if name_of_file in root.read():
                                    root.seek(second_end)
                                    tmp = root.read().decode("utf-8")
                                    position_start = tmp.find(name_of_file.decode("utf-8"))
                                    position_start += tmp[position_start:].find("~#~")
                                    position_end = tmp[position_start:].find("~~~")
                                    file_content = tmp[position_start + 4:position_start + position_end]
                                    size = len(file_content)
                                    date = str(datetime.datetime.now())
                                    file_content = "\n"+destination_path_list[0]+">"+source_path_list[1]+"\n"+str(size)+"\n"+date+"\n"+"~#~\n"+file_content+"\n~~~"
                        else:
                            print(f"Direktorijum '{destination_path_list[0]}' ne postoji ili je u pitanju datoteka.")
            else:
                print(f"Izvorisna datoteka '{source_path_list[0]}\\{source_path_list[1]}' ne postoji ili je u pitanju direktorijum.")
        else:
            print(f"Direktorijum '{source_path_list[0]}' ne postoji ili je u pitanju datoteka.")
    with open("filesystem", "rb+") as root:
        root.seek(second_end)
        content = root.read()
    update_file(content+file_content.encode())

def get(source_path_list, destination_path):
    global FIRST_MFT, SECOND_MFT
    content = ''
    if len(source_path_list) == 1:
        if source_path_list[0] in FIRST_MFT and FIRST_MFT[source_path_list[0]] == "file":
            with open("filesystem", "rb+") as root:
                root.seek(second_end)
                if source_path_list[0].encode() in root.read():
                    root.seek(second_end)
                    tmp = root.read().decode("utf-8")
                    position_start = tmp.find(source_path_list[0])
                    position_start += tmp[position_start:].find("~#~")
                    position_end = tmp[position_start:].find("~~~")
                    content = tmp[position_start + 4:position_start + position_end]
                else:
                    content = ''
            if os.path.isdir(destination_path[0]):
                with open(destination_path + source_path_list[-1], "wb+") as destination:
                    destination.write(content.encode())
            else:
                print(f"Potrebno je unijeti putanju foldera. '{destination_path}' nije validna putanja.")
        else:
            print(f"Datoteka '{source_path_list[0]}' ne postoji ili je u pitanju direktorijum.")
    elif len(source_path_list) == 2:
        if source_path_list[0] in FIRST_MFT and FIRST_MFT[source_path_list[0]] == "folder":
            if (source_path_list[0], source_path_list[1]) in SECOND_MFT and "." in source_path_list[1]:
                with open("filesystem", "rb+") as root:
                    root.seek(second_end)
                    name_of_file = (source_path_list[0] + '>' + source_path_list[1]).encode()
                    if name_of_file in root.read():
                        root.seek(second_end)
                        tmp = root.read().decode("utf-8")
                        position_start = tmp.find(name_of_file.decode("utf-8"))
                        position_start += tmp[position_start:].find("~#~")
                        position_end = tmp[position_start:].find("~~~")
                        content = tmp[position_start + 4:position_start + position_end]
                    else:
                        content = ''
                if os.path.isdir(destination_path):
                    with open(destination_path + source_path_list[-1], "wb+") as destination:
                        destination.write(content.encode())
                else:
                    print(f"Potrebno je unijeti putanju foldera. '{destination_path}' nije validna putanja.")
            else:
                print(f"Izvorisna datoteka '{source_path_list[0]}\\{source_path_list[1]}' ne postoji ili je u pitanju direktorijum.")
        else:
            print(f"Direktorijum '{source_path_list[0]}' ne postoji ili je u pitanju datoteka.")

def put(source_path, destination_path_list):
    global FIRST_MFT, SECOND_MFT, second_end
    content = ''
    if os.path.isfile(source_path):
        with open(source_path, "rb+") as source:
            text = source.read()
        date = str(datetime.datetime.now())
        size = len(text)
        source_path_list = source_path.split("\\")
        new_file = source_path_list[-1]
        if len(destination_path_list) == 1:
            if len(destination_path_list[0]) != 0:
                if destination_path_list[0] in FIRST_MFT and FIRST_MFT[destination_path_list[0]] == "folder":
                    if (destination_path_list[0], new_file) not in SECOND_MFT:
                        SECOND_MFT.add((destination_path_list[0], new_file))
                        with open("filesystem", "ab+") as root:
                            root.seek(0,2)
                            root.write(b'\n')
                            root.write((destination_path_list[0] + '>' + new_file).encode())
                            root.write(b'\n')
                            root.write(str(size).encode())
                            root.write(b'\n')
                            root.write(date.encode())
                            root.write(b'\n')
                            root.write(b'~#~\n')
                            root.write(text)
                            root.write(b'\n~~~')
                            root.seek(second_end)
                            content = root.read()
                        update_file(content)
                    else:
                        print(f"Datoteka '{new_file}' vec postoji u folderu '{destination_path_list[0]}'")
                else:
                    print(f"Direktorijum '{destination_path_list[0]}' ne postoji ili je u pitanju datoteka.")
            elif len(destination_path_list[0]) == 0:
                if new_file not in FIRST_MFT:
                    FIRST_MFT.update({new_file:"file"})
                    with open("filesystem", "ab+") as root:
                        root.seek(0,2)
                        root.write(b'\n')
                        root.write(new_file.encode())
                        root.write(b'\n')
                        root.write(str(size).encode())
                        root.write(b'\n')
                        root.write(date.encode())
                        root.write(b'\n')
                        root.write(b'~#~\n')
                        root.write(text)
                        root.write(b'\n~~~')
                        root.seek(second_end)
                        content = root.read()
                    update_file(content)
                else:
                    print(f"Datoteka '{new_file}' vec postoji u 'root'.")
    else:
        print(f"Datoteka '{source_path}' nije isprvna ili je u pitanje direktorijum. Provjerite putanju.")

def rm(path_list):
    global FIRST_MFT, SECOND_MFT, second_end
    content = ''
    if len(path_list) == 1:
        if path_list[0] in FIRST_MFT and FIRST_MFT[path_list[0]] == 'file':
            FIRST_MFT.pop(path_list[0])
            with open("filesystem", "rb+") as root:
                root.seek(second_end)
                if path_list[0].encode() in root.read():
                    root.seek(second_end)
                    tmp = root.read().decode("utf-8")
                    position_start = tmp.find(path_list[0])
                    position_end = tmp[position_start:].find("~~~")
                    sub = tmp[position_start:position_start + position_end + 4]
                    content = tmp.replace(sub, '').encode()
                    update_file(content)
        else:
            print(f"Datoteka '{path_list[0]}' ne postoji ili je u pitanju direktorijum.")
    elif len(path_list) == 2:
        if path_list[0] in FIRST_MFT and FIRST_MFT[path_list[0]] == 'folder':
            if (path_list[0], path_list[1]) in SECOND_MFT:
                SECOND_MFT.remove((path_list[0], path_list[1]))
                with open("filesystem", "rb+") as root:
                    root.seek(second_end)
                    if (path_list[0] + '>' + path_list[1]).encode() in root.read():
                        root.seek(second_end)
                        tmp = root.read().decode("utf-8")
                        position_start = tmp.find(path_list[0] + '>' + path_list[1])
                        position_end = tmp[position_start:].find("~~~")
                        sub = tmp[position_start:position_start + position_end + 4]
                        content = tmp.replace(sub, '').encode()
                        update_file(content)
            else:
                print(f"Datoteka '{path_list[0]}\\{path_list[1]}' ne postoji ili je u pitanju direktorijum.")
        else:
            print(f"Direktorijum '{path_list[0]}' ne postoji ili je u pitanju datoteka.")

def rmdir(path_list):
    global FIRST_MFT, SECOND_MFT, second_end
    content = ''
    tmp_set = set()
    tmp_list = list()
    if len(path_list) == 1:
        if len(path_list[0]) == 0:
            FIRST_MFT.clear()
            SECOND_MFT.clear()
            update_file(content)
        else:
            if path_list[0] in FIRST_MFT and FIRST_MFT[path_list[0]] == 'folder':
                for element in SECOND_MFT:
                    if element[0] == path_list[0]:
                        if '.' in element[1]:
                            tmp_list.append([path_list[0],element[1]])
                        else:
                            tmp_set.add((element[0], element[1]))
                if len(tmp_list) != 0:
                    for element in tmp_list:
                        rm(element)
                if len(tmp_set) != 0:
                    SECOND_MFT -= tmp_set
                FIRST_MFT.pop(path_list[0])
                with open("filesystem", "rb+") as root:
                    root.seek(second_end)
                    content = root.read()
                update_file(content)
            else:
                print(f"Funkcija rmdir sluzi sa brisanje direktorijuma. Provjerite putanju.")
    elif len(path_list) == 2:
        if path_list[0] in FIRST_MFT and FIRST_MFT[path_list[0]] == 'folder':
                for element in SECOND_MFT:
                    if element[0] == path_list[0] and element[1] == path_list[1]:
                        tmp_set.add((element[0], element[1]))
                if len(tmp_set) != 0:
                    SECOND_MFT -= tmp_set
                with open("filesystem", "rb+") as root:
                    root.seek(second_end)
                    content = root.read()
                update_file(content)
        else:
            print(f"Funkcija rmdir sluzi sa brisanje direktorijuma. Provjerite putanju.")


def welcome_message():
    print("------------------------------------------------------")
    print("2019. Projektni zadatak iz osnova operativnih sistema:")
    print("           Implementacija NTFS fajl sistema           ")
    print("Student: Jovan Vrhovac")
    print("Verzija 0.1")
    print("Za POMOC ukucajte komandu 'help'")
    print("------------------------------------------------------")
    print("\n")

def help():
    print()
    with open("help.txt", "r") as help:
        print(help.read())
    print()

def console():
    start()
    while True:
        command = input(">> ")
        if command == "exit":
            print("Konzola se zatvara. Hvala na koriscenju!")
            sleep(2.5)
            break
        elif command == "help":
            help()
        elif command == "":
            continue
        else:
            first = command.find('"')
            second = first + command[first +1:].find('"')
            text = command[first + 1:second +1]
            com = command.split(' ')
            if len(com) >= 1:
                if com[0] == 'mkdir':
                    if "root\\" in com[1]:
                        path_list = com[1].replace('root\\', '').split('\\')
                        mkdir(path_list)
                    else:
                        print("Putanja mora uvijek biti apsolutna pocevsi od 'root\\'.")
                elif com[0] == 'create':
                    if "root\\" in com[1]:
                        path_list = com[1].replace('root\\', '').split('\\')
                        create(path_list)
                    else:
                        print("Putanja mora uvijek biti apsolutna pocevsi od 'root\\'.")
                elif com[0] == "put":
                    if len(com) >= 3:
                        if "root\\" in com[2]:
                            path_list = com[2].replace('root\\', '').split('\\')
                            put(com[1], path_list)
                        else:
                            print("Putanja mora uvijek biti apsolutna pocevsi od 'root\\'.")
                    else:
                        print("Broj argumenata za funkciju 'put' je 2.")
                elif com[0] == "get": 
                    if len(com) >= 3:
                        if "root\\" in com[1]:
                            path_list = com[1].replace('root\\', '').split('\\')
                            get(path_list, com[2])
                        else:
                            print("Putanja mora uvijek biti apsolutna pocevsi od 'root\\'.")
                    else:
                        print("Broj argumenata za funkciju 'get' je 2.")
                elif com[0] == "ls":
                    if "root\\" in com[1]:
                        path_list = com[1].replace('root\\', '').split('\\')
                        ls(path_list)
                    else:
                        print("Putanja mora uvijek biti apsolutna pocevsi od 'root\\'.")
                elif com[0] == "cp":
                    if len(com) >= 3:
                        if "root\\" in com[2]:
                            path_list_source = com[1].replace('root\\', '').split('\\')
                            path_list_destination = com[2].replace('root\\', '').split('\\')
                            cp(path_list_source, path_list_destination)
                        else:
                            print("Putanja mora uvijek biti apsolutna pocevsi od 'root\\'.")
                    else:
                        print("Broj argumenata za funkciju 'cp' je 2.")
                elif com[0] == "mv":
                    if len(com) >= 3:
                        if "root\\" in com[2]:
                            path_list_source = com[1].replace('root\\', '').split('\\')
                            path_list_destination = com[2].replace('root\\', '').split('\\')
                            mv(path_list_source, path_list_destination)
                        else:
                            print("Putanja mora uvijek biti apsolutna pocevsi od 'root\\'.")
                    else:
                        print("Broj argumenata za funkciju 'mv' je 2.")
                elif com[0] == "echo":
                    if len(com) >= 3:
                        if "root\\" in com[1]:
                            path_list = com[1].replace('root\\', '').split('\\')
                            echo(path_list, text)
                        else:
                            print("Putanja mora uvijek biti apsolutna pocevsi od 'root\\'.")
                    else:
                        print("Broj argumenata za funkciju 'echo' je 2.")
                elif com[0] == "rename":
                    if len(com) >= 3:
                        if "root\\" in com[1]:
                            path_list = com[1].replace('root\\', '').split('\\')
                            rename(path_list, com[2])
                        else:
                            print("Putanja mora uvijek biti apsolutna pocevsi od 'root\\'.")
                    else:
                        print("Broj argumenata za funkciju 'rename' je 2.")
                elif com[0] == "cat":
                    if "root\\" in com[1]:
                        path_list = com[1].replace('root\\', '').split('\\')
                        cat(path_list)
                    else:
                        print("Putanja mora uvijek biti apsolutna pocevsi od 'root\\'.")
                elif com[0] == "rmdir":
                    if "root\\" in com[1]:
                        path_list = com[1].replace('root\\', '').split('\\')
                        rmdir(path_list)
                    else:
                        print("Putanja mora uvijek biti apsolutna pocevsi od 'root\\'.")
                elif com[0] == "rm":
                    if "root\\" in com[1]:
                        path_list = com[1].replace('root\\', '').split('\\')
                        rm(path_list)
                    else:
                        print("Putanja mora uvijek biti apsolutna pocevsi od 'root\\'.")
                elif com[0] == "stat":
                    if "root\\" in com[1]:
                        path_list = com[1].replace('root\\', '').split('\\')
                        stat(path_list)
                    else:
                        print("Putanja mora uvijek biti apsolutna pocevsi od 'root\\'.")
                elif com[0] == "dir":
                        dir()
                else:
                    print(f"Nepoznata komanda '{command}'. Pokusajte ponovo sa ispravnom komandom.")


def main():
    welcome_message()
    try:
        console()
    except Exception:
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
    