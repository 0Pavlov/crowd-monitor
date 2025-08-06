document.addEventListener('DOMContentLoaded', function() {
    // Select page elements
    const taskContainer = document.querySelector('.TaskContainer');
    const expandBtn = document.querySelector('.TaskExpandBtn');
    const hideBtn = document.querySelector('.TaskContainer .TaskNav button');
    const task = document.querySelector('.Task');
    const noSelectedTask = document.querySelector('.NoSelectedTask');
    const selectedTaskContainer = document.querySelector('.SelectedTask');
    const showCreateTaskBtn = document.querySelector('#show-create-task-btn');
    const createTaskContainer = document.querySelector('#create-task-container');

    // --- CREATE TASK LOGIC ---
    if (showCreateTaskBtn) {
        showCreateTaskBtn.addEventListener('click', () => {
            fetch('/get-create-task')
                .then(response => {
                    if (response.ok) return response.text();
                    throw new Error(`Server responded with ${response.status}: You might not have permission.`);
                })
                .then(html => {
                    createTaskContainer.innerHTML = html;
                    taskContainer.classList.remove('collapsed');
                    task.classList.remove('hidden');
                    expandBtn.classList.add('hidden');
                    selectedTaskContainer.classList.add('hidden');
                    noSelectedTask.classList.add('hidden');
                    createTaskContainer.classList.remove('hidden');
                })
                .catch(error => {
                    console.error('Error fetching create task form:', error);
                    alert(error.message);
                });
        });
    }

    // --- ASSIGNMENT & CHAT LOGIC ---
    const assignments_rows = document.getElementsByClassName("AssignmentRowHover");

    for (const assignment_row of assignments_rows) {
        assignment_row.addEventListener('click', () => {
            const taskId = assignment_row.dataset.taskId;
            const assignmentId = assignment_row.dataset.assignmentId;

            fetch(`/assignment?task_id=${taskId}&assignment_id=${assignmentId}`)
                .then(response => {
                    if (response.ok) return response.text();
                    throw new Error(`Failed to fetch assignment. ${response.status}`);
                })
                .then(html => {
                    // Place the new HTML into the container
                    selectedTaskContainer.innerHTML = html;

                    // --- START OF THE CENTRALIZED CHAT LOGIC ---

                    // Stop any previous polling timer
                    if (window.chatPollingInterval) {
                        clearInterval(window.chatPollingInterval);
                    }

                    // --- DOM ELEMENTS ---
                    const submissionForm = document.getElementById('submission-form');
                    const messagesContainer = document.getElementById('messages-container');
                    const messageInput = submissionForm.querySelector('input[name="submitted_answer"]');
                    const last_sub_from_tasks = document.getElementById(`last-sub-for-assignment-${assignmentId}`);

                    // --- GET THE CURRENT USER'S NAME ---
                    // Read the name from the data attribute we added in assignment.html
                    const currentUserName = submissionForm.dataset.currentUserName;

                    // --- HELPER FUNCTIONS ---

                    // Function to format timestamps into a user-friendly format
                    function formatTimestamp(timestampString) {
                        if (!timestampString) return '';
                        try {
                            const date = new Date(timestampString);
                            return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
                        } catch (e) {
                            console.error("Could not format timestamp:", timestampString, e);
                            return timestampString; // Return original if formatting fails
                        }
                    }

                    // Function to style a single message group (bubble and meta)
                    function styleMessage(messageGroup) {
                        const senderName = messageGroup.dataset.senderName;
                        
                        // Align the message bubble left or right
                        if (senderName === currentUserName) {
                            messageGroup.classList.add('message-outgoing');
                        } else {
                            messageGroup.classList.add('message-incoming');
                        }

                        // Format the timestamp within the message
                        const timestampEl = messageGroup.querySelector('.dynamic-timestamp');
                        if (timestampEl) {
                            timestampEl.textContent = formatTimestamp(timestampEl.dataset.timestamp);
                        }
                    }

                    // The NEW appendMessage function that builds the correct M3 bubble HTML
                    function appendMessage(messageData) {
                        // Remove "No messages" placeholder if it exists
                        const noMessagesPlaceholder = document.getElementById('no-messages-placeholder');
                        if (noMessagesPlaceholder) noMessagesPlaceholder.remove();

                        // Determine alignment class based on sender
                        const alignmentClass = (messageData.submitted_by_name === currentUserName) ? 'message-outgoing' : 'message-incoming';
                        
                        // Create the new message HTML with Material 3 structure
                        const newMessageHTML = `
                            <div class="message-group ${alignmentClass}" data-sender-name="${messageData.submitted_by_name}" data-timestamp="${messageData.timestamp}">
                                <div class="message-bubble">
                                    <p>${messageData.submitted_answer}</p>
                                </div>
                                <div class="message-meta">
                                    <span class="sender-name">${messageData.submitted_by_name}</span> at 
                                    <span class="dynamic-timestamp" data-timestamp="${messageData.timestamp}">
                                        ${formatTimestamp(messageData.timestamp)}
                                    </span>
                                </div>
                            </div>
                        `;
                        
                        messagesContainer.insertAdjacentHTML('beforeend', newMessageHTML);
                        // Scroll to the bottom to show the new message
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;

                        // Update the last submission text in the main tasks table
                        if (last_sub_from_tasks) {
                            last_sub_from_tasks.textContent = `${messageData.submitted_by_name}: ${messageData.submitted_answer}`;
                        }
                    }

                    // --- INITIAL SETUP ---
                    // Style all messages that were loaded initially with the template
                    messagesContainer.querySelectorAll('.message-group').forEach(styleMessage);
                    // Scroll to the bottom on initial load
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;

                    // --- EVENT LISTENERS & POLLING ---
                    submissionForm.addEventListener('submit', function(event) {
                        event.preventDefault();
                        const messageText = messageInput.value.trim();
                        if (messageText === '') return;

                        fetch('/create-submission', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                submitted_answer: messageText,
                                assignment_id: assignmentId
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'success') {
                                messageInput.value = '';
                                messageInput.focus();
                                // The new message will appear via the polling mechanism
                            } else {
                                console.error('Submission failed:', data.message);
                                alert('Error: ' + data.message);
                            }
                        })
                        .catch(error => {
                            console.error('Network error:', error);
                            alert('A network error occurred. Please try again.');
                        });
                    });
                    
                    function pollForNewMessages() {
                        const lastMessage = messagesContainer.querySelector('.message-group:last-of-type');
                        let lastTimestamp = lastMessage ? lastMessage.dataset.timestamp : '1970-01-01 00:00:00';

                        fetch(`/get-updates?assignment_id=${assignmentId}&last_timestamp=${lastTimestamp}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'success' && data.new_submissions.length > 0) {
                                data.new_submissions.forEach(appendMessage);
                            }
                        })
                        .catch(error => console.error('Polling error:', error));
                    }

                    // Start polling for this specific chat
                    window.chatPollingInterval = setInterval(pollForNewMessages, 2000);

                    // --- END OF CENTRALIZED CHAT LOGIC ---

                    // Show the side panel
                    taskContainer.classList.remove('collapsed');
                    noSelectedTask.classList.add('hidden');
                    createTaskContainer.classList.add('hidden');
                    selectedTaskContainer.classList.remove('hidden');
                    task.classList.remove('hidden');
                    expandBtn.classList.add('hidden');
                })
                .catch(error => {
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
            if (!assignmentId) return;

            const pastTimestamp = '1970-01-01 00:00:00';

            fetch(`/get-updates?assignment_id=${assignmentId}&last_timestamp=${pastTimestamp}`)
                .then(response => {
                    if (!response.ok) {
                        console.error(`Error fetching update for assignment ${assignmentId}: ${response.status}`);
                        return null;
                    }
                    return response.json();
                })
                .then(data => {
                    if (data && data.status === 'success' && data.new_submissions.length > 0) {
                        const lastSubmission = data.new_submissions[data.new_submissions.length - 1];
                        
                        const lastSubCell = document.getElementById(`last-sub-for-assignment-${assignmentId}`);
                        if (lastSubCell) {
                            lastSubCell.textContent = `${lastSubmission.submitted_by_name}: ${lastSubmission.submitted_answer}`;
                        }
                    }
                })
                .catch(error => {
                    console.error(`Error processing update for assignment ${assignmentId}:`, error);
                });
        });
    }

    // Start polling every 10 seconds
    setInterval(pollLastSubmissions, 10000);

    // END OF THE TASKS BLOCK

    // HIDE
    hideBtn.addEventListener('click', () => {
        task.classList.add('hidden');
        taskContainer.classList.add('collapsed');
        expandBtn.classList.remove('hidden');
    });

    // EXPAND
    expandBtn.addEventListener('click', () => {
        taskContainer.classList.remove('collapsed');
        taskContainer.addEventListener('transitionend', () => {
            expandBtn.classList.add('hidden');
            task.classList.remove('hidden');
        }, { once: true });
    });
});
