import React from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import { Link } from 'react-router-dom';
import { logout } from "../utility/logout";

class Sidebar extends React.Component {
    render() {
        return (
            <>
                {/* Hamburger Button */}
                <button className="btn btn-outline-secondary" type="button" data-bs-toggle="offcanvas" data-bs-target="#sideMenu">
                    ☰
                </button>

                {/* Offcanvas Sidebar */}
                <div className="offcanvas offcanvas-start" tabIndex="-1" id="sideMenu">
                    <div className="offcanvas-header">
                        <h5 className="offcanvas-title">📂 Menu</h5>
                        <button type="button" className="btn-close" data-bs-dismiss="offcanvas"></button>
                    </div>
                    <div className="offcanvas-body">
                        <ul className="list-group">
                            <li className="list-group-item" style={{ cursor: 'pointer' }}>
                                <Link to="/dashboard" className="text-decoration-none">🏠 Dashboard</Link>
                            </li>

                            <li className="list-group-item" style={{ cursor: 'pointer' }}>
                                <Link to="/keywords" className="text-decoration-none">🔑 Keywords</Link>
                            </li>

                            <li className="list-group-item" style={{ cursor: 'pointer' }}>
                                <Link to="/activity-log" className="text-decoration-none">🗒️ Activity Log</Link>
                            </li>

                            <li className="list-group-item" style={{ cursor: 'pointer' }}>
                                <Link to="/stat" className="text-decoration-none">📊 Statistics</Link>
                            </li>

                            <li className="list-group-item" style={{ cursor: 'pointer' }}>
                                <Link to="/settings" className="text-decoration-none">⚙️ Privacy Settings</Link>
                            </li>

                            <li
                                className="list-group-item text-primary"
                                style={{ cursor: 'pointer' }}
                                onClick={logout}
                            >
                                🚪 Logout
                            </li>
                        </ul>
                    </div>
                </div>
            </>
        );
    }
}

export default Sidebar;
