def sort_tasks_by_depth(elements_simple):
    """
    Sort tasks by depth to create a hierarchical structure.
    Moves elements leftwards in the list based on depth, stopping when encountering 
    another element with a lower depth. Preserves the order of elements with the same depth.

    :param elements_simple: List of tuples containing (string, depth, type, command, movable).
    :return: A sorted list of elements based on depth.
    """
    elements_processed_list = []
    elements_processed = 0

    # Add unique identifiers to each element
    elements = [(elem[0], elem[1], idx, elem[2], elem[3], elem[4]) for idx, elem in enumerate(elements_simple)]


    # Process each element bottom to top
    while elements_processed < len(elements):
        # Iterate through the elements of the list from last to first
        for i in range(len(elements) - 1, -1, -1):
            if elements[i] not in elements_processed_list:
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
                elements.insert(j, elements.pop(i))   
    
    # Remove the unique identifier before returning
    elements = [(elem[0], elem[1], elem[3], elem[4], elem[2]) for elem in elements]
    return elements


def sort_post_by_depth(elements):
    """
    Create a structured hierarchy for postconditions based on depth.

    :param elements: List of tuples containing (string, depth, type, command, index).
    :return: A structured list representing the code tree.
    """
    elements_processed_list = []
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

        # Find the corresponding element in the tree and determine its position
        j = 0
        while j < len(total_tree) and total_tree[j][4] != idx:
            j += 1
        # We will try to insert the current element in the total_tree list. We move to the right of that list until we find an element with equal or lower depth and we insert the current element before that element(or in the end of the list if we don't find any element with equal or lower depth)
        j+=1

        while j < len(total_tree) and total_tree[j][1] > current_depth:
            j += 1
        total_tree.insert(j, (current_element, current_depth, type, True, idx))

    return total_tree


def print_tree(elements, annotate_prints=True):
    """
    Format the code tree with comments and write it to a file.

    :param elements: List of tuples containing (element, depth, type, is_comment, index).
    :return: A string representation of the formatted code tree.
    """

     # Clear the contents of the file
    with open("tasks.txt", "w"):
        pass # Clear the contents of the file
        
    for element, depth, type, is_comment, idx in elements:
       
        indent = " " * (depth * 4)  # Indentation based on depth level
        
        # Remove trailing newline from the element
        if len(element)>0 and element[-1] == "\n":
            element = element[:-1]

        
        with open("tasks.txt", "a") as f:
            #if its a comment we need to see if we will include it (postcondition)
            if is_comment:
                element = element.replace("\n", "\n" + indent+"#") #multi line comments if they exist
                if "a summary of the whole if-else block" in type:
                    print(f"{indent}#State: {element}", file=f)
                elif "a summary of the whole if block" in type:
                    print(f"{indent}#State: {element}", file=f)
                elif "a summary of the whole try-except block" in type:
                    print(f"{indent}#State: {element}", file=f)
                elif "a summary of the total loop" in type:
                    print(f"{indent}#State: {element}", file=f)
                    unrolled_loop =1
                elif 'the summary for the whole function' in type:
                    print(f"{indent}#Overall this is what the function does: {element}", file=f) 
                elif "return statement" in type:
                    print(f"{indent}#{element}", file=f)
                elif "print statement" in type and annotate_prints:
                    print(f"{indent}#This is printed: {element}", file=f)
                elif "summary of total for loop" in type:
                    print(f"{indent}#State: {element}", file=f)
                else:
                    pass
               
            #if it is code (non empty) we always include it in the tree
            else:
                if len(element)>0 :
                    print(f"{indent}{element}", file=f)
    #save the contents in the tast.txt file for debugging    
    with open("tasks.txt", "r") as f:
            tasks = f.read()
    return tasks


