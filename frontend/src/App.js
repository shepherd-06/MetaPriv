import React, { Component } from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';


/**
 * pages
 */
import Onboarding from './pages/onboarding';
import Dashboard from './pages/dashboard';

class App extends Component {

  constructor(props) {
    super(props);
    this.state = {
      sessionId: null,
      onboardingStep: '1',
    };
  }

  componentDidMount() {
    const sessionId = localStorage.getItem('sessionId');
    const onboardingStep = localStorage.getItem('onboardingStep');
  
    if (sessionId) {
      // Validate session asynchronously
      window.electronAPI.validateSession(sessionId).then((result) => {
        if (result.valid) {
          console.log("✅ Session is valid. User ID:", result.userId);
          this.setState({
            sessionId,
            onboardingStep,
          });
        } else {
          console.log("❌ Session invalid or expired. Clearing storage...");
          localStorage.removeItem('sessionId');
          localStorage.removeItem('onboardingStep');
          this.setState({
            sessionId: null,
            onboardingStep: '1',
          });
        }
      }).catch((err) => {
        console.error("Error validating session:", err);
        localStorage.removeItem('sessionId');
        localStorage.removeItem('onboardingStep');
        this.setState({
          sessionId: null,
          onboardingStep: '1',
        });
      });
    } else {
      // No session at all
      this.setState({
        sessionId: null,
        onboardingStep: '1',
      });
    }
  }
  


  render() {
    const { sessionId, onboardingStep } = this.state;

    return (
      <Router>
        <Routes>
          {/* If logged in, go to dashboard. Otherwise show onboarding */}
          <Route path="/" element={
            sessionId ? <Navigate to="/dashboard" /> : <Onboarding />
          } />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </Router>
    );
  }
}


export default App;
