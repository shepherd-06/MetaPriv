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
                // Session invalid/expired
                localStorage.removeItem('sessionId');
                localStorage.removeItem('onboardingStep');
            }
        } catch (err) {
            console.error("Error validating session:", err);
            localStorage.removeItem('sessionId');
            localStorage.removeItem('onboardingStep');
        }
    }

    return {
        sessionId: null,
        onboardingStep: null,
    };
}
