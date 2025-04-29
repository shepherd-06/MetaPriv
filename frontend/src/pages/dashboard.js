import React from "react";
import Sidebar from "../component/sidebar";
import 'bootstrap/dist/css/bootstrap.min.css';
import SessionContext from "../context/SessionContext";


class Dashboard extends React.Component {
    static contextType = SessionContext;

    constructor(props) {
        super(props);
        this.state = {
            sessionValid: true,
            botRunning: false,
            loadingBot: false,
        };

        this.handleRun = this.handleRun.bind(this);
        this.handleQuit = this.handleQuit.bind(this);
        this.handleStopBot = this.handleStopBot.bind(this);
        this.checkSessionValidity = this.checkSessionValidity.bind(this);
        this.checkBotStatus = this.checkBotStatus.bind(this);
    }

    async componentDidMount() {
        await this.checkSessionValidity();
        await this.checkBotStatus();
        this.sessionInterval = setInterval(this.checkSessionValidity, 5 * 60 * 1000); // every 5 min
        this.botStatusInterval = setInterval(this.checkBotStatus, 5 * 1000); // every 5 sec
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
            window.location.href = "/"; // redirect to login
        }
    }

    async checkBotStatus() {
        const result = await window.electronAPI.isBotRunning();
        this.setState({ botRunning: result, loadingBot: false });
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
        const { botRunning, loadingBot } = this.state;

        return (
            <div className="container mt-4">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    {/* Hamburger */}
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
            </div>
        );
    }
}

export default Dashboard;
