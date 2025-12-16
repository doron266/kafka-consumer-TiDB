import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './styles.css'

// Bootstrap the React application into the root DOM node.
const rootElement = document.getElementById('root')
const root = createRoot(rootElement)
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
