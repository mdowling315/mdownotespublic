import React, { useState, useEffect, StrictMode, useCallback } from "react";
import PropTypes from "prop-types";
// import InfiniteScroll from "react-infinite-scroll-component";
import './App1.css'

export default function App1({id, videoId }) {
    const [player, setPlayer] = useState(null);
    const [timestamp, setTimestamp] = useState(null);
  
    // This function is called when the YouTube IFrame API is ready
    window.onYouTubeIframeAPIReady = () => {
      const playerInstance = new window.YT.Player('youtube-player', {
        videoId: videoId,
        events: {
          onReady: onPlayerReady,
        },
      });
      setPlayer(playerInstance);
    };
  
    // This function runs when the YouTube player is ready
    const onPlayerReady = (event) => {
      console.log('Player is ready.');
    };
  
    useEffect(() => {
      // Dynamically load the YouTube IFrame API script
      console.log(id)
      console.log(window.id5);
      console.log(videoId)
      console.log(window.VIDEO_ID);
      console.log("beforebranch")
      if (!window.YT) {
        const script = document.createElement('script');
        script.src = "https://www.youtube.com/iframe_api";
        script.onload = () => console.log("YouTube API Script Loaded");
        document.body.appendChild(script);
      }
      else{
        console.log("didnt take branch")
      }
    }, []);
  
    // Function to update timestamp
    const updateTimestamp = () => {
      if (player && typeof player.getCurrentTime === 'function') {
        const currentTime = player.getCurrentTime();
        console.log('Current Timestamp:', currentTime);
        setTimestamp(currentTime);
      }
    };
  
    return (
      <div className = "split">
        <div className="left"> <p>something in the blue box yay </p></div>
        <div className="right">
            <iframe
            id="youtube-player"
            width="100%"
            height="400"
            src={`https://www.youtube.com/embed/${videoId}?enablejsapi=1`}
            allow="autoplay; encrypted-media"
            allowFullScreen
            title="YouTube Video Player"
            ></iframe>

            {/* Button to log timestamp */}
            <button onClick={updateTimestamp} style={{ marginTop: '20px' }}>
            Log Current Timestamp
            </button>

            
        {/* Display the timestamp */}
        {timestamp !== null && <p>Current Timestamp: {timestamp} seconds</p>}

        <br></br>
        
        <form style={{ marginTop: '30px' }} action="/delete_vid/" method="post" encType="multipart/form-data">
            <label> Delete Video </label><br />
            <label> Type "Confirm Delete" to delete this video </label>
            <input type="text" name="confirm" required />
            <input type="hidden" name="id" value={id} />
            <input type="hidden" name="nonce" value={String(videoId)} />
            <input type="submit" name="Delete" value="Delete" />
        </form>
        
        </div>
      </div>
    );
  };


App1.propTypes = {
id: PropTypes.number.isRequired,
videoId: PropTypes.string.isRequired,
};
