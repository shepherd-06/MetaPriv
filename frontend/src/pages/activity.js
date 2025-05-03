import React from "react";
import Sidebar from "../component/sidebar";
import SessionContext from "../context/SessionContext";



class ActivityLogView extends React.Component {
    static contextType = SessionContext;

    constructor(props) {
        super(props);
        this.state = {
            logs: [],
            errorMessage: null,
            currentPage: 1,
            logsPerPage: 50,
        };
    }

    async componentDidMount() {
        const sessionId = this.context;
        try {
            const logs = await window.electronAPI.fetchAllLogs(sessionId);
            if (logs.success) {
                this.setState({ logs: logs.logs });
            } else {
                console.error("Failed to fetch logs: ", logs.message);
                this.setState({ logs: [], errorMessage: logs.message });
            }
        } catch (error) {
            console.error("Failed to fetch logs:", error);
        }
    }

    handlePrevPage = () => {
        this.setState((prevState) => ({
            currentPage: Math.max(prevState.currentPage - 1, 1)
        }));
    };

    handleNextPage = () => {
        const { currentPage, logs, logsPerPage } = this.state;
        const totalPages = Math.ceil(logs.length / logsPerPage);
        this.setState((prevState) => ({
            currentPage: Math.min(prevState.currentPage + 1, totalPages)
        }));
    };

    renderLogs = (logsToShow) => {
        return logsToShow.map((log, index) => {
            const match = log.match(/^\[(.*?)\](.*)$/); // Extract timestamp and message
            const timestamp = match ? match[1] : '';
            const message = match ? match[2] : log;

            const isError = log.includes('Failed to decrypt -');

            return (
                <div
                    key={index}
                    className={`mb-2 ${isError ? 'text-danger' : 'text-muted'}`}
                    style={{ wordBreak: 'break-word' }}
                >
                    <span className="fw-bold text-primary">[{timestamp}]</span>{message}
                </div>
            );
        });
    };

    render() {
        const { logs, currentPage, logsPerPage } = this.state;
        const totalPages = Math.ceil(logs.length / logsPerPage);
        let currentLogs = [];

        // Calculate logs for current page
        const indexOfLastLog = currentPage * logsPerPage;
        const indexOfFirstLog = indexOfLastLog - logsPerPage;
        if (logs.length > 0) {
            currentLogs = logs.slice(indexOfFirstLog, indexOfLastLog);
        }


        return (
            <div className="container mt-4">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    <Sidebar />
                    <h2 className="m-0">Activity Log</h2>
                    <div></div>
                </div>

                <div className="text-center mb-3">
                    <p className="text-muted">Below is a log of all your recent activities.</p>
                </div>

                <div style={{ maxHeight: '70vh', overflowY: 'auto', border: '1px solid #dee2e6', padding: '1rem', borderRadius: '0.25rem' }}>
                    {currentLogs.length > 0 ? (
                        this.renderLogs(currentLogs)
                    ) : (
                        <>
                            <p className="text-center text-muted">No logs available.</p>
                            {this.state.errorMessage && (
                                <p className="text-center btn-error">{this.state.errorMessage}</p>
                            )}
                        </>
                    )}
                </div>

                <div className="d-flex justify-content-between align-items-center mt-3">
                    <button
                        className="btn btn-secondary"
                        onClick={this.handlePrevPage}
                        disabled={currentPage === 1}
                    >
                        Prev
                    </button>
                    <span className="text-muted">
                        Page {currentPage} of {totalPages || 1}
                    </span>
                    <button
                        className="btn btn-success"
                        onClick={this.handleNextPage}
                        disabled={currentPage === totalPages || totalPages === 0}
                    >
                        Next
                    </button>
                </div>
            </div>
        );
    }
}

export default ActivityLogView;
