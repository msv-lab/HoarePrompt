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
    elements = [(elem[0], elem[1], idx, elem[2], elem[3], elem[4]) for idx, elem in enumerate(elements_simple)]
    # Start from the second to last element and move towards the first
    while elements_processed < len(elements):
        # Iterate through the elements of the list from last to first
        for i in range(len(elements) - 1, -1, -1):
            if elements[i] not in elements_processed_list:
                # print(f"Processing element {elements[i]}")
                elements_processed_list.append(elements[i])
                current_element, current_depth, current_id, type, command, movable = elements[i]
                elements_processed += 1
                break
        #if we are allowed to move this element
        if  movable:
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
    elements = [(elem[0], elem[1], elem[3], elem[4], elem[2]) for elem in elements]
    return elements


def sort_post_by_depth(elements):
    elements_processed_list = []
    #make a list total_tree of the  elem[0], elem[1], elem[3] for each element in elements
    total_tree = [(elem[3], elem[1], elem[2], False, elem[4]) for elem in elements]
    elements_processed = 0
    while elements_processed < len(elements):
        # Iterate through the elements of the list from first to last
        for i in range(len(elements)):
            if elements[i] not in elements_processed_list:
                elements_processed_list.append(elements[i])
                current_element, current_depth, type, is_comment, idx = elements[i]
                elements_processed += 1
                break

        # find the index of the element in the total_tree where elem[4] == idx
        j = 0
        while j < len(total_tree) and total_tree[j][4] != idx:
            j += 1
        # We will try to insert the current element in the total_tree list. We move to the right of that list until we find an element with equal or lower depth and we insert the current element before that element(or in the end of the list if we don't find any element with equal or lower depth)
        j+=1

        while j < len(total_tree) and total_tree[j][1] > current_depth:
            j += 1
        total_tree.insert(j, (current_element, current_depth, type, True, idx))

    return total_tree


def print_tree(elements):
     # Clear the contents of the file
    with open("tasks.txt", "w"):
        pass
        unrolled_loop = 1
    for element, depth, type, is_comment, idx in elements:
        # # If the current task is at a higher depth (subtask), increase numbering levels
        # if depth > current_depth:
        #     numbering.append(1)
        # # If the current task is at the same depth, increment the last numbering level
        # elif depth == current_depth:
        #     numbering[-1] += 1
        # # If the current task is at a lower depth, backtrack the numbering levels
        # else:
        #     numbering = numbering[:depth]
        #     numbering[-1] += 1

        # # Format the task numbering based on its depth
        # task_number = ".".join(map(str, numbering))
        indent = " " * (depth * 4)  # Indentation based on depth level
        
        # Print the task with the appropriate numbering and indentation
        #print them in a  file
        #remove the \neline at the end of the command if it exists
        if len(element)>0 and element[-1] == "\n":
            element = element[:-1]
        #here i want to open a file and clear it if it has content
        with open("tasks.txt", "a") as f:
            if is_comment:
                element = element.replace("\n", "\n" + indent+"#")
                # if "the if part of the statement" in type:
                #     print(f"{indent}#State of the program after the if part has been executed: {element}", file=f)
                # if "the else statement of the if-else block" in type:
                #     print(f"{indent}#State of the program after the else part has been executed: {element}", file=f)
                if "a summary of the whole if-else block" in type:
                    print(f"{indent}#State of the program after the if-else block has been executed: {element}", file=f)
                elif "a summary of the whole if block" in type:
                    print(f"{indent}#State of the program after the if block has been executed: {element}", file=f)
                # elif "the try block" in type:
                #     print(f"{indent}#State of the program after the try block has been executed: {element}", file=f)
                # elif "the except block" in type:
                #     print(f"{indent}#State of the program after the except block has been executed: {element}", file=f)
                elif "a summary of the whole try-except block" in type:
                    print(f"{indent}#State of the program after the try-except block has been executed: {element}", file=f)
                # elif "the summary of unrolled_loop" in type:
                #     print(f"{indent}#State of the program after the loop has been unrolled {unrolled_loop} times: {element}", file=f)
                #     unrolled_loop += 1
                elif "a summary of the total loop" in type:
                    print(f"{indent}#State of the program after the loop has been executed: {element}", file=f)
                    unrolled_loop =1
                elif 'the summary for the whole function' in type:
                    print(f"{indent}#Overall this is what the function does: {element}", file=f) 
                # elif "simple command" in type:
                #     print(f"{indent}#State of the program here: {element}", file=f)
                elif "return statement" in type:
                    print(f"{indent}#State of the program after the return statement: {element}", file=f)
                elif "summary of total for loop" in type:
                    print(f"{indent}#State of the program after the  for loop has been executed: {element}", file=f)
                else:
                    pass

               
        #put all the contents of tasks.txt in a string
            else:
                if len(element)>0 :
                    print(f"{indent}{element}", file=f)
        #put all the contents of tasks.txt in a string
        
        # print(f"{indent} {command}")
        # print(f"#{indent} #Task_{task_number}: Type: {type}. Postcondition: {element}")

       
        
    with open("tasks.txt", "r") as f:
            tasks = f.read()
    return tasks



