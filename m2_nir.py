import clang.cindex
import json
import copy

index = clang.cindex.Index.create()

def parse_cpp_code_to_json(cpp_code):
    rows = []
    tu = index.parse('tmp.cpp', args=['-std=c++11'], unsaved_files=[('tmp.cpp', cpp_code)])
    current_row = {"id": None, "code": None}

    for token in tu.get_tokens(extent=tu.cursor.extent):
        if token.location.file.name == 'tmp.cpp':
            if current_row["id"] != token.location.line:
                if current_row["id"] is not None:
                    rows.append(current_row)
                current_row = {"id": token.location.line, "code": token.spelling + " "}
            else:
                current_row["code"] += token.spelling + " "

    if current_row["id"] is not None:
        rows.append(current_row)

    result = {"code": {"rows": rows}}
    return json.dumps(result, indent=4)

def extract_functions(json_result):
    result_dict = json.loads(json_result)
    code_rows = result_dict["code"]["rows"]
    functions = {}
    current_function = None

    i = 0
    while i < len(code_rows):
        row = code_rows[i]
        if "code" in row:
            if "(" in row["code"] and ")" in row["code"] and "{" in row["code"]:
                func_name = row["code"].split("(")[0].strip().split()[-1]
                func_args_str = row["code"].split("(")[1].split(")")[0].strip()
                if func_args_str:
                    func_args = func_args_str.split(",")
                    func_args = [arg.strip().split()[-1] for arg in func_args]
                else:
                    func_args = []
                functions[func_name] = {"args": func_args, "body": []}
                current_function = func_name
                i += 1
                brace_count = 1
                while brace_count > 0 and i < len(code_rows):
                    inner_row = code_rows[i]
                    if "{" in inner_row["code"]:
                        brace_count += 1
                    if "}" in inner_row["code"]:
                        brace_count -= 1
                    if brace_count > 0:
                        functions[current_function]["body"].append(inner_row)
                    i += 1
            else:
                i += 1

    return functions

def filter_main_code(json_result):
    result_dict = json.loads(json_result)
    code_rows = result_dict["code"]["rows"]
    main_code_rows = []
    inside_main = False

    for row in code_rows:
        if "code" in row:
            if "main" in row["code"] and "(" in row["code"]:
                inside_main = True
            if inside_main:
                main_code_rows.append(row)
            if "}" in row["code"]:
                inside_main = False

    main_code_json = {"code": {"rows": main_code_rows}}
    return json.dumps(main_code_json, indent=4)

