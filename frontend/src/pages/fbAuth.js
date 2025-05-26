import React, { Component } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Navigate } from 'react-router-dom';

class FacebookAuth extends Component {
    constructor(props) {
        super(props);
        this.state = {
            fbEmail: '',
            fbPassword: '',
            error: '',
            success: '',
            loading: false,
            redirectToDashboard: false
        };
    }

    handleChange = (field, value) => {
        this.setState({ [field]: value, error: '', success: '', loading: false });
    };

    handleSubmit = async () => {
        const { fbEmail, fbPassword } = this.state;
        const sessionId = localStorage.getItem('sessionId');

        if (!fbEmail || !fbPassword) {
            this.setState({ error: 'Both fields are required.' });
            return;
        }

        this.setState({ loading: true, error: '', success: '' });

        const result = await window.electronAPI.submitFacebookAuth({
            sessionId,
            fbEmail,
            fbPassword
        });

        if (result.success) {
            this.setState({ success: result.message, loading: false });
            localStorage.setItem('onboardingStep', '5');
            setTimeout(() => {
                this.setState({ redirectToDashboard: true });
            }, 2000);
        } else {
            this.setState({ error: result.message, loading: false });
        }
    };

    render() {
        const { fbEmail, fbPassword, error, success, loading, redirectToDashboard } = this.state;

        if (redirectToDashboard) {
            return <Navigate to="/dashboard" />;
        }

        return (
            <div className="container mt-5">
                <h2>📘 Facebook Authentication</h2>
                <p className="text-muted mt-3">
                    We do <strong>not store</strong> your Facebook password in our database.
                    <br />
                    Your email will be stored <strong>encrypted</strong> using your <strong>Master Password</strong>.
                    <br />
                    Your full Facebook login credentials will be securely stored in your operating system's keyring.
                </p>

                <div className="col-md-6 mt-4">
                    <input
                        type="text"
                        className="form-control mb-3"
                        placeholder="Facebook Email or Username"
                        value={fbEmail}
                        onChange={(e) => this.handleChange('fbEmail', e.target.value)}
                        disabled={loading}
                    />
                    <input
                        type="password"
                        className="form-control mb-3"
                        placeholder="Facebook Password"
                        value={fbPassword}
                        onChange={(e) => this.handleChange('fbPassword', e.target.value)}
                        disabled={loading}
                    />
                    <button className="btn btn-primary w-100" onClick={this.handleSubmit} disabled={loading}>
                        {loading ? (
                            <>
                                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                Saving credentials...
                            </>
                        ) : (
                            'Submit'
                        )}
                    </button>

                    {error && <div className="alert alert-danger mt-3">{error}</div>}
                    {success && <div className="alert alert-success mt-3">{success}</div>}
                </div>
            </div>
        );
    }
}

export default FacebookAuth;
