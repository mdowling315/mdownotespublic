import React, { useState, useEffect, StrictMode, useCallback } from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";
import './App1.css'
import Post from "./Post.jsx";
import SimplePost from "./SimplePost.jsx";

export default function App1({id, videoId, vididSQL}) {
    const [player, setPlayer] = useState(null);
    const [timestamp, setTimestamp] = useState(null);
    const [cur_load, setCurLoad] = useState([]);
    const [comment, setComment] = useState("");
    const [isDisabled, setIsDisabled] = useState(false);
    const [order, setOrder] = useState(false);
    const [reveal, setReveal] =useState(false);
    const [showCurLoad, setShowCurLoad] = useState(true);

    // "exported"
    const [arr, SetArr] = useState([]);
    const [arr1, SetArr1] = useState([]);
    const [nexturl, SetNexturl] = useState("");
    const [nexturl1, SetNexturl1] = useState("");
    const [NextAllowed, setNextAllowed] = useState(false);
    const [Fetched, setFetched] = useState(false);
    // const [RenderedPosts, setRenderedPosts] = useState([]);
  
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

    function addPost(e) {
        e.preventDefault();
        if (comment.trim() !== "" && cur_load.length < 200) {
            if (player && typeof player.getCurrentTime === 'function') {
                const currentTime = player.getCurrentTime();
                console.log('Current Timestamp:', currentTime);
                setTimestamp(currentTime);
                const new_arr = [...cur_load, { timestamp: Math.floor(currentTime), text: comment }];
                if (order){
                    new_arr.sort((a, b) => b.timestamp - a.timestamp );  // Numeric comparison for sorting
                }
                else{
                    new_arr.sort((a, b) => a.timestamp - b.timestamp);  // Numeric comparison for sorting
                }
                
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

    function update_order(){
        const new_arr = [...cur_load];
        if (!order){
            new_arr.sort((a, b) => b.timestamp - a.timestamp );  // Numeric comparison for sorting
        }
        else{
            new_arr.sort((a, b) => a.timestamp - b.timestamp);  // Numeric comparison for sorting
        }
        setCurLoad(new_arr);
        setOrder(!order)
    }

    function delete_post (index){
        const new_arr = [...cur_load];
        new_arr.splice(index,1);
        setCurLoad(new_arr);
    }

    const delete_post_net = (postid) => {
      fetch(`/api/posts/?postid=${postid}`, {
        method: "DELETE",
      })
        .then((response) => {
            if (!response.ok) {
              throw new Error("Failed to delete resource");
            } else {
              return
            }
          })
        .then(() => {
          // Update the state to remove the deleted post
          SetArr((prevArr) => prevArr.filter((x) => x.postid !== postid));
        })
        .catch((error) => {
          console.error("Error deleting post:", error);
        });
    }

    function sendPosts(e){
        if (cur_load.length != 0){
            setIsDisabled(true);
            fetch(`/api/posts/?vidid=${vididSQL}`, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                "Content-Type": "application/json", // Correct Content-Type
                },
                body: JSON.stringify({ batch: cur_load }),
            })
            setCurLoad([]);
        }
        else{
            e.preventDefault();
        }
    }

    //useEffect for fetching from REST API
    useEffect(() => {
        fetch(`/api/posts/?vidid=${vididSQL}&size=30`, {
          method: "GET",
          credentials: "same-origin", // how to do the authorization
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error("Failed to delete resource");
            } else {
              return response.json();
            }
          })
          .then((data) => {
            console.log(`next url set to ${data.next}`);
            SetArr(data.results);
            SetArr1(data.results);
            SetNexturl1(data.next);
            SetNexturl(data.next);
            setFetched(true);
          })
          .catch((error) => console.log(error));
      }, []);


    //useEffect for IFrame setup
    useEffect(() => {
      // Dynamically load the YouTube IFrame API script

      const handleBeforeUnload = (event) => {
        // Call sendPosts before the user exits
        // Optionally, show a confirmation message (not fully customizable in modern browsers)
        if (cur_load.length !=0){
            const message = 'Are you sure you want to leave? Your changes may not be saved.';
            event.returnValue = message; // Standard for most browsers
            return message; // For some older browsers
        }
      };
      window.addEventListener('beforeunload', handleBeforeUnload);
      //console.log(id)
      //console.log(window.id5);
      //console.log(videoId)
      //console.log(window.VIDEO_ID);
      //console.log("beforebranch")
      if (!window.YT) {
        const script = document.createElement('script');
        script.src = "https://www.youtube.com/iframe_api";
        script.onload = () => console.log("YouTube API Script Loaded");
        document.body.appendChild(script);
      }
      else{
        console.log("didnt take branch")
      }
      return () => {
        window.removeEventListener('beforeunload', handleBeforeUnload);
      };
    }, [cur_load]);
  
    // Function to update timestamp
    const updateTimestamp = () => {
      if (player && typeof player.getCurrentTime === 'function') {
        const currentTime = player.getCurrentTime();
        console.log('Current Timestamp:', currentTime);
        setTimestamp(currentTime);
      }
    };

    const fetchMoreData = () => {
        // console.log("tryna fetch with arr length: " + RenderedPosts.length);
        console.log("fetchmoreDatacalled");
    
        console.log(nexturl);
        fetch(nexturl, {
        method: "GET",
        credentials: "same-origin",
        })
        .then((response) => {
            if (response.ok) {
            return response.json();
            }
            throw new Error("Failed to fetch resource");
        })
        .catch((error) => console.log(error))
        .then((data) => {
            // debugger;
            // console.log("got the data from "+nexturl);
            console.log(data.results);
            // const newarr = [...arr];
            // const newarr1 = data.results;
            // debugger;
            SetArr([...arr, ...data.results]); // prevArr is the latest state
            SetNexturl(data.next); // Update nexturl as usual
            // console.log("next is :" + data.next);
        });
      }
    
      const fetchMoreData1 = () => {
        // console.log("tryna fetch with arr length: " + RenderedPosts.length);
        console.log("fetchmoreDatacalled");
    
        console.log(nexturl1);
        fetch(nexturl1, {
        method: "GET",
        credentials: "same-origin",
        })
        .then((response) => {
            if (response.ok) {
            return response.json();
            }
            throw new Error("Failed to fetch resource");
        })
        .catch((error) => console.log(error))
        .then((data) => {
            // debugger;
            // console.log("got the data from "+nexturl);
            console.log(data.results);
            // const newarr = [...arr];
            // const newarr1 = data.results;
            // debugger;
            SetArr1([...arr1, ...data.results]); // prevArr is the latest state
            SetNexturl1(data.next); // Update nexturl as usual
            // console.log("next is :" + data.next);
        });
      }

  
    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          addPost(e); // Submit the form when Enter is pressed
        }
      };

    return (
      <div className = "split">
        {showCurLoad ? (<div id="left"> <h1>Current Load of Posts</h1> 
        <button onClick={() => setShowCurLoad(false)}> Follow-Along with Posts </button>
        <div className="boxed-div">
        <h3> Send The Server Your Posts! </h3>
        <form onSubmit={sendPosts}>
                <input type="submit" name="Send" value="Send" />
        </form>
        </div>
        <h3> Count: {cur_load.length} (max 200 per load)</h3>
        <br></br>
        <button onClick={() => update_order()}> {order ? ("Switch to lowest-highest") : ("Switch to highest-lowest")}</button>
        <br></br>
        {cur_load.map((x, index) => (
            <div className="comment">
                {x.timestamp < 3600 ? (
                <h3 className="left-align">{((x.timestamp-(x.timestamp%60))/60).toString().padStart(2, '0')}:{(x.timestamp%60).toString().padStart(2, '0')} &#9; </h3>
                ) : (
                <h3 className="left-align">{((x.timestamp-(x.timestamp%3600))/3600).toString().padStart(1, '0')}:{(((x.timestamp-(x.timestamp%60))/60)%60).toString().padStart(2, '0')}:{(x.timestamp%60).toString().padStart(2, '0')} &#9; </h3>  
                )}
                <p className="center-align">{x.text}</p>
                <button className="right-align" onClick={() => delete_post(index)}>Delete</button>
            </div>
            
          
        ))}
       
        </div> ) : (
          <div id="left">
            <button onClick={() => setShowCurLoad(true)}>Back to Your Current Load of Posts </button>
          <InfiniteScroll 
              style = {{width: "100%"}}
              dataLength={arr1.length} // number of items in the  list
              hasMore={!!nexturl1} // boolean to determine if more data can lod
              next={fetchMoreData1}
              loader={<h4>Loading more posts...</h4>} // loader when fetching newdata
              scrollThreshold={0.9}
              scrollableTarget = "left"
              endMessage={
              <p style={{ textAlign: "center" }}>
                  <b>All posts loaded</b>
              </p>
              }
          >
              
              <br></br>
              <h1 style={{ textAlign: "center" }}>Posts</h1>
              <br></br>
              {arr1.map((x) => (
                  
                  <SimplePost  style={{ textAlign: "center" }} key = {x.postid} url = {x.url} postid = {x.postid} ></SimplePost>
              ))}
          </InfiniteScroll>
          </div>
        )}
        <div className="right">
            <div id = "right-bottom">

                <form style={{ marginTop: '30px', textAlign: 'center' }} action="/delete_vid/" method="post" encType="multipart/form-data">
                        <label> Delete Video </label><br />
                        <label> Type "Confirm Delete" to delete this video </label>
                        <input type="text" name="confirm" required />
                        <input type="hidden" name="id" value={id} />
                        <input type="hidden" name="nonce" value={String(videoId)} />
                        <input type="submit" name="Delete" value="Delete" />
                    </form>
                    <br></br> <br></br>
                    <div className = "flexboxagain1">
                    <div id = "iframe-wrap">
                    <iframe
                        style={{textAlign: 'center', display: "flex" }}
                        id="youtube-player"
                        width="100%"
                        height="100%"
                        src={`https://www.youtube.com/embed/${videoId}?enablejsapi=1`}
                        allow="autoplay; encrypted-media"
                        allowFullScreen
                        title="YouTube Video Player">
                    </iframe>
                    
                <br></br>

                
                </div>
                  </div>

                <form style = {{ width: '40%', textAlign: 'center' }} onSubmit={addPost}>
                <textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)} // Update state with input
                    placeholder="Enter your post"
                    disabled={isDisabled}
                    style={{
                    width: '100%', // Make it take the full width of the container
                    height: '20px', // Set a larger height for more typing space
                    fontSize: '16px', // Increase font size for better readability
                    padding: '10px', // Optional: add padding for better spacing inside
                    resize: 'vertical', // Optional: allow resizing vertically
                    }}
                    onKeyDown={handleKeyPress} // Listen for key press event
                />
                <button type="submit">Submit</button> {/* Submit button */}
                </form>

                  {Fetched ? (  
                    reveal ? (  
                  <InfiniteScroll 
                      className = "flexboxagain"
                      style = {{width: "100%"}}
                      dataLength={arr.length} // number of items in the  list
                      hasMore={!!nexturl} // boolean to determine if more data can lod
                      next={fetchMoreData}
                      loader={<h4>Loading more posts...</h4>} // loader when fetching newdata
                      scrollThreshold={0.9}
                      scrollableTarget = "right-bottom"
                      endMessage={
                      <p style={{ textAlign: "center" }}>
                          <b>All posts loaded</b>
                      </p>
                      }
                  >
                      <br></br>
                      <h1 style={{ textAlign: "center" }}>Posts</h1>
                      <br></br>
                      {arr.map((x) => (
                          <Post  style={{ textAlign: "center" }} key = {x.postid} url = {x.url} postid = {x.postid} Del_post={delete_post_net}></Post>
                      ))}
                  </InfiniteScroll>) : (
                    <div className = "flexboxagain">
                    <br></br>
                    <h1 style={{ textAlign: "center" }}>posts are hidden by default, click to reveal</h1>
                    <br></br>
                    <button onClick={() => setReveal(true)}> Show Posts </button>
                    </div>
                  )) : (
                      <h4> fetching... </h4>
                  )}
                
            
            </div>
        </div>
      </div>
    );
  };


App1.propTypes = {
id: PropTypes.number.isRequired,
videoId: PropTypes.string.isRequired,
};
