import React, { Component } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

class Onboarding extends Component {
    constructor(props) {
        super(props);
        this.state = {
            loginUsername: '',
            loginPassword: '',
            signupUsername: '',
            signupPassword: '',
            error: '',
        };
    }

    validateUsername(username) {
        return username.length >= 6 && username.length <= 20;
    }

    validatePassword(password) {
        return /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[\W_]).{8,30}$/.test(password);
    }

    handleLogin = async () => {
        const { loginUsername, loginPassword } = this.state;
        if (!this.validateUsername(loginUsername) || !this.validatePassword(loginPassword)) {
            this.setState({ error: 'Invalid login credentials.' });
            return;
        }

        const result = await window.electronAPI.loginAccount({
            username: loginUsername,
            password: loginPassword,
        });

        if (result.success) {
            localStorage.setItem('sessionId', result.sessionId);
            localStorage.setItem('onboardingStep', result.onboardingStep);
            window.location.reload(); // or navigate to appropriate view
        } else {
            this.setState({ error: result.message });
        }
    };

    handleSignup = async () => {
        const { signupUsername, signupPassword } = this.state;
        if (!this.validateUsername(signupUsername) || !this.validatePassword(signupPassword)) {
            this.setState({ error: 'Invalid signup info. Password must be 8-30 chars, include letters, numbers, and symbols.' });
            return;
        }

        const result = await window.electronAPI.createAccount({
            username: signupUsername,
            password: signupPassword
        });

        if (result.success) {
            alert(result.message);
            // clear sign up fields and focus on login
            this.setState({
                signupUsername: '',
                signupPassword: '',
            })
        } else {
            this.setState({ error: result.message });
        }

    };

    handleChange = (field, value) => {
        this.setState({ [field]: value, error: '' });
    };

    render() {
        const { error } = this.state;

        return (
            <div className="container mt-5">
                <div className="row">
                    <div className="col-md-6 border-end">
                        <h3 className="mb-3">Login</h3>
                        <input
                            type="text"
                            className="form-control mb-2"
                            placeholder="Username"
                            value={this.state.loginUsername}
                            onChange={(e) => this.handleChange('loginUsername', e.target.value)}
                        />
                        <input
                            type="password"
                            className="form-control mb-3"
                            placeholder="Password"
                            value={this.state.loginPassword}
                            onChange={(e) => this.handleChange('loginPassword', e.target.value)}
                        />
                        <button className="btn btn-primary w-100" onClick={this.handleLogin}>
                            Login
                        </button>
                    </div>

                    <div className="col-md-6">
                        <h3 className="mb-3">Sign Up</h3>
                        <input
                            type="text"
                            className="form-control mb-2"
                            placeholder="New Username"
                            value={this.state.signupUsername}
                            onChange={(e) => this.handleChange('signupUsername', e.target.value)}
                        />
                        <input
                            type="password"
                            className="form-control mb-3"
                            placeholder="New Password"
                            value={this.state.signupPassword}
                            onChange={(e) => this.handleChange('signupPassword', e.target.value)}
                        />
                        <button className="btn btn-success w-100" onClick={this.handleSignup}>
                            Create Account
                        </button>
                    </div>
                </div>

                {error && <div className="alert alert-danger mt-4 text-center">{error}</div>}
            </div>
        );
    }
}

export default Onboarding;
