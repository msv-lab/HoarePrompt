def sort_tasks_by_depth(elements_simple):
    """
    Move elements leftwards in the list based on depth, stopping when an element encounters
    another element with a lower depth. The order of elements with the same depth is preserved 
    based on their original position.

    :param elements: List of tuples where each tuple contains (string, depth, id).
    :return: The modified list.
    """
    elements_processed_list = []
    elements_processed = 0
    elements = [(elem[0], elem[1], idx) for idx, elem in enumerate(elements_simple)]
    # Start from the second to last element and move towards the first
    while elements_processed < len(elements):
        # Iterate through the elements of the list from last to first
        for i in range(len(elements) - 1, -1, -1):
            if elements[i] not in elements_processed_list:
                # print(f"Processing element {elements[i]}")
                elements_processed_list.append(elements[i])
                current_element, current_depth, current_id = elements[i]
                elements_processed += 1
                break

        # Move the current element leftwards until we encounter an element with a lower depth
        j = i
        while j > 0 and elements[j - 1][1] > current_depth:
            j -= 1

        # If we found a new position, move the element
        if j != i:
            # print(f"Moving element {elements[i]} to position {j}")
            elements.insert(j, elements.pop(i))
            # print(f"New list: {elements}")
    #remove the third element from the tuple
    elements = [(elem[0], elem[1]) for elem in elements]
    return elements


# Example list of tuples (string, depth)
elements = [
    ("A", 3),
    ("B", 1),
    ("C", 2),
    ("D", 3),
    ("D", 6),
    ("E", 4),
    ("F", 2)
]

# Add unique identifiers to each element by appending the index as the third item in the tuple

# Applying the move function
# modified_elements = sort_tasks_by_depth(elements)

# # Removing the unique identifier for display if needed
# final_elements = [(elem[0], elem[1]) for elem in modified_elements]

# # Printing the modified list
# for item in final_elements:
#     print(item)

def pretty_print_tasks(elements):
    """
    Pretty prints a sorted list of tasks with hierarchical numbering based on depth.

    :param elements: List of tuples where each tuple contains (string, depth).
    :return: None
    """
    numbering = []  # Keeps track of the numbering for each depth level
    current_depth = 0

    for element, depth in elements:
        # If the current task is at a higher depth (subtask), increase numbering levels
        if depth > current_depth:
            numbering.append(1)
        # If the current task is at the same depth, increment the last numbering level
        elif depth == current_depth:
            numbering[-1] += 1
        # If the current task is at a lower depth, backtrack the numbering levels
        else:
            numbering = numbering[:depth]
            numbering[-1] += 1

        # Format the task numbering based on its depth
        task_number = ".".join(map(str, numbering))
        indent = " " * (depth * 4)  # Indentation based on depth level

        # Print the task with the appropriate numbering and indentation
        print(f"{indent}Task_{task_number} {element}")

        # Update the current depth for the next iteration
        current_depth = depth


# # Example sorted list of tuples (string, depth)
# elements = [
#     ("A", 2),
#     ("B", 3),
#     ("C", 3),
#     ("D", 4),
#     ("E", 2),
#     ("F", 3),
#     ("X", 4),
#     ("G", 4)
# ]

# 
# # Print the tasks with hierarchical numbering
# pretty_print_tasks(modified_elements)
