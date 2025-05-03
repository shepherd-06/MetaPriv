export async function logout() {
    const sessionId = localStorage.getItem('sessionId');

    // Clean up localStorage
    localStorage.removeItem('sessionId');
    localStorage.removeItem('onboardingStep');

    // Call the Electron API to invalidate the session
    if (sessionId) {
        window.electronAPI.invalidateSession(sessionId)
            .then(() => {
                console.log('Session invalidated successfully.');
            })
            .catch((err) => {
                console.error('Failed to invalidate session:', err);
            });
    }

    // Optionally: Reload or redirect user to the login/onboarding screen
    window.location.reload();
}
