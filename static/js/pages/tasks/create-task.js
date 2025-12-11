/**
 * Handles the Create Task UI and Close Task API calls.
 * @param {Object} elements - The collection of DOM elements.
 */
function initializeCreateTaskLogic(elements) {
    const { 
        taskContainer, expandBtn, task, noSelectedTask, 
        selectedTaskContainer 
    } = elements;

    // Elements for the AJAX part
    // Append the HTML if the user has permission
    const showCreateTaskBtn = document.querySelector('#show-create-task-btn');
    const createTaskContainer = document.querySelector('#create-task-container');
    // Close task buttons
    const closeTaskBtnList = document.querySelectorAll('#close-task-button');

    // For each button
    closeTaskBtnList.forEach((button) => {
        // Add event listener for a click
        button.addEventListener('click', () => {
            // Extract task Id from dataset
            const taskId = button.dataset.taskId;
            // Data we will send to the server
            const data = {task_id: taskId};
            // Fetch the route
            fetch('/close-task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
            .then(response => response.json())
            .then(data => {
                    //console.log(data);
                })
            .catch((error) => {
                    console.error('Error', error);
                });
        });
    })
    
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
}
