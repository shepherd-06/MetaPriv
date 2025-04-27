import React from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import Sidebar from "../component/sidebar";
import SessionContext from "../context/SessionContext";

class Keyword extends React.Component {
    static contextType = SessionContext;

    constructor(props) {
        super(props);
        this.state = {
            showAddForm: false,
            keywordInputs: [''], // List of NEW keywords
            keywordsList: [], // 🆕 list of active keywords
        };

        this.handleAddMoreInput = this.handleAddMoreInput.bind(this);
        this.toggleAddForm = this.toggleAddForm.bind(this);
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmitKeywords = this.handleSubmitKeywords.bind(this);
    }

    async componentDidMount() {
        const sessionId = this.context;
        if (!sessionId) {
            window.location.href = "/";
        } else {
            await this.handleFetchKeywords();
        }
    }

    toggleAddForm() {
        this.setState({ showAddForm: !this.state.showAddForm });
    }

    handleAddMoreInput() {
        this.setState(prevState => ({
            keywordInputs: [...prevState.keywordInputs, '']
        }));
    }

    handleInputChange(index, value) {
        const updatedInputs = [...this.state.keywordInputs];
        updatedInputs[index] = value;
        this.setState({ keywordInputs: updatedInputs });
    }

    async handleSubmitKeywords() {
        const sessionId = this.context;
        const { keywordInputs } = this.state;

        // Clean up empty inputs
        const keywordsToAdd = keywordInputs.map(k => k.trim()).filter(k => k);

        if (keywordsToAdd.length === 0) {
            alert("Please enter at least one keyword.");
            return;
        }

        const result = await window.electronAPI.addKeywords({
            sessionId,
            keywords: keywordsToAdd,
        });

        if (result.success) {
            alert(result.message);
            this.setState({ keywordInputs: [''], showAddForm: false });
            this.handleFetchKeywords(); // refresh
        } else {
            alert(result.message);
        }
    }

    async handleFetchKeywords() {
        const sessionId = this.context; // from SessionContext
        const result = await window.electronAPI.fetchKeywords(sessionId);

        if (result.success) {
            console.log("Fetched Keywords: ", result.keywords);
            this.setState({ keywordsList: result.keywords });
        } else {
            console.error(result.message);
        }
    }


    render() {
        const { showAddForm, keywordInputs } = this.state;

        return (
            <div className="container mt-4">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    {/* Left: Hamburger (Sidebar) */}
                    <div>
                        <Sidebar />
                    </div>

                    {/* Right: Buttons */}
                    <div className="d-flex">
                        <button className="btn btn-primary me-2" onClick={this.toggleAddForm}>
                            ➕ Add Keyword
                        </button>
                        <button className="btn btn-danger" disabled>
                            ➖ Remove Keyword
                        </button>
                    </div>
                </div>


                <div className="row">
                    {/* Active Keywords */}
                    <div className="col-md-6">
                        <h4>Active Keywords</h4>
                        <ul className="list-group">
                            {this.state.keywordsList.length > 0 && this.state.keywordsList.map((keyword) => (
                                <li key={keyword.id} className="list-group-item">
                                    {keyword.text}
                                </li>
                            ))}

                            {
                                this.state.keywordsList.length === 0 && (
                                    <p> No Active KeyWords at the moment!</p>
                                )
                            }


                        </ul>
                    </div>

                    {/* Add Keywords Form */}
                    {showAddForm && (
                        <div className="col-md-6">
                            <h4>➕ Add New Keywords</h4>
                            {keywordInputs.map((input, index) => (
                                <input
                                    key={index}
                                    type="text"
                                    className="form-control mb-2"
                                    placeholder="Enter keyword"
                                    value={input}
                                    onChange={(e) => this.handleInputChange(index, e.target.value)}
                                />
                            ))}

                            <button className="btn btn-secondary mb-2 w-100" onClick={this.handleAddMoreInput}>
                                ➕ Add Another
                            </button>

                            <button className="btn btn-success w-100" onClick={this.handleSubmitKeywords}>
                                ✅ Submit Keywords
                            </button>
                        </div>
                    )}
                </div>
            </div>
        );
    }
}

export default Keyword;
