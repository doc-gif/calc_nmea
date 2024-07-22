target_filepath = 'data/part2/actual_positions.txt'
output_filepath = target_filepath.split('.')[0] + '_output.txt'


with open(target_filepath) as target_file, open(output_filepath, 'w') as output_file:
    result = ''
    for line in target_file.read().splitlines():
        result += '[' + line + '],\n'

    # 最終行の文字列',\n'を削除
    result = result[:-2]

    output_file.write(result)
