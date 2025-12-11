/**
 * Handles Assignment selection, Chat UI, and Chat Polling.
 * @param {Object} elements - The collection of DOM elements.
 */
function initializeAssignmentChatLogic(elements) {
    const { 
        taskContainer, expandBtn, task, noSelectedTask, 
        selectedTaskContainer 
    } = elements;

    // We need to access this to hide it when opening a chat
    const createTaskContainer = document.querySelector('#create-task-container');

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
}
