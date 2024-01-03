import os
import re
import csv
import sys

def remove_duplicates_with_location(items):
    unique_items = []
    unique_locations = []
    duplicate_items_count = 0
    duplicate_items = []
    
    for item, location in items:
        if item not in unique_items:
            unique_items.append(item)
            unique_locations.append(location)
        else:
            duplicate_items_count += 1
            duplicate_items.append(item)
            duplicate_items.append(location)
    
    return unique_items, unique_locations, duplicate_items_count, duplicate_items

def write_to_csv(filename, headers, data):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

def find_rest_endpoints(directory):
    rest_endpoints = []
    rest_locations = []
    num_endpoints = 0  
    
    for root, dirs, files in os.walk(directory):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')  # Skip the node_modules folder
        if 'test' in dirs:
            dirs.remove('test')  # Skip the test folder
        for file in files:
            if file.endswith((".js", ".ts")):
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    content = f.readlines()
                    for line_num, line in enumerate(content, start=1):
                        if not line.strip().startswith("//") and not line.strip().startswith("#"):
                            matches = re.findall(r"(\w+\.(get|post|put|patch|delete|use)\(['\"][/](.*?)['\"](?:\s*,\s*async\s*\(\s*req\s*,\s*res\s*\))?(?:\s*,\s*(.*?)\))?)", line)
                            for match in matches:
                                endpoint = match[1].upper() + " /" + match[2]
                                rest_endpoints.append(endpoint)
                                rest_locations.append((filepath, line_num))
                                num_endpoints += 1 
    
    return num_endpoints, rest_endpoints, rest_locations

def find_graphql_queries(directory):
    graphql_queries = []
    graphql_locations = []
    num_queries = 0

    for root, dirs, files in os.walk(directory):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')  # Skip the node_modules folder
        if 'test' in dirs:
            dirs.remove('test')  # Skip the test folder
        for file in files:
            if file.endswith((".js", ".ts")):
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    content = f.read()
                    matches = re.findall(r"type Query {[\s\S]*?}", content)
                    for match in matches:
                        #print (match)
                        #queries = re.findall(r"(\w+)[\(|:]", match) 
                        #queries = re.findall(r"(?<![\s,])\b(?<![\(])\b(\w+)[\(|:]", match) # queries = re.findall(r"(?<![(\s,])\b(\w+)[\(|:]", match)
                        queries = re.findall(r"(?:^|\})\s*(\w+)[\(|:]", match, re.MULTILINE)
                        for query in queries:
                            graphql_queries.append("Query " + query)
                            graphql_locations.append((filepath, 0))
                            num_queries += 1
                    matches = re.findall(r"gql`[\s\S]*?query\s+(\w+)", content)
                    for match in matches:
                        graphql_queries.append("Query " + match)
                        graphql_locations.append((filepath, 0))
                        num_queries += 1

    return num_queries, graphql_queries, graphql_locations

def find_graphql_mutations(directory):
    graphql_mutations = []
    graphql_locations = []
    num_mutations = 0

    for root, dirs, files in os.walk(directory):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')  # Skip the node_modules folder
        if 'test' in dirs:
            dirs.remove('test')  # Skip the test folder
        for file in files:
            if file.endswith((".js", ".ts")):
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    content = f.read()
                    matches = re.findall(r"type Mutation {[\s\S]*?}", content)
                    for match in matches:
                        mutations = re.findall(r"(?:^|\})\s*(\w+)[\(|:]", match, re.MULTILINE)
                        for mutation in mutations:
                            graphql_mutations.append("Mutation " + mutation)
                            graphql_locations.append((filepath, 0))
                            num_mutations += 1
                    matches = re.findall(r"gql`[\s\S]*?mutation\s+(\w+)", content)
                    for match in matches:
                        graphql_mutations.append("Mutation " + match)
                        graphql_locations.append((filepath, 0))
                        num_mutations += 1

    return num_mutations, graphql_mutations, graphql_locations


if len(sys.argv) > 1:
    directory = sys.argv[1]
else:
    print("Please provide the directory path as a command line argument.")
    sys.exit(1)

num_queries, queries, query_locations = find_graphql_queries(directory)
num_mutations, mutations, mutation_locations = find_graphql_mutations(directory)
num_endpoints, endpoints, rest_locations = find_rest_endpoints(directory)

queries, query_locations, query_duplicate_count, query_dup_items = remove_duplicates_with_location(zip(queries, query_locations))
mutations, mutation_locations, mutation_duplicate_count, mutation_dup_items = remove_duplicates_with_location(zip(mutations, mutation_locations))

num_queries -= query_duplicate_count
num_mutations -= mutation_duplicate_count

write_to_csv("queries.csv", ["Query", "Location"], zip(queries, query_locations))
write_to_csv("mutations.csv", ["Mutation", "Location"], zip(mutations, mutation_locations))
write_to_csv("rest_endpoints.csv", ["Endpoint", "Location"], zip(endpoints, rest_locations))

print(f"Total number of GraphQL queries found: {num_queries}")
print(f"Total number of GraphQL mutations found: {num_mutations}")
print(f"Total number of REST endpoints found: {num_endpoints}")
print(f"Number of duplicate GraphQL queries removed: {query_duplicate_count}")
print(f"Number of duplicate GraphQL mutations removed: {mutation_duplicate_count}")

"""
for query in query_dup_items:
    print(query)

for mutation in mutation_dup_items:
    print(mutation)
"""

#num_operations, operations, graphql_locations = find_graphql_operations(directory)

#for endpoint, location in zip(endpoints, rest_locations):
 #   print(f"Endpoint: {endpoint}" + "\n" + f"Location: {location}" + "\n")

#for operation, location in zip(operations, graphql_locations):
 #   print(f"GraphQL Operation: {operation}" + "\n" + f"Location: {location}" + "\n")

#print(f"Total number of REST endpoints found: {num_endpoints}")
#print(f"Total number of GraphQL operations found: {num_operations}")