def transform_json(functions):
    json_result = functions["main"]
    code_rows = json.loads(json.dumps(json_result["body"], indent=4))
    #code_rows = result_dict["code"]["rows"]
    transformed_code_rows = []
    new_code_rows = []
    for row in code_rows:
        if "code" in row:
            new_code_rows.append(row)
            for func_name, func_details in functions.items():
                if func_name + " (" in row["code"]:
                    new_code_rows.pop()
                    args = row["code"].split(func_name + " (")[1].split(")")[0].split(",")
                    args = [arg.strip() for arg in args]
                    param_map = {param: arg for param, arg in zip(func_details["args"], args)}
                    for func_row in func_details["body"]:
                        new_func_row = func_row.copy()
                        for param_name, arg_name in param_map.items():
                            new_func_row["id"] = row["id"]
                            new_func_row["code"] = new_func_row["code"].replace(param_name, arg_name)
                        new_code_rows.append(new_func_row)
                    break
    # for row in code_rows:
    #     if "code" in row:
    #         new_code_rows.append(row)
    #         for func_name, func_details in functions.items():
    #             if "for" + " (" in row["code"]:
    #                 new_code_rows.pop()
    #                 args = row["code"].split("for" + " (")[1].split(")")[0].split(";")
    #                 args = [arg.strip() for arg in args]
    #                 param_map = {param: arg for param, arg in zip(func_details["args"], args)}
    #                 for func_row in func_details["body"]:
    #                     new_func_row = func_row.copy()
    #                     for param_name, arg_name in param_map.items():
    #                         new_func_row["id"] = row["id"]
    #                         new_func_row["code"] = new_func_row["code"].replace(param_name, arg_name)
    #                     new_code_rows.append(new_func_row)
    #                 break

    # for row in code_rows:
    #     if "code" in row:
    #         new_code_rows.append(row)
    #         for func_name, func_details in functions.items():
    #             if "if" + " (" in row["code"]:
    #                 new_code_rows.pop()
    #                 args = row["code"].split(func_name + " (")[1].split(")")[0].split("==")
    #                 args = [arg.strip() for arg in args]
    #                 param_map = {param: arg for param, arg in zip(func_details["args"], args)}
    #                 for func_row in func_details["body"]:
    #                     new_func_row = func_row.copy()
    #                     for param_name, arg_name in param_map.items():
    #                         new_func_row["id"] = row["id"]
    #                         new_func_row["code"] = new_func_row["code"].replace(param_name, arg_name)
    #                     new_code_rows.append(new_func_row)
    #                 break

                    

    for row in new_code_rows:
        if "code" in row:
            if "malloc" in row["code"]:
                var_declaration = row["code"].split("=")[0].strip()
                varname = var_declaration.split()[-1]
                new_row = {"id": row["id"], "varname": varname, "value": "new"}
                transformed_code_rows.append(new_row)
            elif "delete" in row["code"]:
                var_declaration = row["code"].split("=")[0].strip()
                varname = var_declaration.split()[-1]
                new_row = {"id": row["id"], "varname": varname, "value": "delete"}
                transformed_code_rows.append(new_row)
            elif "=" in row["code"]:
                if "->" in row["code"]:
                    parts = row["code"].split("->")
                    varname = parts[0].strip()
                    field_op_value = parts[1].split("=")
                    field = field_op_value[0].strip()
                    value = field_op_value[1].strip().split(";")[0] if len(field_op_value) > 1 else None
                    new_row = {
                        "id": row["id"],
                        "varname": varname,
                        "field": {
                            "f": field,
                            "op": "->",
                            "value": value
                        }
                    }
                else:
                    parts = row["code"].split("=")
                    varname = parts[0].strip()
                    value = parts[1].strip().split(";")[0]
                    new_row = {
                        "id": row["id"],
                        "varname": varname,
                        "value": value.replace(" ", "")
                    }
                transformed_code_rows.append(new_row)
            else:
                transformed_code_rows.append(row)

    transformed_json_result = {"code": {"rows": transformed_code_rows}}
    return json.dumps(transformed_json_result, indent=4)

def clear_json(json_result):
    result_dict = json.loads(json_result)
    code_rows = result_dict["code"]["rows"]
    updated_code_rows = [row for row in code_rows if "code" not in row]
    result_dict["code"]["rows"] = updated_code_rows
    return json.dumps(result_dict, indent=4)

def analyze_memory_edges(json_data, result):
    edges = []  
    pointers = []
    def add_edge(varname, edge):
        edges.append([varname, edge])
    for row in json_data['code']['rows']:
        varname = row['varname']

        if 'value' in row:
            value = row['value']
            if varname in pointers:
                for edge in edges:
                    if edge[0] == varname:
                        edges.remove(edge)
            if value == 'new':
                ptr_name = varname.split()[-1]
                add_edge(ptr_name, f'n{row["id"]}')
            elif ' * ' in row['varname']:
                pointers.append(varname.split('* ')[-1].strip())
            elif value in pointers:
                for edge in edges:
                    if edge[0] == value:
                        value = edge[1]
                        break
                add_edge(varname, value)
        elif 'field' in row:
            field = row['field']
            if field['f'] == 'nx':
                if varname in pointers:
                    for edge in edges:
                        if edge[0] == varname:
                            varname = edge[1]
                value = field['value'].split()[-1]
                if value in pointers:
                    for edge in edges:
                        if edge[0] == value:
                            value = edge[1]
                add_edge(varname, value)
        

        elif 'field' in row:
            if row['field'] == 'nx':
                for key in edges.keys():
                    edges[key] = [edge for edge in edges[key] if not any(f'n{row["id"]}' in link for link in edge)]

        print(f'{row["id"]} строка - {edges}')


        def replace_nullptr(edges, pointers):
            def replace(edge):
                if edge[1] == 'nullptr':
                    return pointers[0] if pointers else None
                return edge[1]

            for edge in edges:
                edge[1] = replace(edge)

        replace_nullptr(edges, pointers)
        result.append([row, copy.deepcopy(edges)])
        print("RESULT")
        print(edges)
        
    return edges
