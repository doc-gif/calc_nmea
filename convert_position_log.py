target_filepath = 'data/part1/smartphone_position_log.txt'
output_filepath = target_filepath.split('.')[0] + '_output' + '.txt'

with open(target_filepath, 'r') as target, open(output_filepath, 'w') as output:
    result = ""
    for line in target.read().splitlines():
        if line == '':
            break
        line = line.replace('[', '').replace(']', '').replace(' ', '')[:-1]
        temp = line.split(',')
        result += temp[1] + ',' + temp[0] + '\n'
    output.write(result)
