document.addEventListener('DOMContentLoaded', function() {
    
    // Select the Shared Elements from the page
    const elements = {
        taskContainer: document.querySelector('.TaskContainer'),
        expandBtn: document.querySelector('.TaskExpandBtn'),
        hideBtn: document.querySelector('.TaskContainer .TaskNav button'),
        task: document.querySelector('.Task'),
        noSelectedTask: document.querySelector('.NoSelectedTask'),
        selectedTaskContainer: document.querySelector('.SelectedTask')
    };

    // Initialize the Create Task / Close Task Logic
    // Defined in: create-task.js
    if (typeof initializeCreateTaskLogic === 'function') {
        initializeCreateTaskLogic(elements);
    }

    // Initialize the Chat / Assignment Logic
    // Defined in: assignment-and-chat-logic.js
    if (typeof initializeAssignmentChatLogic === 'function') {
        initializeAssignmentChatLogic(elements);
    }

    // Initialize the Table Poller (Last submissions)
    // Defined in: table-poller.js
    if (typeof startTableSubmissionPolling === 'function') {
        startTableSubmissionPolling();
    }

    // Initialize the Sidebar Toggle (Hide/Expand)
    // Defined in: sidebar-navigation.js
    if (typeof initializeSidebarNavigation === 'function') {
        initializeSidebarNavigation(elements);
    }
});
