import React from 'react';
import Sidebar from '../component/sidebar';
import SessionContext from '../context/SessionContext';

class Stat extends React.Component {
    static contextType = SessionContext;

    render() {
        return (
            <div className="container mt-4">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    {/* Left: Hamburger (Sidebar) */}
                    <div className="d-flex align-items-center">
                        <Sidebar />
                        <h3 className="px-4">📊 MetaPriv: Usage Statistics</h3>
                    </div>
                </div>

            </div>
        );
    }
}

export default Stat;