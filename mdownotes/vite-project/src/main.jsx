import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// import './index.css'
import App1 from './App1.jsx'


const id = parseInt(window.id5, 10); // Ensure it's a number
const videoId1 = String(window.VIDEO_ID); // Ensure it's a string

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App1 id = {id} videoId = {videoId1}></App1>
  </StrictMode>,
)
