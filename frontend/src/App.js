import React, { Component } from 'react';
import './App.css';

class App extends Component {
  constructor(props) {
    super(props);
    this.handleRun = this.handleRun.bind(this);
    this.handleQuit = this.handleQuit.bind(this);
  }

  async handleRun() {
    const result = await window.electronAPI.runBot();
    alert(result);
  }

  handleQuit() {
    window.electronAPI.quitApp();
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1>🧠 MetaPriv Control Panel</h1>
          <p>Use the buttons below to interact with the automation bot.</p>

          <button onClick={this.handleRun} style={{ padding: '10px 20px', margin: '10px' }}>
            ▶️ Start Bot
          </button>

          <button onClick={this.handleQuit} style={{ padding: '10px 20px', margin: '10px' }}>
            ❌ Quit App
          </button>
        </header>
      </div>
    );
  }
}

export default App;
