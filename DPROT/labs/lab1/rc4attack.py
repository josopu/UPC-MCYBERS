from os import walk, path

# Get the data files. They must be stored inside a folder named "data" and at the same cwd as this file is
data_path = path.dirname(path.realpath(__file__)) + "/data/"

# Initialize key_guess as a list of 13 elements
key_guess = []
m0_hex = 0
iter_d = 1

# Function to extract binary values from a file
def get_data(file_path):
    iv_array= []
    message_array = []
    with open(file_path, "r") as file:
        for data in file.readlines():
            iv, message = data.split(" ")
            iv_array.append(iv[2:])
            message_array.append(message[2:-1])
    return iv_array, message_array


def key_sums(key_guess):
    val = 0
    for i in range(len(key_guess)):
        val += int(key_guess[i], 16)
    return val % 256


def simulate_attack(iv_array, message_array):
    global m0_hex
    global iter_d
    iter_d += 1
    keystream_prob = []
    
    print(f"Gathering keystream first bytes for IV={iv_array[0][:-2]}xx ... done")

    if iv_array[0][:2] == "01":
        for index in range(0,len(iv_array)):
            x_plus_2 = hex(int(iv_array[index], 16) + 2)[-2:]
            keystream_prob.append(hex(int(message_array[index], 16) ^ int(x_plus_2,16)))
        m0 = max(set(keystream_prob), key = keystream_prob.count)
        m0_hex = hex(int(m0, 16) % 256)
        m0_count = keystream_prob.count(m0)
        print(f"\tGuessed m[0]={m0_hex} (with freq. {m0_count}) *** OK ***")
    
        """ # The IV -> 03 is the generic part as well, so commenting this section out (not deleting just in case lol)
    elif iv_array[0][:2] == "03":
        for index in range(0,len(iv_array)):
            keystream_prob.append(hex((int(message_array[index], 16) ^ int(m0_hex, 16)) - int(iv_array[index][-2:], 16) - 6))
        key = max(set(keystream_prob), key = keystream_prob.count)
        key_hex = hex(int(key, 16) % 256)
        key_count = keystream_prob.count(key)
        key_guess.append(key_hex)
        print(f"\tGuessed k[{len(key_guess)-1}]={key_hex} (with freq. {key_count}) *** OK ***")
        """
    
    else:
        """
        (   c[0]                    XOR m[0]    )   -   x                   -   10                      -   k[0]
        (   message_array[index]    XOR m0_hex  )   -   iv_array[index]     -   iter_d*(iter_d+1)//2    -   sum(key_guess)
        """
        for index in range(0,len(iv_array)):
            keystream_prob.append(hex((int(message_array[index], 16) ^ int(m0_hex, 16)) - int(iv_array[index][-2:], 16) - iter_d * (iter_d + 1) // 2 - key_sums(key_guess)))
        key = max(set(keystream_prob), key = keystream_prob.count)
        key_hex = hex(int(key, 16) % 256)
        key_count = keystream_prob.count(key)
        key_guess.append(key_hex)
        print(f"\tGuessed k[{len(key_guess)-1}]={key_hex} (with freq. {key_count}) *** OK ***")

def main():
    data = []
    for data_file in next(walk(data_path))[2]:
        iv_array, message_array = get_data(data_path + data_file)
        simulate_attack(iv_array, message_array)

    # Format the guessed key as a 13-byte hexadecimal string
    print("Guessed key: 0x", end="")
    for key in key_guess:
        print(f"{key[-2:]}", end="")
    print("\nGuessed msg:", m0_hex)


if __name__ == "__main__":
    main()
