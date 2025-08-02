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

    // Get the assignments
    const assignments_rows = document.getElementsByClassName("AssignmentRow");

    for (const assignment_row of assignments_rows) {
        assignment_row.addEventListener('click', () => {
            // Get the task ID from the clicked row
            const taskId = assignment_row.dataset.taskId;
            const assignmentId = assignment_row.dataset.assignmentId;

            // Perform the fetch request to the /assignment route
            // Pass the taskId and assignmentId as a query parameter in the URL
            fetch(`/assignment?task_id=${taskId}&assignment_id=${assignmentId}`)
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

                    // --- START OF THE CHAT MESSAGING BLOCK ---

                    // Now that the HTML is on the page, find the new chat form and its elements.
                    const submissionForm = document.getElementById('submission-form');
                    const messagesContainer = document.getElementById('messages-container');
                    const messageInput = submissionForm.querySelector('input[name="submitted_answer"]');

                    // Add an event listener specifically for this newly created form.
                    submissionForm.addEventListener('submit', function(event) {
                        // Prevent the default form submission which causes a page reload.
                        event.preventDefault();

                        // Get the message text and the assignment ID from the form's data attribute.
                        const messageText = messageInput.value.trim();
                        const assignmentId = submissionForm.dataset.assignmentId;

                        // Do not proceed if the message is empty.
                        if (messageText === '') {
                            return; 
                        }

                        // Use fetch to send the data to the API endpoint.
                        fetch('/create-submission', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json' // Essential for request.get_json().
                            },
                            // Convert the JavaScript data into a JSON string to send in the request body.
                            body: JSON.stringify({
                                submitted_answer: messageText,
                                assignment_id: assignmentId
                            })
                        })
                        .then(response => response.json()) // Parse the JSON response from the Flask server.
                        .then(data => {
                            // Check the 'status' field from the Flask jsonify response.
                            if (data.status === 'success') {
                                // If there's a "NO MESSAGES" placeholder, remove it.
                                const noMessagesPlaceholder = document.getElementById('no-messages-placeholder');
                                if (noMessagesPlaceholder) {
                                    noMessagesPlaceholder.remove();
                                }

                                // Create the HTML for the new message using data from the server response.
                                const newMessageHTML = `
                                    <div class="message-group">
                                        <p><strong>From:</strong> ${data.new_submission.submitted_by_name}</p>
                                        <p><strong>Message:</strong> ${data.new_submission.submitted_answer}</p>
                                        <p><strong>At:</strong> ${data.new_submission.timestamp}</p>
                                    </div>
                                `;

                                // Add the new message HTML to the end of the messages container.
                                messagesContainer.insertAdjacentHTML('beforeend', newMessageHTML);
                                
                                // Clear the input field and put the cursor back in it.
                                messageInput.value = '';
                                messageInput.focus();

                            } else {
                                // If Flask returned an error, show it to the user.
                                console.error('Submission failed:', data.message);
                                alert('Error: ' + data.message);
                            }
                        })
                        .catch(error => {
                            // Handle network-level errors (e.g., server is down).
                            console.error('Network error:', error);
                            alert('A network error occurred. Please try again.');
                        });
                    });
                    
                    // --- END OF CHAT MESSAGING BLOCK ---

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
