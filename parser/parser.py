def parse(filename):
    rows = []
    with open(filename, 'r') as f:
        header = next(f).strip().split("]")[1][1:].split(",")
        for line in f:
            line = line.strip().split("]")[1][1:].split(",")
            rows.append(line)
    return (header, rows)

def write_csv(parsed_file, out_filename):
    with open(out_filename, 'w') as o:
        o.write(','.join(parsed_file[0]) + '\n')
        for line in parsed_file[1]:
            o.write(','.join(line) + '\n')