# Example list of tuples (string, depth)
# elements = [g, depth)
# elements = [
#     ("A", 3, "aaa"),
#     ("B", 1, "llll"),
#     ("C", 2, "kkkk"),
#     ("D", 3, "jjjj"),
#     ("D", 6, "hhhh"),
#     ("E", 4, "gggg"),
#     ("F", 2, "ffff")
# ]

# Add unique identifiers to each element by appending the index as the third item in the tuple

# Applying the move function
# modified_elements = sort_tasks_by_depth(elements)

# Removing the unique identifier for display if needed
# final_elements = [(elem[0], elem[1], elem[3]) for elem in modified_elements]

# Printing the modified list
# for item in modified_elements:
#     print(item)

def pretty_print_tasks(elements):
    """
    Pretty prints a sorted list of tasks with hierarchical numbering based on depth.

    :param elements: List of tuples where each tuple contains (string, depth).
    :return: None
    """
    numbering = []  # Keeps track of the numbering for each depth level
    current_depth = -1
    # Clear the contents of the file
    with open("tasks.txt", "w"):
        pass

    for element, depth, type, command in elements:
        # # If the current task is at a higher depth (subtask), increase numbering levels
        # if depth > current_depth:
        #     numbering.append(1)
        # # If the current task is at the same depth, increment the last numbering level
        # elif depth == current_depth:
        #     numbering[-1] += 1
        # # If the current task is at a lower depth, backtrack the numbering levels
        # else:
        #     numbering = numbering[:depth]
        #     numbering[-1] += 1

        # # Format the task numbering based on its depth
        # task_number = ".".join(map(str, numbering))
        indent = " " * (depth * 4)  # Indentation based on depth level

        # Print the task with the appropriate numbering and indentation
        #print them in a  file
        #remove the \neline at the end of the command if it exists
        if len(command)>0 and command[-1] == "\n":
            command = command[:-1]
        #here i want to open a file and clear it if it has content
        with open("tasks.txt", "a") as f:
            if len(command)>0:
                print(f"{indent}#This is {type} and its postcondition is : {element}", file=f)
                print(f"{indent}{command}", file=f)
            elif "summary" in type:
                print(f"{indent}#This is {type} and its total postcondition is : {element}", file=f)
            elif len(element)==0:
                print(f"{indent}#This is {type}", file=f)
            else :
                print(f"{indent}#This is {type} and its total postcondition is : {element}", file=f)
        #put all the contents of tasks.txt in a string
        
        # print(f"{indent} {command}")
        # print(f"#{indent} #Task_{task_number}: Type: {type}. Postcondition: {element}")

        # Update the current depth for the next iteration
        current_depth = depth
    with open("tasks.txt", "r") as f:
            tasks = f.read()
    return tasks


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
