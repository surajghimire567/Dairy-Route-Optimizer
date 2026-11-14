from openpyxl import load_workbook
def read_rows(path):
    wb = ...
    ws = ...
    rows = ...
    header = next(rows)
    result = []
    for row in rows:
        result.append(dict(zip(header, row)))
    return result
data = read_rows("backend/data/latest_one.xlsx")
print(data[:3])
print(type(data[0]["Date"]), type(data[0]["Quantity (kg)"]))