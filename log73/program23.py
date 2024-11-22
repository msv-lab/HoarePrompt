def task_status(tasks, running):
    completed, pending = 0, 0
    while running:
        for task in tasks:
            if task == "complete":
                completed += 1
            elif task == "pending":
                pending += 1
            else:
                print("Unknown task")
        running = check_status()
    return completed, pending
