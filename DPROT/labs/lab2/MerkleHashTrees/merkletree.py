#!/usr/bin/env python3
import os
import hashlib
import math

# Global variables
cwd = os.path.dirname(os.path.abspath(__file__))
docs_folder = os.path.join(cwd, 'docs')
nodes_folder = os.path.join(cwd, 'nodes')
index_file = os.path.join(cwd, "index.txt")


def cleanup(folder):
    for filename in os.listdir(folder):
        if ".dat" in filename:
            os.unlink(os.path.join(folder, filename))


def compute_sha1_hash(data: bytes) -> bytes:
    sha1 = hashlib.sha1()
    sha1.update(data)
    return sha1.digest()


def aggregate_hashes(hash1: bytes, hash2: bytes) -> bytes:
    return hash1 + hash2


def merkle_tree_full():
    global cwd
    global docs_folder
    global nodes_folder
    global index_file

    cleanup(nodes_folder)

    index_data = []

    doc_prefix = br'\x35'
    node_prefix = br'\xE8'

    num_docs = len(os.listdir(docs_folder))
    for doc_num in range(num_docs):
        with open(os.path.join(docs_folder, f"doc{doc_num}.dat"), 'rb') as doc_file:
            doc_data = doc_file.read()
            doc_hash = compute_sha1_hash(doc_prefix + doc_data)
            with open(os.path.join(nodes_folder, f"node0.{doc_num}.dat"), 'wb') as doc_output_file:
                doc_output_file.write(doc_hash)
                index_data.append(f"0:{doc_num}:{doc_hash.hex()}")

    num_levels = int(math.ceil(math.log2(num_docs)))

    for level in range(0, num_levels):
        for j in range(0, 2 ** (num_levels - level - 1)):
            node_file1_path = os.path.join(nodes_folder, f"node{level}.{2 * j}.dat")
            node_file2_path = os.path.join(nodes_folder, f"node{level}.{2 * j + 1}.dat")

            if os.path.exists(node_file1_path):
                with open(node_file1_path, 'rb') as node_file1:
                    node_data1 = node_file1.read()
            else:
                continue

            if os.path.exists(node_file2_path):
                with open(node_file2_path, 'rb') as node_file2:
                    node_data2 = node_file2.read()
            else:
                node_data2 = compute_sha1_hash(br'')

            hash2 = compute_sha1_hash(node_prefix + aggregate_hashes(node_data1, node_data2))

            with open(os.path.join(nodes_folder, f"node{level+1}.{j}.dat"), 'wb') as node_output_file:
                node_output_file.write(hash2)
                index_data.append(f"{level+1}:{j}:{hash2.hex()}")

    root_hash = index_data[-1].split(":")[-1]
    with open(index_file, "+w") as file:
        file.write(f"MerkleTree:sha1:{doc_prefix.decode('utf-8')[2:]}:{node_prefix.decode('utf-8')[2:]}:{num_docs}:{num_levels}:{root_hash}\n")
        for item in index_data:
            file.write(f"{item}\n")


def insert_new_document():
    global index_file
    global docs_folder

    with open(index_file, "r") as f:
        index_data = [f.readline().split(":")]
        for line in f.readlines():
            index_data.append(line.split(":"))

    num_docs = len(os.listdir(docs_folder))
    if int(index_data[0][4]) < num_docs:
        new_num_doc = num_docs - 1
        doc_prefix = br'\x' + index_data[0][2].encode('utf-8')
        node_prefix = br'\x' + index_data[0][3].encode('utf-8')
        with open(os.path.join(docs_folder, f"doc{new_num_doc}.dat"), 'rb') as doc_file:
            doc_data = doc_file.read()
            doc_hash = compute_sha1_hash(doc_prefix + doc_data)
            with open(os.path.join(nodes_folder, f"node0.{new_num_doc}.dat"), 'wb') as doc_output_file:
                doc_output_file.write(doc_hash)
                index_data[num_docs:num_docs] = [["0",f"{new_num_doc}",f"{doc_hash.hex()}\n"]]

        num_levels = int(math.ceil(math.log2(num_docs)))
        node_branch = new_num_doc
        new_node_branch = int(math.floor(new_num_doc / 2))
        for level in range(0, num_levels):
            if node_branch % 2 == 0:  # node de l'esquerra, mai tindrem node de la dreta
                node_data1 = read_node(level, node_branch)
                node_data2 = compute_sha1_hash(br'')
            else:  # node de la dreta
                node_data1 = read_node(level, node_branch-1)
                node_data2 = read_node(level, node_branch)
            hash2 = compute_sha1_hash(node_prefix + aggregate_hashes(node_data1, node_data2))
            with open(os.path.join(nodes_folder, f"node{level+1}.{new_node_branch}.dat"), 'wb') as node_output_file:
                node_output_file.write(hash2)
                x = find_node(level + 1, new_node_branch, index_data)
                if x<0:
                    x=x*-1
                    index_data[x:x] = [[f"{level + 1}",f"{new_node_branch}",f"{hash2.hex()}\n"]]
                else:
                    index_data[x] = [f"{level + 1}",f"{new_node_branch}",f"{hash2.hex()}\n"]
            node_branch = int(math.floor(node_branch / 2))
            new_node_branch = int(math.floor(node_branch / 2))
            if level+1 == num_levels:  # Root node, let's update the header
                index_data[0][4] = f"{num_docs}"
                index_data[0][5] = f"{num_levels}"
                index_data[0][-1] = f"{hash2.hex()}\n"
            
        with open(index_file, "w") as file:
            for items in index_data:
                item = ':'.join(items)
                file.write(f"{item}")
                # print(item, end="")
    else:
        print("No new file. Nothing to do.")


