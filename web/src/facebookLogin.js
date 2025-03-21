document.getElementById('facebookLoginForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const username = document.getElementById('facebookUsername').value;
    const password = document.getElementById('facebookPassword').value;
    // Use Electron's main process to securely store credentials via IPC
    electronAPI.storeCredentials(username, password);
    alert('Facebook credentials saved securely!');
    window.location.href = 'dashboard.html'; // Redirect to the dashboard or next part of your app
});
