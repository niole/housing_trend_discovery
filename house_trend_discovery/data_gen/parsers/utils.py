import re

def parse_table(soup_table) -> dict[str, list[str]]:
    headers = [t.get_text().strip() for t in soup_table.find_all('th')]
    cells = [t.get_text().strip() for t in soup_table.find_all('td')]

    table_width = len(headers)

    # the elements in each column i are len(cells) mod tablewidth + i
    # or i + tablewidth until you run out of cells
    # or iterate over all cell_is, mod by table width to get the column_i that it belongs to
    result = [(h, []) for h in headers]

    for i in range(len(cells)):
        header_i = i % table_width
        result[header_i][1].append(cells[i])

    return dict(result)

def parse_sideways_table(table) -> dict[str, list[str]]:
    top_row_cells = table.find('tr').find_all('td')
    table_width = len(top_row_cells)

    cells = [t.get_text().strip() for t in table.find_all('td')]
    table_map = {}

    # parse sideways table
    for i in range(0, len(cells), table_width):
        header = cells[i]
        table_map[header] = [t.strip() for t in cells[i+1:i+table_width]]

    return table_map

def combine_results(*argv) -> dict:
    res = {}
    for r in argv:
        res.update(r)
    return res

def get_file(filename) -> str:
    with open(filename, 'r') as f:
        return f.read()

def get_nums(s):
    s = s.replace(',', '')
    m = re.search(r'(\d+)', s)
    if m is not None:
        return int(m.group(0))
    return None
