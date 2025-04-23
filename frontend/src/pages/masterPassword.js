import React, { Component } from 'react';
import { Navigate } from 'react-router-dom';
import { cacheManager } from "../utility/cachemanager";

class MasterPassword extends Component {
    constructor(props) {
        super(props);
        this.state = {
            password: '',
            confirmPassword: '',
            unlockPassword: '',
            error: '',
            success: '',
            fbAuth: false,
            sessionId: null,
            onboardingStep: null,
        };
    }

    async componentDidMount() {
        const { sessionId, onboardingStep } = await cacheManager();
        this.setState({ sessionId, onboardingStep });
        console.log("Current ", sessionId, " > ", onboardingStep);
    }

    handleChange = (field, value) => {
        this.setState({ [field]: value, error: '', success: '' });
    };

    handleSubmit = async () => {
        /**
         * this beautiful function is for saving master Password
         */
        const { password, confirmPassword } = this.state;
        const sessionId = localStorage.getItem('sessionId');

        if (!sessionId) {
            this.setState({ error: 'Session expired. Please log in again.' });
            return;
        }

        if (password.length !== 24 || confirmPassword.length !== 24) {
            this.setState({ error: 'Password must be exactly 24 characters long.' });
            return;
        }

        if (password !== confirmPassword) {
            this.setState({ error: 'Passwords do not match.' });
            return;
        }

        const result = await window.electronAPI.setMasterPassword({
            sessionId,
            masterPassword: password
        });

        if (result.success) {
            this.setState({
                success: result.message,
                fbAuth: true,
                onboardingStep: "3",
            });
            localStorage.setItem('onboardingStep', "3");
        } else {
            this.setState({ error: result.message });
        }
    };

    handleUnlockPassword = async () => {
        /**
         * this one is to verify that master o password is correcto.
         */
        const { unlockPassword, sessionId } = this.state;

        if (!unlockPassword || unlockPassword.length !== 24) {
            this.setState({ error: 'Master Password must be exactly 24 characters long.' });
            return;
        }

        const result = await window.electronAPI.verifyMasterPassword({
            sessionId,
            masterPassword: unlockPassword
        });

        if (result.success) {
            this.setState({
                success: result.message,
                onboardingStep: result.onboardingStep,
                fbAuth: result.onboardingStep === 4,
            });
            localStorage.setItem('onboardingStep', result.onboardingStep.toString());
        } else {
            this.setState({ error: result.message });
        }
    };

    render() {
        const {
            password, confirmPassword, unlockPassword,
            error, success, fbAuth, onboardingStep
        } = this.state;

        if (fbAuth) {
            return <Navigate to="/facebook-auth" />;
        }

        if (onboardingStep === 5) {
            // fbAuth has been found in database.
            return <Navigate to="/dashboard" />;
        }


        return (
            <div className="container mt-5">
                <div className="row mt-4">
                    {/* set masterpassword */}
                    {onboardingStep === "2" && (
                        <>
                            <h2>🔐 Master Password Setup</h2>
                            <p className="text-muted mt-3">
                                The master password will be used to encrypt all of your sensitive data.
                                <br />
                                It must be <strong>exactly 24 characters</strong> long and will not be recoverable.
                                <br />
                                If you forget it, your encrypted data will be permanently inaccessible.
                            </p>
                            <div className="col-md-6">
                                <input
                                    type="password"
                                    className="form-control mb-3"
                                    placeholder="Enter Master Password"
                                    value={password}
                                    onChange={(e) => this.handleChange('password', e.target.value)}
                                />
                                <input
                                    type="password"
                                    className="form-control mb-3"
                                    placeholder="Confirm Master Password"
                                    value={confirmPassword}
                                    onChange={(e) => this.handleChange('confirmPassword', e.target.value)}
                                />
                                <button className="btn btn-primary w-100" onClick={this.handleSubmit}>
                                    Save Master Password
                                </button>

                                {error && <div className="alert alert-danger mt-3">{error}</div>}
                                {success && <div className="alert alert-success mt-3">{success}</div>}
                            </div>
                        </>
                    )}
                    {/* unlock for step 3 and 4 */}
                    {onboardingStep !== "2" && (
                        <div className="col-md-6">
                            <h2>🔓 Unlock Your Account</h2>
                            <input
                                type="password"
                                className="form-control mt-3"
                                placeholder="Enter Master Password to Unlock"
                                value={unlockPassword}
                                onChange={(e) => this.handleChange('unlockPassword', e.target.value)}
                            />
                            <button className="btn btn-primary w-100 mt-2" onClick={this.handleUnlockPassword}>
                                Unlock Your Account
                            </button>

                            {error && <div className="alert alert-danger mt-3">{error}</div>}
                            {success && <div className="alert alert-success mt-3">{success}</div>}
                        </div>
                    )}
                </div>
            </div>
        );
    }
}

export default MasterPassword;
