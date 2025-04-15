import './App.css';

function App() {
  const handleRun = async () => {
    const result = await window.electronAPI.runBot();
    alert(result);
  };

  const handleQuit = () => {
    window.electronAPI.quitApp();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🧠 MetaPriv Control Panel</h1>
        <p>Use the buttons below to interact with the automation bot.</p>

        <button onClick={handleRun} style={{ padding: '10px 20px', margin: '10px' }}>
          ▶️ Start Bot
        </button>

        <button onClick={handleQuit} style={{ padding: '10px 20px', margin: '10px' }}>
          ❌ Quit App
        </button>
      </header>
    </div>
  );
}

export default App;
