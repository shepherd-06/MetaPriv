import React from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import Sidebar from "../component/sidebar";

class Keyword extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            showAddForm: false,
            keywordInputs: [''],
        };

        this.handleAddMoreInput = this.handleAddMoreInput.bind(this);
        this.toggleAddForm = this.toggleAddForm.bind(this);
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmitKeywords = this.handleSubmitKeywords.bind(this);
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

    handleSubmitKeywords() {
        console.log("Submitting keywords:", this.state.keywordInputs);
        // Placeholder: later will send to backend
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
                        <button className="btn btn-danger">
                            ➖ Remove Keyword
                        </button>
                    </div>
                </div>


                <div className="row">
                    {/* Active Keywords */}
                    <div className="col-md-6">
                        <h4>📝 Active Keywords</h4>
                        <ul className="list-group mt-3">
                            {/* Placeholder, later will be mapped from backend */}
                            <li className="list-group-item">pikachu</li>
                            <li className="list-group-item">privacy</li>
                            <li className="list-group-item">security</li>
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
