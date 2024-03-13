"""Assignment 1: RGB TIF File Handling"""

# Function 1: Loading a TIF file to extract the data and information
def load_file(file_name):
    try:
        file_handle = open(file_name, 'rb')
        file = file_handle.read()
        name = f'{file_name}'
    except FileNotFoundError:  # check if a file exists or not
        file = bytes("", 'utf-8')
        name = "file not found"
    return file, name


# Function 2: Getting the file header and the IFD offset
def get_file_header(data):
    offset = data[4:8]
    # check whether little endian or big endian, outputs IFD offset with respect to endianness
    if data.startswith(b"II"):
        return 'little', int.from_bytes(offset, 'little')
    elif data.startswith(b"MM"):
        return 'big', int.from_bytes(offset, 'big')



# Extracting the directory entries
def extract_ifd_entries(data, byte_order, ifd_offset):
    # Number of entries
    number_entries = int.from_bytes(data[ifd_offset:ifd_offset + 2], byte_order)

    # Creating entry list. Range starts after the 2-byte count, ends after IFDs are finished.
    ifd_entry = [data[a:a + 12] for a in range(ifd_offset + 2, (number_entries * 12) + ifd_offset + 2, 12)]
    return ifd_entry, number_entries


# Extracting the IFD entry
def extract_ifd_entry(ifd_entry, byte_order):
    # Initialising the different field types and their sizes
    types = {1: 'BYTE', 2: 'ASCII', 3: 'SHORT', 4: 'LONG', 5: 'RATIONAL', 6: 'SBYTE', 7: 'UNDEFINED', 8: 'SSHORT', 9: 'SLONG', 10: 'SRATIONAL', 11: 'FLOAT', 12: 'DOUBLE'}
    type_size = {1 : 1, 2 : 1, 3 : 2, 4 : 4, 5 : 8, 6 : 1, 7 : 1, 8 : 2, 9 : 4, 10 : 8, 11 : 4, 12 : 8}

    # Separating the 12-byte sequence into smaller pieces
    byte = ifd_entry
    tags = int.from_bytes(byte[0:2], byte_order)
    field_type = types[int.from_bytes(byte[2:4], byte_order)]
    field_type_size = type_size[int.from_bytes(byte[2:4], byte_order)]
    number_of_values = int.from_bytes(byte[4:8], byte_order)
    value_offset = byte[8:]

    # putting the different separated bytes into one list type
    one_value = [tags, field_type, field_type_size, number_of_values, value_offset]
    return one_value


# Extracting the IFD values. Each byte in the IFD means something different.
def extract_field_values(data, field_entry, byte_order):
    key = field_entry[0]
    value_offset = int.from_bytes(field_entry[4], byte_order) # offset will always be the last 4 bytes in IFD entry iff value does not fit into 4 bytes
    value_entry = []

    # General case. If the value is contained inside the last 4 bytes of the IFD entry.
    if field_entry[2]*field_entry[3] < 5:
        value = field_entry[4]
        for i in range(0, field_entry[3]):
            value_entry.append(int.from_bytes(value[i*field_entry[2]:i*field_entry[2] + field_entry[2]], byte_order))

    # Bytes can fit into the value, or if it is greater than 4, can be offset, then the individual byte values are taken from there
    elif field_entry[1] == 'BYTE':
        value_entry.append(data[value_offset:value_offset+field_entry[3]])

    # Rationals work differently from the rest. Value is always located somewhere else, and are separated into numerator and denominator
    elif field_entry[1] == 'RATIONAL':
        numerator = int.from_bytes(data[value_offset:value_offset+4], byteorder=byte_order)
        denominator = int.from_bytes(data[value_offset+4:value_offset+8], byteorder=byte_order)
        value_entry = [float(numerator/denominator)]

    # The value will be stored at the offset, until the number of values
    elif field_entry[1] == 'ASCII':
        if field_entry[3] <= 4:
            value_entry = [bytes.decode(each, 'ascii') for each in field_entry[4]]
        else:
            value_entry = [bytes.decode(data[value_offset:value_offset + (field_entry[3]-1)], 'ascii')]

    # Any other case, where the values are not in the 4 byte value/offset.
    else:
        for m in range(0, field_entry[3]):
            value_entry.append(int.from_bytes(data[value_offset + m*field_entry[2]: value_offset + m*field_entry[2] + field_entry[2]], byteorder=byte_order))
    return {key:value_entry}


# Extracting the RGB values of the strips of data
def extract_image(data, field_values, byte_order):
    image_width = field_values[256][0]
    image_length = field_values[257][0]
    strip_offset = field_values[273]
    strip_byte_counts = field_values[279]
    rgb_array = []
    img = []

    for i in range(0, len(strip_offset)): # for each strip
        for j in range(0, strip_byte_counts[i], 3):
            rgb_array.append([data[strip_offset[i] + j], data[1 + strip_offset[i] + j], data[2 + strip_offset[i] + j]])

    for k in range(0, image_length*image_width, image_width): # all the individual lists
        sublist = rgb_array[k:k + image_width]
        img.append(sublist)

    return img

if __name__ == '__main__':

    # FUNCTION 1 - load_file()
    print('FUNCTION 1')
    file_name = 'squares_small_01.tif'
    print(type(file_name))
    data, info = load_file(file_name)
    print(data)
    print(info)
    print(type(data))
    print(len(data))
    print(type(info))
    print()
    # FUNCTION 2 - get_file_header()
    print('FUNCTION 2')
    print(type(data))
    byte_order, ifd_offset = get_file_header(data)
    print(byte_order)
    print(ifd_offset)
    print(type(byte_order))
    print(type(ifd_offset))
    print()
    # FUNCTION 3 - extract_ifd_entries()
    print('FUNCTION 3')
    print(type(data))
    print(type(byte_order))
    print(type(ifd_offset))
    ifd_entries, ifd_entries_N = extract_ifd_entries(data, byte_order, ifd_offset)
    print(ifd_entries)
    print(ifd_entries_N)
    print(type(ifd_entries))
    print(type(ifd_entries[0]))
    print(type(ifd_entries_N))
    print()
    # FUNCTION 4 - extract_ifd_entry()
    print('FUNCTION 4')
    print(type(ifd_entries[0]))
    print(type(byte_order))
    field_entries = []
    for i in range(0, ifd_entries_N):
        field_entries.append(extract_ifd_entry(ifd_entries[i], byte_order))
    print(field_entries)
    print(type(extract_ifd_entry(ifd_entries[0], byte_order)))
    print('--')
    for i in field_entries[0]:
        print(type(i))
    print('--')
    print()
    # FUNCTION 5 - extract_field_values()
    field_values = dict()
    print('FUNCTION 5')
    print(type(data))
    print(type(field_entries[0]))
    print(type(byte_order))
    for i in range(0, len(field_entries)):
        field_values.update(extract_field_values(data, field_entries[i], byte_order))
    print(type(field_values))
    single_field_value = extract_field_values(data, field_entries[0], byte_order)
    print(type(single_field_value))
    print('FIELD VALUES')
    for tag, value in field_values.items():
        print(tag, ':', value, '/ types', type(tag), ':', type(value), '/', type(value[0]))
    print()
    # FUNCTION 6 - extract_image()
    print('FUNCTION 6')
    print(type(data))
    print(type(field_values))
    print(type(byte_order))
    img = extract_image(data, field_values, byte_order)
    print(type(img))
    for j in range(0, field_values[257][0]):
        for i in range(0, field_values[256][0]):
            print(f'({img[j][i][0]},{img[j][i][1]},{img[j][i][2]})', end='')
    print()

