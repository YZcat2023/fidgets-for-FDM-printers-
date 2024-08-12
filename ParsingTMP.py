import re
def parse_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    layer_data = {}  # 保存每一层数据
    current_layer = None  # 当前层标识符
    current_layer_lines = []  # 当前层的所有数据
    for line in lines:
        if line.startswith(';LOC'):  # 每一层开始的标志
            if current_layer is not None:  # 保存上一层的数据
                if current_layer[0] in layer_data:
                    layer_data[current_layer[0]].append((current_layer[1], current_layer_lines))
                else:
                    layer_data[current_layer[0]] = [(current_layer[1], current_layer_lines)]
            # 提取层号和区域号
            current_layer_match = re.search(r';LOC(\d+)', line)
            b_value_match = re.search(r'B(\d+)', line)
            current_layer = (int(current_layer_match.group(1)), int(b_value_match.group(1)) if b_value_match else 0)
            current_layer_lines = [line.strip()]
        else:
            current_layer_lines.append(line.strip())
    if current_layer is not None:  # 保存最后一层的数据
        if current_layer[0] in layer_data:
            layer_data[current_layer[0]].append((current_layer[1], current_layer_lines))
        else:
            layer_data[current_layer[0]] = [(current_layer[1], current_layer_lines)]
    total_regions = sum(len(regions) for regions in layer_data.values())
    print(f"解析出 {len(layer_data)} 层，共 {total_regions} 个区域")
    return layer_data
def calculate_averages(commands):
    x_values = [float(re.search(r'X([\d.]+)', num).group(1)) for num in commands if re.search(r'X([\d.]+)', num)]
    y_values = [float(re.search(r'Y([\d.]+)', num).group(1)) for num in commands if re.search(r'Y([\d.]+)', num)]
    x_avg = sum(x_values) / len(x_values) if x_values else 0
    y_avg = sum(y_values) / len(y_values) if y_values else 0
    return x_avg, y_avg
def calculate_e_total(commands):
    e_values = [float(re.search(r'E([\d.]+)', num).group(1)) for num in commands if re.search(r'E([\d.]+)', num)]
    return sum(e_values)#提取并且e值总和
def filter_data(loc_dict):
    retained_dict = {}  # 保留的层
    removed_regions = 0  # 移除的区域数
    removal_reasons = []  # 移除原因
    keys = sorted(loc_dict.keys())
    for i in range(len(keys) - 1):
        current_layer_key = keys[i]
        next_layer_key = keys[i + 1]
        retained_regions = []
        for current_region in loc_dict[current_layer_key]:
            #二元数组，包含区域id和和命令
            current_region_id, current_commands = current_region
            current_g1_commands = [num for num in current_commands if num.startswith('G1')]#便利，如过命令是以G1开头的就加进这个数组里面
            current_e_total = calculate_e_total(current_g1_commands)

            print(f"层 {current_layer_key}, 区域 {current_region_id} - E 总和: {current_e_total}")

            if current_e_total <= 0.5:
                removed_regions += 1
                removal_reasons.append(f"层 {current_layer_key}, 区域 {current_region_id} 被移除，E总和:"+str(current_e_total))
                continue
            current_x_avg, current_y_avg = calculate_averages(current_g1_commands)
            remove_region = False
            for next_region in loc_dict[next_layer_key]:
                next_region_id, next_commands = next_region
                next_g1_commands = [num for num in next_commands if num.startswith('G1')]
                next_x_avg, next_y_avg = calculate_averages(next_g1_commands)
                print(
                    f"层 {current_layer_key}, 区域 {current_region_id} - X 平均值: {current_x_avg}, Y 平均值: {current_y_avg}")
                print(f"层 {next_layer_key}, 区域 {next_region_id} - X 平均值: {next_x_avg}, Y 平均值: {next_y_avg}")

                if abs(current_x_avg - next_x_avg) < -1 and abs(current_y_avg - next_y_avg) < -1:
                    remove_region = True
                    removal_reasons.append(
                        f"层 {current_layer_key}, 区域 {current_region_id} 被移除: 与层 {next_layer_key}, 区域 {next_region_id} 的 X 或 Y 平均值差值 < 2")
                    break

            if not remove_region:
                retained_regions.append(current_region)
            else:
                removed_regions += 1
        if retained_regions:
            retained_dict[current_layer_key] = retained_regions

    # 保留最后一层，检查E值总和是否大于1
    last_layer_key = keys[-1]
    if last_layer_key in loc_dict:
        last_retained_regions = []
        for region in loc_dict[last_layer_key]:
            region_id, commands = region
            g1_commands = [num for num in commands if num.startswith('G1')]
            e_total = calculate_e_total(g1_commands)
            if e_total >0:
                last_retained_regions.append(region)
            else:
                removed_regions += 1
                removal_reasons.append(f"层 {last_layer_key}, 区域 {region_id} 被移除: E 总和:"+str(e_total))
        if last_retained_regions:
            retained_dict[last_layer_key] = last_retained_regions
    retained_count = sum(len(regions) for regions in retained_dict.values())
    print(f"保留了 {retained_count} 个区域，移除了 {removed_regions} 个区域")
    print("移除原因如下:")
    for reason in removal_reasons:
        print(reason)
    return retained_dict
def write_filtered_file(retained_dict, output_filename):
    with open(output_filename, 'w') as file:
        for key, regions in sorted(retained_dict.items()):
            for region_id, data in regions:
                for line in data:
                    file.write(f'{line}\n')
    print(f"已将保留的区域写入到 {output_filename}")


