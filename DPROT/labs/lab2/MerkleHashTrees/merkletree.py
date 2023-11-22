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
    for i in range(0, len(hash_list)):
        if hash_list[i][0] == x and hash_list[i][1] == y:
            return i
    # This is a workaround to let us know that we need to create a new node at -i position
    i=1
    while(hash_list[i][0] <= x):
        i+=1
        if i==len(hash_list):
            break
    return i*-1



def generate_proof_of_membership():
    global index_file

    with open(index_file, "r") as f:
        index_data = [f.readline().split(":")]
        for line in f.readlines():
            index_data.append(line.split(":"))

    doc_name = input("Enter the document name (e.g., doc0.dat): ")
    k = int(input("Enter the position k for which you want to generate the proof: "))
    proof_file_path = input("Enter the path to save the proof file: ")

    reconstructed_proof = generate_proof(index_data, k)
    with open(proof_file_path, "w") as proof_file:
        for node in reconstructed_proof:
            proof_file.write(f"{node[0]}:{node[1]}:{node[2]}\n")

    print(f"\nProof of membership for {doc_name} at position {k} has been generated and saved to {proof_file_path}.")
    print("\nReconstructed Proof:")
    for node in reconstructed_proof:
        print(f"{node[0]}:{node[1]}:{node[2]}:{node[3]}")



def verify_proof_of_membership():
    global index_file

    with open(index_file, "r") as f:
        index_data = [f.readline().split(":")]
        for line in f.readlines():
            index_data.append(line.split(":"))

    doc_name = input("Enter the document name (e.g., doc0.dat): ")
    k = int(input("Enter the position k for which you have the proof: "))
    proof_file_path = input("Enter the path to the proof file: ")

    expected_proof = []
    with open(proof_file_path, "r") as proof_file:
        for line in proof_file:
            expected_proof.append(line.strip().split(":"))


    reconstructed_proof = generate_proof(index_data, k)
    expected_proof = []
    with open(proof_file_path, "r") as proof_file:
        for line in proof_file:
            expected_proof.append(line.strip().split(":"))

    is_valid = verify_proof(index_data, expected_proof, k)
    print("\nExpected Proof:")
    for node in expected_proof:
        print(f"{node[0]}:{node[1]}:{node[2]}:{node[3]}")

    print("\nReconstructed Proof:")
    for node in reconstructed_proof:
        print(f"{node[0]}:{node[1]}:{node[2]}:{node[3]}")
    print(f"\nIs the proof valid? {is_valid}")



def reconstruct_proof_from_file(proof_file_path):
    reconstructed_proof = []
    with open(proof_file_path, "r") as proof_file:
        for line in proof_file:
            reconstructed_proof.append(line.strip().split(":"))
    return reconstructed_proof


def generate_proof(index_data, k):
    proof = []
    node_index = k
    while node_index > 0:
        sibling_index = node_index - 1 if node_index % 2 == 0 else node_index + 1
        is_left_child = node_index % 2 == 0
        sibling_node = [int(index_data[sibling_index][0]), int(index_data[sibling_index][1]),
                        index_data[sibling_index][2], is_left_child]
        proof.append(sibling_node)
        node_index = sibling_index // 2 - 1 if sibling_index % 2 == 0 else sibling_index // 2

    return proof


def verify_proof():
    global index_file
    global docs_folder
    global nodes_folder

    with open(index_file, "r") as f:
        index_data = [f.readline().split(":")]
        for line in f.readlines():
            index_data.append(line.split(":"))

    public_info = index_data[0][0] + ":" + index_data[0][1] + ":" + index_data[0][2] + ":" + index_data[0][3] + ":" + \
                  index_data[0][4] + ":" + index_data[0][5] + ":" + index_data[0][6]

    doc_name = input("Enter the document name (e.g., doc0.dat): ")
    k = int(input("Enter the position k for which you have the proof: "))
    proof_file_path = input("Enter the path to the proof file: ")

    with open(proof_file_path, "r") as proof_file:
        proof_data = [line.split(":") for line in proof_file.readlines()]

    doc_index = int(doc_name.split(".")[0][3:])
    reconstructed_proof = generate_proof(index_data, k)
    is_valid = verify_proof_membership(public_info, doc_name, reconstructed_proof)
    print("\nIs the proof valid?", is_valid)

def verify_proof_membership(public_info, doc_name, reconstructed_proof):
    doc_prefix, _, _, _, _, _, _ = public_info.split(':')
    with open(os.path.join(docs_folder, doc_name), 'rb') as doc_file:
        doc_data = doc_file.read()
        doc_hash = compute_sha1_hash(doc_prefix.encode('utf-8') + doc_data)

    current_hash = doc_hash
    for node in reconstructed_proof:
        sibling_node_hash = bytes.fromhex(node[2])
        current_hash = compute_sha1_hash(sibling_node_hash + current_hash)
        
        print(f"Sibling Node Hash: {sibling_node_hash.hex()}")
        print(f"Current Hash: {current_hash.hex()}")

    root_hash = bytes.fromhex(public_info.split(":")[-1].strip())

    print(f"Final Current Hash: {current_hash.hex()}")
    print(f"Root Hash: {root_hash.hex()}")

    return current_hash == root_hash


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