# cpp_code = """
# struct ListNode {
#     int nValue;
#     ListNode* nx;
# };

# void initialize(ListNode* pNode, ListNode* pNextInit, int nValInit) {
#     pNode->nx = pNextInit;
#     pNode->nValue = nValInit;
# }

# int main() {
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     for(int i = 0; i < 2; i++)
#     {
#         tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#         initialize(tmp, nullptr, i);
#         elemH = tmp;
#     }
#     tmp = nullptr
# }
# """

# cpp_code = """
# struct ListNode {
#     int nValue;
#     ListNode* nx;
# };

# void initialize(ListNode* pNode, ListNode* pNextInit, int nValInit) {
#     pNode->nx = pNextInit;
#     pNode->nValue = nValInit;
# }

# int main() {
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     for(int i = 0; i < 2; i++)
#     {
#         tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#         initialize(tmp, elemH, i);
#         elemH = tmp;
#     }
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, elemH, 3);
#     tmp = nullptr
# }
# """

# cpp_code = """
# struct ListNode {
#     int nValue;
#     ListNode* nx;
# };

# void initialize(ListNode* pNode, ListNode* pNextInit, int nValInit) {
#     pNode->nx = pNextInit;
#     pNode->nValue = nValInit;
# }

# int main() {
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     for(int i = 0; i < 2; i++)
#     {
#         tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#         initialize(tmp, elemH, i);
#         elemH = tmp;
#     }
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, elemH, 3);
#     elemH = tmp;
#     tmp = nullptr
# }
# """

# cpp_code = """
# struct ListNode {
#     int nValue;
#     ListNode* nx;
# };

# void initialize(ListNode* pNode, ListNode* pNextInit, int nValInit) {
#     pNode->nx = pNextInit;
#     pNode->nValue = nValInit;
# }

# int main() {
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, nullptr, 10);
#     elemH = tmp;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     if(elemH == nullptr){
#          initialize(tmp, elemH, 20);
#          elemH = tmp;
#     }
#     tmp = nullptr
# }
# """
# int main() {
#     int i = 0;
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, nullptr, 10);
#     elemH = tmp;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     if(i == 0){
#          initialize(tmp, elemH, 20);
#          elemH = tmp;
#     }
#     tmp = nullptr
# }
# """
# cpp_code = """
# struct ListNode {
#     int nValue;
#     ListNode* nx;
# };

# void initialize(ListNode* pNode, ListNode* pNextInit, int nValInit) {
#     pNode->nx = pNextInit;
#     pNode->nValue = nValInit;
# }

# int main() {
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, nullptr, 10);
#     elemH = tmp;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, elemH, 20);
#     tmp = nullptr
# }
# """
# cpp_code = """
# struct ListNode {
#     int nValue;
#     ListNode* nx;
# };

# void initialize(ListNode* pNode, ListNode* pNextInit, int nValInit) {
#     pNode->nx = pNextInit;
#     pNode->nValue = nValInit;
# }

# int main() {
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, nullptr, 10);
#     elemH = tmp;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, elemH, 20);
#     elemH = tmp;
#     tmp = nullptr
# }
# """
cpp_code = """
struct ListNode {
    int nValue;
    ListNode* nx;
};

void initialize(ListNode* pNode, ListNode* pNextInit, int nValInit) {
    pNode->nx = pNextInit;
    pNode->nValue = nValInit;
}

int main() {
    struct NodeInt* elemH = nullptr;
    struct NodeInt* tmp = nullptr;
    tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
    initialize(tmp, nullptr, 10);
    elemH = tmp;
    tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
    initialize(tmp, elemH, 20);
    tmp = nullptr;
}
"""

json_result = parse_cpp_code_to_json(cpp_code)
print(json_result)
print("1////////////////////////////")

