document.getElementById('masterPasswordForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const masterPassword = document.getElementById('masterPassword').value;
    // Assume `hashPassword` and `saveMasterPassword` are functions you've defined to hash the password and save it to the database.
    const hashedPassword = await hashPassword(masterPassword);
    saveMasterPassword(hashedPassword);
    alert('Master password set successfully!');
    window.location.href = 'facebookLogin.html'; // Redirect to Facebook login page
});
