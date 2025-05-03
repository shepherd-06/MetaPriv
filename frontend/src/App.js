import React, { Component } from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';

// Pages
import Onboarding from './pages/onboarding';
import Dashboard from './pages/dashboard';
import FacebookAuth from './pages/fbAuth';
import MasterPassword from './pages/masterPassword';
import Keyword from './pages/keywords';
import ActivityLogView from './pages/activity';

// util
import { cacheManager } from './utility/cachemanager';

// context
import SessionContext from './context/SessionContext';


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      sessionId: null,
      onboardingStep: '1',
      loading: true,
    };
  }

  async componentDidMount() {
    const { sessionId, onboardingStep } = await cacheManager();
    const loading = false;
    this.setState({ sessionId, onboardingStep, loading });
  }

  render() {
    const { sessionId, onboardingStep, loading } = this.state;

    if (loading) return <div className="text-center mt-5">Loading...</div>;

    const isLoggedIn = !!sessionId;

    return (
      <SessionContext.Provider value={sessionId}>
        <Router>
          <Routes>
            {/* Home Route: determine onboarding flow */}
            <Route path="/" element={
              !isLoggedIn ? (
                <Onboarding />
              ) : (
                <Navigate to="/master-password" />
              )
            } />

            {/* Protected Routes */}
            <Route path="/dashboard" element={
              isLoggedIn ? <Dashboard /> : <Navigate to="/" />
            } />

            <Route path="/keywords" element={
              isLoggedIn ? <Keyword /> : <Navigate to="/" />
            } />

            <Route path="/master-password" element={
              isLoggedIn ? <MasterPassword /> : <Navigate to="/" />
            } />
            <Route path="/facebook-auth" element={
              isLoggedIn ? <FacebookAuth /> : <Navigate to="/" />
            } />

            <Route path="/activity-log" element={
              isLoggedIn ? <ActivityLogView /> : <Navigate to="/" />
            } />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </Router>
      </SessionContext.Provider>
    );
  }
}

export default App;
