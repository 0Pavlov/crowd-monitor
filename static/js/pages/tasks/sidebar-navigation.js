/**
 * Handles the sidebar expansion and collapsing logic.
 * @param {Object} elements - The collection of DOM elements.
 */
function initializeSidebarNavigation(elements) {
    const { hideBtn, task, taskContainer, expandBtn } = elements;

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
}
