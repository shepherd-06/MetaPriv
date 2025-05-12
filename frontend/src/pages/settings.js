import React from 'react';
import Sidebar from "../component/sidebar";
import SessionContext from "../context/SessionContext";


class Settings extends React.Component {
    static contextType = SessionContext;

    constructor(props) {
        super(props);
        this.state = {
            syncEnabled: false,
            backendUrl: '',
            syncPeriod: '1',
            botRunFrequency: '3'
        };
    }

    componentDidMount() {
        this.refreshSyncStatus();
    }

    handleToggleSync = () => {
        this.setState((prevState) => ({ syncEnabled: !prevState.syncEnabled }));
    };

    handleInputChange = (e) => {
        this.setState({ [e.target.name]: e.target.value });
    };

    handleSaveBackendUrl = async () => {
        const { syncEnabled, backendUrl, syncPeriod } = this.state;

        if (!syncEnabled) {
            console.log('Sync is not enabled.');
            return;
        }

        if (!backendUrl) {
            console.error('Backend URL is required.');
            return;
        }

        try {
            const sessionId = this.context;
            const result = await window.electronAPI.saveSyncSettings({
                sessionId,
                backendUrl,
                syncPeriod
            });

            if (result.success) {
                alert(result.message);
                this.refreshSyncStatus(); // Refresh after save
            } else {
                alert(`Failed: ${result.message}`);
            }
        } catch (error) {
            console.error('Error saving sync settings:', error);
            alert(`Error: ${error.message}`);
        }
    };


    handleClearKeywords = () => {
        console.log('Clearing all keywords...');
        // Add your clear logic here
    };

    handleSaveBotFrequency = () => {
        console.log('Saved Bot Run Frequency:', this.state.botRunFrequency);
        // Add your save logic here
    };

    refreshSyncStatus = async () => {
        const sessionId = this.context;

        try {
            const result = await window.electronAPI.fetchSyncStatus(sessionId);
            if (result.success && result.data) {
                const { backendUrl, syncPeriod } = result.data;

                this.setState({
                    syncEnabled: true,
                    backendUrl: backendUrl || '',
                    syncPeriod: syncPeriod || '1'
                });
            } else {
                console.warn('No sync config found or fetch failed:', result.message);
            }
        } catch (err) {
            console.error('Error fetching sync status:', err);
        }
    };

    render() {
        const { syncEnabled, backendUrl, syncPeriod, botRunFrequency } = this.state;

        return (
            <div style={{ height: '100vh', overflowY: 'auto', paddingBottom: "50px" }} className="container my-4">

                <div className="d-flex justify-content-left align-items-center mb-4">
                    {/* Hamburger */}
                    <Sidebar />
                    <h1 className="px-4">Settings</h1>

                </div>

                {/* Sync Section */}
                <div className="card mb-4">
                    <div className="card-header">
                        <h5>Sync Settings</h5>
                    </div>
                    <div className="card-body">
                        <div className="form-check form-switch mb-3">
                            <input
                                className="form-check-input"
                                type="checkbox"
                                checked={syncEnabled}
                                onChange={this.handleToggleSync}
                                id="syncToggle"
                            />
                            <label className="form-check-label" htmlFor="syncToggle">
                                Enable Sync
                            </label>
                        </div>

                        {syncEnabled && (
                            <>
                                <div className="mb-3">
                                    <label className="form-label">Backend URL</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        name="backendUrl"
                                        value={backendUrl}
                                        onChange={this.handleInputChange}
                                        placeholder="https://your-backend.com/api"
                                    />
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">Sync Period</label>
                                    <select
                                        className="form-select"
                                        name="syncPeriod"
                                        value={syncPeriod}
                                        onChange={this.handleInputChange}
                                    >
                                        <option value="1">Every hour</option>
                                        <option value="2">Every 2 hours</option>
                                        <option value="6">Every 6 hours</option>
                                        <option value="12">Every 12 hours</option>
                                        <option value="24">Per day</option>
                                    </select>
                                </div>

                                <button
                                    className="btn btn-primary"
                                    onClick={this.handleSaveBackendUrl}
                                >
                                    Save Sync Settings
                                </button>
                            </>
                        )}
                    </div>
                </div>

                {/* Clear Keywords Section */}
                <div className="card mb-4">
                    <div className="card-header">
                        <h5>Keyword Management</h5>
                    </div>
                    <div className="card-body">
                        <p>Clear All Keywords</p>
                        <button
                            className="btn btn-danger"
                            onClick={this.handleClearKeywords}
                            disabled
                        >
                            Clear Keywords
                        </button>
                    </div>
                </div>

                {/* Bot Frequency Section */}
                <div className="card mb-4">
                    <div className="card-header">
                        <h5>Bot Run Settings</h5>
                    </div>
                    <div className="card-body">
                        <div className="mb-3">
                            <label className="form-label">How often do you run the bot?</label>
                            <select
                                className="form-select"
                                name="botRunFrequency"
                                value={botRunFrequency}
                                onChange={this.handleInputChange}
                                disabled
                            >
                                <option value="3">Every 3 hours</option>
                                <option value="6">Every 6 hours</option>
                                <option value="12">Every 12 hours</option>
                            </select>
                        </div>

                        <p className="text-muted">
                            Note: The interval between each iteration will be randomized
                            between the selected period and the next +3 hours (e.g., if set to 3
                            hours, it will run between 3–6 hours).
                        </p>

                        <button
                            className="btn btn-primary"
                            onClick={this.handleSaveBotFrequency}
                            disabled
                        >
                            Save Bot Settings
                        </button>
                    </div>
                </div>
            </div>
        );
    }
}

export default Settings;
