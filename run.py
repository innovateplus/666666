#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import io
import os
import sys
from collections import defaultdict

def main():
    json_path = os.path.join(os.path.dirname(__file__), 'all.json')
    txt_path = os.path.join(os.path.dirname(__file__), 'all.txt')

    # 读取 JSON
    try:
        with io.open(json_path, 'r', encoding='utf-8') as f:
            data_all = json.load(f)
    except FileNotFoundError:
        print(f"错误：未找到文件 {json_path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"错误：解析 JSON 失败: {e}", file=sys.stderr)
        return 1

    if not isinstance(data_all, dict) or 'data' not in data_all:
        print("错误：all.json 中缺少顶层 'data' 字段或格式不正确", file=sys.stderr)
        return 1

    entries = data_all.get('data', [])
    # 存放被筛选出的条目（按原顺序）
    filtered = []

    for item in entries:
        # 跳过格式不对的条目
        if not isinstance(item, dict):
            continue
        ports = item.get('port')
        ip = item.get('ip')
        locations = item.get('locations', {})
        # 确保 port 是可迭代的，ip 和 locations 存在
        if ip is None or ports is None or not isinstance(ports, (list, tuple)):
            continue
        # 如果包含 443，则记录该条目
        if 443 in ports:
            # 获取字段（使用空字符串作为缺省值以避免 None 写入）
            region = locations.get('region', '') if isinstance(locations, dict) else ''
            city = locations.get('city', '') if isinstance(locations, dict) else ''
            cca2 = locations.get('cca2', '') if isinstance(locations, dict) else ''
            iata = locations.get('iata', '') if isinstance(locations, dict) else ''
            filtered.append({
                'ip': ip,
                'region': region,
                'city': city,
                'cca2': cca2,
                'iata': iata,
            })

    # 统计每个 iata 的序号（按照 filtered 的出现顺序）
    iata_counts = defaultdict(int)
    lines = []
    cnt = 0
    for entry in filtered:
        iata = entry.get('iata', '')
        iata_counts[iata] += 1
        cnt += 1
        index = iata_counts[iata]
        # 组装行：ip:443#region|city|cca2|iata|index
        line = f"{entry.get('ip', '')}:443#{entry.get('region','')}|{entry.get('city','')}|{entry.get('cca2','')}-{entry.get('iata','')}-{index}号节点|总{cnt}号节点"
        lines.append(line)

    # 写入输出文件（utf-8，无 BOM）
    try:
        with io.open(txt_path, 'w', encoding='utf-8') as f:
            for ln in lines:
                f.write(ln + '\n')
    except OSError as e:
        print(f"错误：写入文件失败: {e}", file=sys.stderr)
        return 1

    print(f"已写入 {len(lines)} 条到 {txt_path}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
