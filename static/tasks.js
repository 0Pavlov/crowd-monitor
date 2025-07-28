document.addEventListener('DOMContentLoaded', function() {
    // CREATE TASK BLOCK

    // Select the elements from the page
    const taskContainer = document.querySelector('.TaskContainer');
    const expandBtn = document.querySelector('.TaskExpandBtn');
    const hideBtn = document.querySelector('.TaskContainer .TaskNav button');
    const task = document.querySelector('.Task');
    const noSelectedTask = document.querySelector('.NoSelectedTask');
    const selectedTaskContainer = document.querySelector('.SelectedTask');

    // Elements for the AJAX part
    // Append the HTML if the user has permission
    const showCreateTaskBtn = document.querySelector('#show-create-task-btn');
    const createTaskContainer = document.querySelector('#create-task-container');
    
    // Check if the button exists (it won't for workers)
    if (showCreateTaskBtn) {
        showCreateTaskBtn.addEventListener('click', () => {
            // Use fetch() to call the new server route
            fetch('/get-create-task')
                .then(response => {
                    // Check if the server responded with 'OK' (status 200-299)
                    if (response.ok) {
                        // If it's okay, it means the user is an admin and the server is sending HTML
                        return response.text(); // Get the response body as raw text (HTML 'create-task.html')
                    } else {
                        // If the server responded with an error (like 403 Forbidden)
                        // This will trigger the .catch() block below
                        throw new Error(`Server responded with ${response.status}: You might not have permission.`);
                    }
                })
                .then(html => {
                    // SUCCESS!
                    // 'html' now contains the string of the rendered create-task.html
                    
                    // Inject the form HTML into our placeholder container
                    createTaskContainer.innerHTML = html;

                    // Make the main panel visible (triggering the transition)
                    taskContainer.classList.remove('collapsed');

                    // Scenario when the createTaskContainer is visible but collapsed
                    if (!expandBtn.classList.contains('hidden') && !createTaskContainer.classList.contains('hidden')) {
                        // Hide the container and then unhide it after the transition
                        createTaskContainer.classList.add('hidden');

                        // Listen for the transition to finish
                        taskContainer.addEventListener('transitionend', () => {
                            task.classList.remove('hidden');
                            // Hide the expand button
                            expandBtn.classList.add('hidden');
                            // Hide the 'selectedTaskContainer'
                            selectedTaskContainer.classList.add('hidden');
                            // Hide the 'NoSelectedTask' div
                            noSelectedTask.classList.add('hidden');
                            // Unhide the create task container
                            createTaskContainer.classList.remove('hidden');
                        }, {once: true});
                    }

                    // Scenario when the container isn't visible and collapsed
                    if (!expandBtn.classList.contains('hidden') && createTaskContainer.classList.contains('hidden')) {
                        // Listen for the transition to finish
                        taskContainer.addEventListener('transitionend', () => {
                            task.classList.remove('hidden');
                            // Hide the expand button
                            expandBtn.classList.add('hidden');
                            // Hide the 'selectedTaskContainer'
                            selectedTaskContainer.classList.add('hidden');
                            // Hide the 'NoSelectedTask' div
                            noSelectedTask.classList.add('hidden');
                            // Unhide the create task container
                            createTaskContainer.classList.remove('hidden');
                    
                        }, {once: true});
                    }
                    else {
                        task.classList.remove('hidden');
                        // Hide the expand button
                        expandBtn.classList.add('hidden');

                        // Hide the 'selectedTaskContainer'
                        selectedTaskContainer.classList.add('hidden');
                        // Hide the 'NoSelectedTask' div
                        noSelectedTask.classList.add('hidden');

                        // Unhide the create task container
                        createTaskContainer.classList.remove('hidden');
                    }
                })
                .catch(error => {
                    // This block will run if the fetch fails (network error)
                    // or if the server returned an error status (like 403)
                    console.error('Error fetching create task form:', error);
                    alert(error.message);
                });
        });
    }

    // END OF THE CREATE TASK BLOCK

    // TASKS BLOCK

    // Get the tasks
    const task_rows = document.getElementsByClassName("TaskRow");

    for (const task_row of task_rows) {
        task_row.addEventListener('click', () => {
            // Get the task ID from the clicked row
            const taskId = task_row.id;

            // Perform the fetch request to the /assignment route
            // Pass the task ID as a query parameter in the URL
            fetch(`/assignment?id=${taskId}`)
                .then(response => {
                    // Check if the request was successful
                    if (response.ok) {
                        // Get the HTML response
                        return response.text();
                    } else {
                        // Handle errors
                        throw new Error(`Failed to fetch assignment. ${response.status}`);
                    }
                })
                .then(html => {
                    // Update the UI

                    // Place the HTML into .SelectedTask container
                    selectedTaskContainer.innerHTML = html;

                    // Expand the side panel
                    taskContainer.classList.remove('collapsed');

                    // Case when the task container is hidden
                    if (!expandBtn.classList.contains('hidden') && task.classList.contains('hidden')) {
                        // Listen for the transition to finish
                        taskContainer.addEventListener('transitionend', () => {
                            // Hide the other views inside the panel
                            noSelectedTask.classList.add('hidden');
                            createTaskContainer.classList.add('hidden');
                            // Show the container for the fetched assignment
                            selectedTaskContainer.classList.remove('hidden');
                            // Unhide the main task container
                            task.classList.remove('hidden');
                            // Hide the expand button
                            expandBtn.classList.add('hidden');
                        }, {once: true});
                    } else {
                        // Don't wait for transition to end
                        // Hide the other views inside the panel
                        noSelectedTask.classList.add('hidden');
                        createTaskContainer.classList.add('hidden');
                        // Show the container for the fetched assignment
                        selectedTaskContainer.classList.remove('hidden');
                        task.classList.remove('hidden');
                        expandBtn.classList.add('hidden');
                    }
                })
                .catch(error => {
                    // Log and display any errors that occured during the fetch
                    console.error('Error fetching assignment:', error);
                    alert(error.message);
                });
        });
    }

    // END OF THE TASKS BLOCK

    // HIDE
    // When the 'hide' button is clicked
    hideBtn.addEventListener('click', () => {
        // Add the 'hidden' class to the task description
        task.classList.add('hidden');
        // Add the 'collapsed' class to shrink the container
        taskContainer.classList.add('collapsed');
        // Remove the 'hidden' class from the 'expand' button
        expandBtn.classList.remove('hidden');
    });

    // EXPAND
    // When the 'expand' button is clicked
    expandBtn.addEventListener('click', () => {
        // Remove the 'collapsed' class from the container
        taskContainer.classList.remove('collapsed');
        // Listen for the transition to finish
        taskContainer.addEventListener('transitionend', () => {
            // Add the 'hidden' class to the 'expand' button
            expandBtn.classList.add('hidden');
            // After the container is fully expanded
            // Remove the 'hidden' class from the task description
            task.classList.remove('hidden');
        }, {once: true});
    });
});
