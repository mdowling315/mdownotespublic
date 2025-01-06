import React, { useState, useEffect, StrictMode, useCallback } from "react";
import PropTypes from "prop-types";
// import InfiniteScroll from "react-infinite-scroll-component";
import './App1.css'

export default function App1({id, videoId }) {
    const [player, setPlayer] = useState(null);
    const [timestamp, setTimestamp] = useState(null);
    const [cur_load, setCurLoad] = useState([])
    const [comment, setComment] = useState("");
  
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

    function addComment(e) {
        e.preventDefault();
        if (comment.trim() !== "" && cur_load.length < 200) {
            if (player && typeof player.getCurrentTime === 'function') {
                const currentTime = player.getCurrentTime();
                console.log('Current Timestamp:', currentTime);
                setTimestamp(currentTime);
                const new_arr = [...cur_load, { timestamp: Math.floor(currentTime), text: comment }];
                new_arr.sort((a, b) => a.timestamp - b.timestamp);  // Numeric comparison for sorting
                setCurLoad(new_arr);
                setComment("");
              }
              else{
                console.log("something wrong with player")
              }
        }
        else{
            console.log("something wrong with comment")
            console.log(comment)
        }
    }



  
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
        <div className="left"> <h1>Current Load of Posts</h1> <h2>max 200 per load</h2>
        {cur_load.map((x) => (
            <div className="comment">
                <h3 className="left-align">{((x.timestamp-(x.timestamp%60))/60).toString().padStart(2, '0')}:{(x.timestamp%60).toString().padStart(2, '0')}: &#9;</h3>
                <p className="center-align">{x.text}</p>
            </div>
          
        ))}
        </div>
        <div className="right">

            <form style={{ marginTop: '30px' }} action="/delete_vid/" method="post" encType="multipart/form-data">
                <label> Delete Video </label><br />
                <label> Type "Confirm Delete" to delete this video </label>
                <input type="text" name="confirm" required />
                <input type="hidden" name="id" value={id} />
                <input type="hidden" name="nonce" value={String(videoId)} />
                <input type="submit" name="Delete" value="Delete" />
            </form>
            <br></br> <br></br>
            <iframe
            id="youtube-player"
            width="800"
            height="450"
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

        <form onSubmit={addComment}>
          <input
            type="text"
            value={comment}
            onChange={(e) => setComment(e.target.value)} // Update state with input
            placeholder="Enter your comment"
            disabled={false}
          />
        </form>

        <br></br>
        
        
        
        </div>
      </div>
    );
  };


App1.propTypes = {
id: PropTypes.number.isRequired,
videoId: PropTypes.string.isRequired,
};
