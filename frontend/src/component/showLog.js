import React from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import SessionContext from "../context/SessionContext";

class ShowActiveLog extends React.Component {
    static contextType = SessionContext;

    constructor(props) {
        super(props);
        this.state = {
            logs: [],
            lastMessage: "",  // keeps track of the last received log line
        };
        this.fetchLogs = this.fetchLogs.bind(this);
    }

    componentDidMount() {
        if (this.props.isBotRunning) {
            this.startFetching();
        }
    }

    componentDidUpdate(prevProps) {
        if (prevProps.isBotRunning !== this.props.isBotRunning) {
            if (this.props.isBotRunning) {
                this.startFetching();
            } else {
                this.stopFetching();
            }
        }
    }

    componentWillUnmount() {
        this.stopFetching();
    }

    startFetching() {
        this.fetchLogs(); // fetch immediately
        this.logInterval = setInterval(this.fetchLogs, 5000); // fetch every 5s
    }

    stopFetching() {
        if (this.logInterval) {
            clearInterval(this.logInterval);
            this.logInterval = null;
        }
    }

    async fetchLogs() {
        const sessionId = this.context;
        if (!sessionId) return;

        const { lastMessage } = this.state;
        const currentTime = new Date().toISOString();

        try {
            const result = await window.electronAPI.fetchRecentLogs({
                sessionId,
                currentTime,
                lastMessage,
            });

            if (result && result.success && Array.isArray(result.logs)) {
                if (result.logs.length > 0) {
                    const newLogs = [...this.state.logs, ...result.logs];
                    const newLastMessage = result.logs[result.logs.length - 1]; // last log line
                    this.setState({
                        logs: newLogs,
                        lastMessage: newLastMessage,
                    });
                }
            } else {
                console.error("Failed to fetch logs or no logs returned.");
            }
        } catch (error) {
            console.error("Error fetching logs:", error);
        }
    }

    render() {
        const { logs } = this.state;

        return (
            <div className="card mt-4" style={{ height: "300px", overflowY: "scroll" }}>
                <div className="card-header">
                    <h5 className="m-0">📜 Live Bot Logs</h5>
                </div>
                <ul className="list-group list-group-flush">
                    {logs.length > 0 ? (
                        logs.map((log, index) => (
                            <li key={index} className="list-group-item small">
                                {log}
                            </li>
                        ))
                    ) : (
                        <li className="list-group-item text-muted small">No logs yet...</li>
                    )}
                </ul>
            </div>
        );
    }
}

export default ShowActiveLog;