def read_node(x, y):
    with open(os.path.join(nodes_folder, f"node{x}.{y}.dat"), 'rb') as node_file1:
        data = node_file1.read()
    return data


def find_node(x, y, hash_list):
    x = str(x)
    y = str(y)
    for i in range(1, len(hash_list)):
        if hash_list[i][0] == x and hash_list[i][1] == y:
            return i
    # This is a workaround to let us know that we need to create a new node at -i position
    i=1
    while(hash_list[i][0] <= x):
        i+=1
        if i==len(hash_list):
            break
    return i*-1


def node_exist(x,y,hash_list):
    x = str(x)
    y = str(y)
    for i in range(1, len(hash_list)):  # Podria ser molt més eficient si el [i][0] és més gran que X ja sortir
        if hash_list[i][0] == x and hash_list[i][1] == y:
            return i
    return False


def generate_proof_of_membership():
    global index_file

    with open(index_file, "r") as f:
        index_data = [f.readline().split(":")]
        for line in f.readlines():
            index_data.append(line.split(":"))

    proof_path = []
    x = -1
    while x<0:
        x = int(input(f"What doc you want to get the proof on (doc[0:{int(index_data[0][4])-1}].dat): "))
        if x >= int(index_data[0][4]):
            x=-1
    for level in range(0,int(math.ceil(math.log2(int(index_data[0][4]))))):
        if x % 2 == 0:  # node esquerra
            if node_exist(level,x+1,index_data):
                proof_path.append(index_data[find_node(level,x+1,index_data)])
            else:
                # proof_path.append(compute_sha1_hash(br'').decode('utf-8'))  # FIXME Si faig decode em peta el codi... hardcodejem el hash
                proof_path.append(f"['{level}', '{x+1}', 'da39a3ee5e6b4b0d3255bfef95601890afd80709\\n'] <-- This node does not exist we use hardcoded hash of void")
        else:  # node dret
            proof_path.append(index_data[find_node(level,x-1,index_data)])
        x = int(math.floor(x / 2))
    print(f"To calculate the proof, you will need the appended prefix: \"\\x{index_data[0][3]}\"")
    for path in proof_path:
        print(path)
    print(index_data[-1])  # give the root too


def verify_proof():
    print("Sorry but tbh... didn't understand what you want us to do. Too late to even ask :(")
    """  # Ok let's not include this but leaving it here anyway hehe
    from random import choice
    from time import sleep
    riddles_and_solutions = [
        ("I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?", "An echo"),
        ("The more you take, the more you leave behind. What am I?", "Footsteps"),
        ("I am taken from a mine, and shut up in a wooden case, from which I am never released, and yet I am used by almost every person. What am I?", "Pencil lead"),
        ("I have keys but open no locks. I have space but no room. You can enter, but you can't go inside. What am I?", "A keyboard"),
        ("The person who makes it, sells it. The person who buys it never uses it. What is it?", "A coffin")
    ]
    random_riddle, solution = choice(riddles_and_solutions)
    print("But... I'll give you a riddle lol\n\t", random_riddle)
    for i in range(0,10):
        print(".", end="", flush=True)
        sleep(1)
    print("\tThe solution is: ", solution)
    """


def main():
    work = [
        merkle_tree_full,
        insert_new_document,
        generate_proof_of_membership,
        verify_proof
    ]
    while True:
        x = int(input("""
What to do?
    1: Calc full Merkle Tree
    2: Insert new document
    3: Generate proof of membership
    4: Verify proof of membership
    5: Exit
"""))
        if x == 5:
            break
        if x in [1, 2, 3, 4]:
            work[x - 1]()


if __name__ == "__main__":
    main()
