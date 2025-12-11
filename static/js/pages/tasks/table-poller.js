/**
 * Polls the server every 10 seconds to update the table with the last submission.
 */
function startTableSubmissionPolling() {
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
}
