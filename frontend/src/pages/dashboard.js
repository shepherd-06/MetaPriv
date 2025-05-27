import React from "react";
import { Link, Navigate } from "react-router-dom";
import Sidebar from "../component/sidebar";
import 'bootstrap/dist/css/bootstrap.min.css';
import SessionContext from "../context/SessionContext";
import ShowActiveLog from "../component/showLog";

class Dashboard extends React.Component {
    static contextType = SessionContext;

    constructor(props) {
        super(props);
        this.state = {
            sessionValid: true,
            botRunning: false,
            loadingBot: false,
            checkingKeywords: true,
            keywordStatus: null,
            redirectToKeywords: false,
            showToast: false, // show/hide toast
            toastMessage: '', // message text
            toastType: '',    // success, warning, etc.

        };

        this.handleRun = this.handleRun.bind(this);
        this.handleQuit = this.handleQuit.bind(this);
        this.handleStopBot = this.handleStopBot.bind(this);
        this.checkSessionValidity = this.checkSessionValidity.bind(this);
        this.checkBotStatus = this.checkBotStatus.bind(this);
        this.checkKeywordStatus = this.checkKeywordStatus.bind(this); // 🆕
    }

    async componentDidMount() {
        await this.checkSessionValidity();
        await this.checkBotStatus();
        await this.checkKeywordStatus(); // 🆕
        this.sessionInterval = setInterval(this.checkSessionValidity, 5 * 60 * 1000);
        this.botStatusInterval = setInterval(this.checkBotStatus, 5 * 1000);
    }

    componentWillUnmount() {
        clearInterval(this.sessionInterval);
        clearInterval(this.botStatusInterval);
    }

    async checkSessionValidity() {
        const sessionId = this.context;
        const result = await window.electronAPI.validateSession(sessionId);
        if (!result || !result.valid) {
            localStorage.removeItem('sessionId');
            localStorage.removeItem('onboardingStep');
            // TODO: need to have a proper logout function
            return <Navigate to="/" />;
        }
    }

    async checkBotStatus() {
        const result = await window.electronAPI.isBotRunning();
        this.setState({ botRunning: result, loadingBot: false });
    }

    async checkKeywordStatus() {
        const sessionId = this.context;
        this.setState({ checkingKeywords: true });

        const result = await window.electronAPI.countKeywords(sessionId);

        if (result && !result.success) {
            // No keywords: show warning toast and redirect
            this.setState({
                showToast: true,
                toastMessage: '❌ No keywords found. Redirecting in 2 seconds...',
                toastType: 'warning',
            });
            setTimeout(() => {
                this.setState({ redirectToKeywords: true });
            }, 2000);
        } else if (result && result.success) {
            // Keywords found: show success toast
            this.setState({
                showToast: true,
                toastMessage: `${result.message}. Ready to run the bot!`,
                toastType: 'success',
            });
        }

        this.setState({
            checkingKeywords: false,
            keywordStatus: result,
        });

        // Hide toast after a while
        setTimeout(() => {
            this.setState({ showToast: false });
        }, 4000);
    }


    async handleRun() {
        const sessionId = this.context;
        this.setState({ loadingBot: true });
        await window.electronAPI.runBot({
            sessionId,
        });
    }

    async handleStopBot() {
        await window.electronAPI.stopBot();
        this.setState({ botRunning: false });
    }

    handleQuit() {
        window.electronAPI.quitApp();
    }

    render() {
        const { botRunning, loadingBot, checkingKeywords, keywordStatus, redirectToKeywords } = this.state;

        if (redirectToKeywords) {
            return <Navigate to="/keywords" replace />;
        }

        return (
            <div className="container mt-4">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    <Sidebar />
                    <h2 className="m-0">🧠 MetaPriv Control Panel</h2>
                    <button className="btn btn-danger" onClick={this.handleQuit}>❌ Quit App</button>
                </div>

                <div className="text-center">
                    <p className="text-muted">Use the buttons below to interact with the automation bot.</p>

                    {botRunning ? (
                        <div className="row justify-content-center align-items-center mb-3">
                            <div className="col-auto">
                                <p className="text-success m-0" style={{
                                    padding: "5px 10px",
                                    border: "1px dashed #32CBFF",
                                    borderRadius: "5px"
                                }}>
                                    ✅ Bot is running...
                                </p>
                            </div>
                            <div className="col-auto">
                                <button className="btn btn-warning" onClick={this.handleStopBot}>
                                    ⛔ Stop Bot
                                </button>
                            </div>
                        </div>
                    ) : (
                        <button
                            className="btn btn-success"
                            onClick={this.handleRun}
                            disabled={loadingBot}
                        >
                            {loadingBot ? (
                                <>
                                    <span className="spinner-border spinner-border-sm me-2" role="status" />
                                    Starting Bot...
                                </>
                            ) : (
                                "▶️ Start Bot"
                            )}
                        </button>
                    )}
                </div>

                {botRunning && <ShowActiveLog isBotRunning={botRunning} />}

                {/* Toast */}
                <div className="position-fixed bottom-0 end-0 p-3" style={{ zIndex: 9999 }}>
                    <div className={`toast align-items-center text-bg-${this.state.toastType} border-0 ${this.state.showToast ? 'show' : ''}`} role="alert" aria-live="assertive" aria-atomic="true">
                        <div className="d-flex">
                            <div className="toast-body">
                                {this.state.toastMessage}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

export default Dashboard;
