import React, { Component } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

class FacebookAuth extends Component {
    constructor(props) {
        super(props);
        this.state = {
            fbEmail: '',
            fbPassword: '',
            error: '',
            success: ''
        };
    }

    handleChange = (field, value) => {
        this.setState({ [field]: value, error: '', success: '' });
    };

    handleSubmit = () => {
        const { fbEmail, fbPassword } = this.state;

        if (!fbEmail || !fbPassword) {
            this.setState({ error: 'Both fields are required.' });
            return;
        }

        // We'll complete the actual handling later
        this.setState({ success: '✅ Facebook credentials submitted (not yet processed).' });
    };

    render() {
        const { fbEmail, fbPassword, error, success } = this.state;

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
                    />
                    <input
                        type="password"
                        className="form-control mb-3"
                        placeholder="Facebook Password"
                        value={fbPassword}
                        onChange={(e) => this.handleChange('fbPassword', e.target.value)}
                    />
                    <button className="btn btn-primary w-100" onClick={this.handleSubmit}>
                        Submit
                    </button>

                    {error && <div className="alert alert-danger mt-3">{error}</div>}
                    {success && <div className="alert alert-success mt-3">{success}</div>}
                </div>
            </div>
        );
    }
}

export default FacebookAuth;
