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

    // END OF THE CREATE TASK BLOCK

    // TASKS BLOCK

    // Get the assignments
    const assignments_rows = document.getElementsByClassName("AssignmentRowHover");

    for (const assignment_row of assignments_rows) {
        assignment_row.addEventListener('click', () => {
            // Get the task ID from the clicked row
            const taskId = assignment_row.dataset.taskId;
            // Get the assignment ID from the clicked row
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

                    // If a polling timer from a previous chat is running, stop
                    if (window.chatPollingInterval) {
                        clearInterval(window.chatPollingInterval);
                    }

                    // Now that the HTML is on the page, find the new chat form and its elements
                    const submissionForm = document.getElementById('submission-form');
                    const messagesContainer = document.getElementById('messages-container');
                    const messageInput = submissionForm.querySelector('input[name="submitted_answer"]');
                    const currentAssignmentId = submissionForm.dataset.assignmentId;
                    // the last submission visible in the assignments overview
                    const last_sub_from_tasks = document.getElementById(`last-sub-for-assignment-${currentAssignmentId}`);
                    // Get the username of the current user who observing the form in the moment
                    const currentUserName = submissionForm.dataset.currentUserName;

                    // Function to style a single message group (bubble and meta)
                    function styleMessage(messageGroup) {
                        // Get the sender name
                        const senderName = messageGroup.dataset.senderName;

                        // Align the message bubble left or right
                        if (senderName === currentUserName) {
                            // Align to the right
                            messageGroup.classList.add('message-outgoing');
                        } else {
                            // Align to the left
                            messageGroup.classList.add('message-incoming');
                        }
                    }

                    // Helper function to create HTML for a new message and append it
                    function appendMessage(messageData) {
                        // Remove the "No messages" placeholder if it exists
                        const noMessagesPlaceholder = document.getElementById('no-messages-placeholder');
                        if (noMessagesPlaceholder) {
                            noMessagesPlaceholder.remove();
                        }

                        // Determine alignment class based on sender
                        const alignmentClass = (messageData.submitted_by_name === currentUserName) ? 'message-outgoing' : 'message-incoming';

                        // Create the new message HTML with the right styling applied
                        const newMessageHTML = `
                            <div class="message-group ${alignmentClass}" data-sender-name="${messageData.submitted_by_name}" data-timestamp="${messageData.timestamp}">
                                <div class="message-bubble">
                                    <p>${messageData.submitted_answer}</p>
                                </div>
                                <div class="message-meta">
                                    <span class="sender-name">${messageData.submitted_by_name}</span> at
                                    <span class="dynamic-timestamp" data-timestamp="${messageData.timestamp}">
                                        ${messageData.formatted_timestamp}
                                    </span>
                                </div>
                            </div>
                        `;
                        // Append the chat with the new message on the bottom
                        messagesContainer.insertAdjacentHTML('beforeend', newMessageHTML);
                        // Scroll to the bottom to show the new message
                        task.scrollTop = task.scrollHeight;

                        // Also update the last sub in the main tasks table
                        if (last_sub_from_tasks) {
                            last_sub_from_tasks.textContent = `${messageData.submitted_by_name}: ${messageData.submitted_answer}`;
                        }
                    }

                    // Style all messages that were loaded initially with the template
                    messagesContainer.querySelectorAll('.message-group').forEach(styleMessage);
                    // Scroll to the bottom on initial load
                    //messagesContainer.scrollTop = messagesContainer.scrollHeight;

                    // Add an event listener specifically for this newly created form
                    submissionForm.addEventListener('submit', function(event) {
                        // Prevent the default form submission which causes a page reload
                        event.preventDefault();

                        // Get the message text and the assignment ID from the form's data attribute
                        const messageText = messageInput.value.trim();

                        // Do not proceed if the message is empty
                        if (messageText === '') {
                            return; 
                        }

                        // Use fetch to send the data to the API endpoint
                        fetch('/create-submission', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json' // Essential for request.get_json()
                            },
                            // Convert the JavaScript data into a JSON string to send in the request body
                            body: JSON.stringify({
                                submitted_answer: messageText,
                                assignment_id: currentAssignmentId
                            })
                        })
                        .then(response => response.json()) // Parse the JSON response from the Flask server
                        .then(data => {
                            // Check the 'status' field from the Flask jsonify response
                            if (data.status === 'success') {
                                // Clear the input field and put the cursor back in it
                                messageInput.value = '';
                                messageInput.focus();

                            } else {
                                // If Flask returned an error, show it to the user
                                console.error('Submission failed:', data.message);
                                alert('Error: ' + data.message);
                            }
                        })
                        .catch(error => {
                            // Handle network-level errors (e.g., server is down)
                            console.error('Network error:', error);
                            alert('A network error occurred. Please try again.');
                        });
                    });
                    
                    // --- POLLING FUNCTION ---
                    function pollForNewMessages() {
                        const lastMessage = messagesContainer.querySelector('.message-group:last-of-type');
                        // Get the timestamp of the last message
                        // If there are no messages, use a default past date
                        let lastTimestamp = lastMessage ? lastMessage.dataset.timestamp : '1970-01-01 00:00:00';

                        // Chat info for closing the chat if assignment is closed
                        const chatInputContainer = document.querySelector('.chat-input-container');
                        const submissionForm = document.getElementById('submission-form');
                        const chatInput = submissionForm.querySelector('input[name="submitted_answer"]');
                        const chatButton = submissionForm.querySelector('button');

                        fetch(`/get-updates?assignment_id=${currentAssignmentId}&last_timestamp=${lastTimestamp}`)
                        .then(response => response.json())
                        .then(data => {
                            // CHAT CLOSING BLOCK START
                            if (data.assignment_status === 'closed') {
                                // Check if it's already disabled to avoid redundant DOM manipulation
                                if (!chatInput.disabled) {
                                    chatInput.placeholder = 'Assignment is closed';
                                    chatInput.disabled = true;
                                    chatButton.disabled = true;

                                    // Add a class for styling the disabled state
                                    submissionForm.classList.add('deactivated');
                                }
                            } else if (data.assignment_status === 'not_closed') {
                                // Re-enable the form if the status is not 'closed'
                                if (chatInput.disabled) {
                                    chatInput.placeholder = 'Type your message...';
                                    chatInput.disabled = false;
                                    chatButton.disabled = false;
                                    submissionForm.classList.remove('deactivated');
                                }
                            }
                            // CHAT CLOSING BLOCK END
                            if (data.status === 'success' && data.new_submissions.length > 0) {
                                // If the server sent new messages, add each one
                                data.new_submissions.forEach(submission => {
                                    appendMessage(submission);
                                });
                            }
                        })
                        .catch(error => {
                            console.error('Polling error:', error);
                        });
                    }

                    // Start polling for new messages every 1 second
                    window.chatPollingInterval = setInterval(pollForNewMessages, 1000);

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

    // --- POLLING for last submissions in the table ---
    function pollLastSubmissions() {
        // Find all assignment rows to get their IDs
        const assignmentRows = document.querySelectorAll('.AssignmentRowHover');

        assignmentRows.forEach(row => {
            const assignmentId = row.dataset.assignmentId;
            if (!assignmentId) return; // Skip if no id is found

            // Call /get-updates for each assignment
            // Pass a very old timestamp to ensure we get the latest submission,
            // as the endpoint is designed to find submissions after a certain time
            const pastTimestamp = '1970-01-01 00:00:00';

            fetch(`/get-updates?assignment_id=${assignmentId}&last_timestamp=${pastTimestamp}`)
                .then(response => {
                    if (!response.ok) {
                        // If the server returns an error (like 404 or 500), log it but don't stop the process
                        console.error(`Error fetching update for assignment ${assignmentId}: ${response.status}`);
                        return null; // Prevent the next .then() from running on a failed request
                    }
                    return response.json(); // If the response is OK, parse it as JSON
                })
                .then(data => {
                    // Make sure the data is valid and that there are submissions
                    if (data && data.status === 'success' && data.new_submissions.length > 0) {
                        // The endpoint returns an array of submissions. The last one in the array is the most recent
                        const lastSubmission = data.new_submissions[data.new_submissions.length - 1];
                        
                        // Find the corresponding cell in the table to update
                        const lastSubCell = document.getElementById(`last-sub-for-assignment-${assignmentId}`);
                        if (lastSubCell) {
                            // Update the cell's text content
                            lastSubCell.textContent = `${lastSubmission.submitted_by_name}: ${lastSubmission.submitted_answer}`;
                        }
                    }
                })
                .catch(error => {
                    // This will catch network errors or errors from the .json() parsing if the response wasn't OK
                    console.error(`Error processing update for assignment ${assignmentId}:`, error);
                });
        });
    }

    // Start polling every 10 seconds
    setInterval(pollLastSubmissions, 10000);

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
