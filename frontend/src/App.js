import React, { Component } from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';

// Pages
import Onboarding from './pages/onboarding';
import Dashboard from './pages/dashboard';
import FacebookAuth from './pages/fbAuth';
import MasterPassword from './pages/masterPassword';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      sessionId: null,
      onboardingStep: '1',
      loading: true,
    };
  }

  componentDidMount() {
    const sessionId = localStorage.getItem('sessionId');
    const onboardingStep = localStorage.getItem('onboardingStep');

    if (sessionId) {
      window.electronAPI.validateSession(sessionId).then((result) => {
        if (result && result.valid) {
          this.setState({
            sessionId,
            onboardingStep,
            loading: false,
          });
        } else {
          localStorage.removeItem('sessionId');
          localStorage.removeItem('onboardingStep');
          this.setState({
            sessionId: null,
            onboardingStep: '1',
            loading: false,
          });
        }
      }).catch((err) => {
        console.error("Error validating session:", err);
        localStorage.removeItem('sessionId');
        localStorage.removeItem('onboardingStep');
        this.setState({
          sessionId: null,
          onboardingStep: '1',
          loading: false,
        });
      });
    } else {
      this.setState({ sessionId: null, onboardingStep: '1', loading: false });
    }
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
              <Navigate to="/facebook-auth" />
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
