#State of the program right berfore the function call: tasks is a list of strings where each string is either 'complete' or 'pending', and running is a boolean indicating whether the tasks should continue to be processed.
def func_1(tasks, running):
    completed, pending = 0, 0
    while running:
        for task in tasks:
            if task == 'complete':
                completed += 1
            elif task == 'pending':
                pending += 1
            else:
                print('Unknown task')
        
        running = check_status()
        
    #State of the program after the loop has been executed: `tasks` is a list of strings containing tasks that are either 'complete' or 'pending'; `running` is false (indicating that no further processing will occur); `completed` is the total count of 'complete' tasks in `tasks`; `pending` is the total count of 'pending' tasks in `tasks`.
    return completed, pending
    #The program returns the total count of 'complete' tasks as 'completed' and the total count of 'pending' tasks as 'pending'
#Overall this is what the function does:
The function accepts a list of strings `tasks` and a boolean `running`. It counts the number of tasks that are 'complete' and 'pending' while the `running` flag is true. The function returns the count of 'complete' tasks and the count of 'pending' tasks. If any task has an unknown status, it prints 'Unknown task'. The `check_status()` function determines whether to continue processing tasks, but since its implementation is unknown, it may affect the loop's execution in ways that are not defined here. The function does not handle cases where `tasks` could be empty or where `running` is false at the start.

