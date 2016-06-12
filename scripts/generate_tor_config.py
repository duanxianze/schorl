start = 9054
end = 9154

def generate_tor_config(start, end):
    with open('torrc', 'w+') as f:
        for i in range(start, end+1):
            f.write("SOCKSPort {}\n".format(str(i)))

generate_tor_config(start, end)
