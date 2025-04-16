import React, { Component } from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';

// Pages
import Onboarding from './pages/onboarding';
import Dashboard from './pages/dashboard';
import FacebookAuth from './pages/fbAuth';
import MasterPassword from './pages/masterPassword';

// util
import cacheManager from './utility/cachemanager';


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
      <Router>
        <Routes>
          {/* Home Route: determine onboarding flow */}
          <Route path="/" element={
            !isLoggedIn ? (
              <Onboarding />
            ) : onboardingStep === '2' ? (
              <Navigate to="/master-password" />
            ) : onboardingStep === '3' ? (
              <Navigate to="/master-password" />
            ) : (
              <Navigate to="/dashboard" />
            )
          } />

          {/* Protected Routes */}
          <Route path="/dashboard" element={
            isLoggedIn ? <Dashboard /> : <Navigate to="/" />
          } />
          <Route path="/master-password" element={
            isLoggedIn ? <MasterPassword /> : <Navigate to="/" />
          } />
          <Route path="/facebook-auth" element={
            isLoggedIn ? <FacebookAuth /> : <Navigate to="/" />
          } />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    );
  }
}

export default App;