functions = extract_functions(json_result)
#filtered_json_result = filter_main_code(json_result)
#print(filtered_json_result)

print("/2////////main/////////////")
print(functions["main"])


print("/2/////////init////////////")
print(functions["initialize"])


transformed_json_result = transform_json(functions)
json_res = clear_json(transformed_json_result)
print(json_res)
data = json.loads(json_res)
print("/3///////////////////////////")

#json_res_with_functions = handle_functions(json_res, functions)
#print(json_res_with_functions)
#print("/4///////////////////////////")

#json_res_with_if = handle_if_statements(json_res_with_functions)
#print(json_res_with_if)
#print("/5///////////////////////////")

#json_res_with_cycle = handle_cycle_statements(json_res_with_if)
#print(json_res_with_if)
#print("/6///////////////////////////")

#data = json.loads(json_res_with_cycle)
building_process = []
edges = analyze_memory_edges(data, building_process)



def transform_to_cnf(arr):
    var_map = {}
    cnf_formula = []
    var_counter = 1
    for pair in arr:
        if pair[0] not in var_map:
            var_map[pair[0]] = var_counter
            var_counter += 1
        if pair[1] not in var_map:
            var_map[pair[1]] = var_counter
            var_counter += 1
        cnf_pair = [-var_map[pair[0]], var_map[pair[1]]]
        cnf_formula.append(cnf_pair)
    return cnf_formula, var_map


def transform_to_cnf_1(arr):
    var_map = {}
    cnf_formula = []
    var_counter = 1
    for pair in arr:
        if pair[0] not in var_map:
            var_map[pair[0]] = var_counter
            var_counter += 1
        if pair[1] not in var_map:
            var_map[pair[1]] = var_counter
            var_counter += 1
        cnf_pair = [-var_map[pair[0]], var_map[pair[1]]]
        cnf_formula.append(cnf_pair)
    return cnf_formula, var_map


def add_black_and_white_assignments(cnf_formula):
    black_assignment = []
    white_assignment = []
    variables = set()

    for clause in cnf_formula:
        for literal in clause:
            variables.add(abs(int(literal)))

    for var in variables:
        black_assignment.append(var)
        white_assignment.append(-var)

    cnf_formula.append(black_assignment)
    cnf_formula.append(white_assignment)

    return cnf_formula

cnf_formula, var_map = transform_to_cnf(edges)
print("var_map:", var_map)
print("CNF формула:", cnf_formula)

cnf_formula_with_assignments = add_black_and_white_assignments(cnf_formula)
print("CNF формула с конъюнкциями 'чёрного' и 'белого' решений:", cnf_formula_with_assignments)

import pycosat

solution = pycosat.solve(cnf_formula_with_assignments)
print("Решение найдено:", solution)

def find_leaked_obj_num(solution):
    for num in solution:
        if num < 0:
            return abs(num)
    return None

def find_leaked_obj(solution, target):
    for obj in solution:
        if len(obj) > 1 and obj[1] == target:
            return obj
    return None 

def find_leaked_obj_1(solution, target):
    for key, value in solution.items():
        if isinstance(value, int) and abs(value) == target:
            return key
    return None  

if solution != "UNSAT":
    print("Решение найдено:", solution)
    leaked_num = find_leaked_obj_num(solution)
    cnf_formula = []
    cnf_formula_with_assignments = []
    building_process.reverse()

    cnf_formula,  var_map = transform_to_cnf(building_process[0][1])
    leaked_obj = find_leaked_obj_1(var_map, leaked_num)
    print("Потерян объект ", leaked_obj)

    for backup in  building_process:
        cnf_formula,  var_map = transform_to_cnf(backup[1])
        #cnf_formula_with_assignments = add_black_and_white_assignments(cnf_formula)
        # solution = pycosat.solve(cnf_formula_with_assignments)
        # if solution == "UNSAT":
        #     print("Строка с ошибкой:", backup[0]["id"])

        #leaked_obj = first_key_with_modulus(var_map, leaked_num)
        if find_leaked_obj(backup[1], leaked_obj) is not None:
            print("Строка с ошибкой:", backup[0]["id"])
            break




