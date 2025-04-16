export async function cacheManager() {
    const sessionId = localStorage.getItem('sessionId');
    const onboardingStep = localStorage.getItem('onboardingStep');

    if (sessionId) {
        try {
            const result = await window.electronAPI.validateSession(sessionId);
            if (result && result.valid) {
                return {
                    sessionId,
                    onboardingStep,
                };
            } else {
                localStorage.removeItem('sessionId');
                localStorage.removeItem('onboardingStep');
            }
        } catch (err) {
            console.error("Error validating session:", err);
            localStorage.removeItem('sessionId');
            localStorage.removeItem('onboardingStep');
        }
    }
    window.location.href = "/";
    return {
        sessionId: null,
        onboardingStep: null,
    };
}
