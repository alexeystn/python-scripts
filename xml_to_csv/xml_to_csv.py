import xml.etree.ElementTree as ET
import os
import sys
import csv


input_filename = './XML/ФСЭМ.xml'
output_filename = 'output.csv'


def scan_for_attributes(attr, r):

    if not r.tag in attr.keys():
        attr[r.tag] = set()
    for key in r.keys():
        attr[r.tag].add(key)
    for sub_r in r:
        scan_for_attributes(attr, sub_r)


def scan_for_values(csvw, r, entry):

    if r.tag == 'Section':
        type_str = r.attrib['Type']
        entry[type_str + '.Name'] = r.attrib['Name']
        entry[type_str + '.Code'] = r.attrib['Code']
    else:
        for key in r.keys():
            new_key = r.tag + '.' + key
            entry[new_key] = r.attrib[key]
    if len(r) == 0:
        #if r.tag == 'Content':
        #    return
        if len(r.attrib) == 0:
            return
        csvw.writerow(entry.values())
        return
    for sub_r in r:
        scan_for_values(csvw, sub_r, entry.copy())


def scan_for_sections(sections, r, path=[]):
    
    if r.tag == 'Section':
        path.append(r.attrib['Type'])
    else:
        if len(path) > 0:
            sections.add(tuple(path))
    for sub_r in r:
        scan_for_sections(sections, sub_r, path.copy())


def get_section_columns(sections):
    
    sections = list(sections)
    lens = [len(s) for s in sections]
    full_path = sections[lens.index(max(lens))]
    attrs = ['Code', 'Name']
    result = [ p + '.' + a for p in full_path for a in attrs]

    return result


def get_attribute_columns(attributes):

    result = []
    for tag in attributes:
        if tag == 'Section':
            continue
        for attr in attributes[tag]:
            s = tag + '.' + attr
            result.append(s)
    return result



csvfile = open(output_filename, 'w', encoding='utf-8', newline='')
csvwriter = csv.writer(csvfile, delimiter='\t')

sections = set()
attributes = {}

print(' Загрузка файла ' + input_filename + '... ', end='')
tree = ET.parse(input_filename)
print(' Готово ')

root = tree.getroot()
for dir1 in root:
    for dir2 in dir1:
        scan_for_attributes(attributes, dir2)
        scan_for_sections(sections, dir2)

section_columns = get_section_columns(sections)
attribute_columns = get_attribute_columns(attributes)

print()
keys = section_columns + attribute_columns
entry = {k:'' for k in keys}
for k in keys:
    print(k)

print('\n Запись результата ' + output_filename + '... ', end='')

csvwriter.writerow(entry.keys())
for dir1 in root:
    for dir2 in dir1:
        scan_for_values(csvwriter, dir2, entry.copy())
csvfile.close()
print(' Готово ')

