import React, {
    useState,
    useEffect,
    useCallback,
    useRef,
  } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import { StrictMode } from "react";


dayjs.extend(relativeTime);
dayjs.extend(utc);


export default function Post({ url, postid, Del_post}) {

    const urlRef = useRef(url);
    const [comments, setComments] = useState([]);
    const [comment, setComment] = useState("");
    const [owner, setOwner] = useState("");
    const [timestamp, setTimestamp] = useState(null);
    const [vid_timestamp, setVidTimestamp] = useState("");
    const [text, setText] = useState("");
    // for conditional rendering
    const [Fetched, setFetched] = useState(false);
    const [ownerShowUrl, setownerShowUrl] = useState("");
    // text box
    const [isDisabled, setIsDisabled] = useState(false);
    const [logOwnsThis, setlogOwnsThis] = useState(false);

    const [confirmDel, setConfirmDel] = useState(false);


    // Timestamp
    const processTimestamp = useCallback((timestamp1) => {
        setTimestamp(dayjs.utc(timestamp1).local().fromNow());
    }, []);


    const delete_comment_net = (commentid) => {
        fetch(`/api/comments/?commentid=${commentid}`, {
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
            setComments((prevComments) => prevComments.filter((x) => x.commentid !== commentid));
          })
          .catch((error) => {
            console.error("Error deleting comment:", error);
          });
      }




    function addComment(e) {
        e.preventDefault();
        setIsDisabled(true);
        fetch(`/api/comments/?postid=${postid}`, {
            method: "POST",
            credentials: "same-origin",
            headers: {
              "Content-Type": "application/json", // Correct Content-Type
            },
            body: JSON.stringify({ postid:postid, comment: comment }),
          })
            .then((response) => {
              if (response.ok) {
                // console.log(e.target.value);
                return response.json();
              }
              setIsDisabled(false);
              throw new Error("Failed to fetch resource");
              // data shouldn't be anything?
              // is there a bug that we need to check
            })
            .then((data) => {
              // debugger;
              const newComments = [...comments];
              const newComment = data;
              newComment.created = dayjs.utc(newComment.created).local().fromNow()
              newComments.push(newComment);
              setComments(newComments);
              setComment("");
              setIsDisabled(false);
            })
            .catch((error) => console.log(error));
    }

    useEffect(() => {
        // Declare a boolean flag that we can use to cancel the API request.
        let ignoreStaleRequest = false;
        // console.log("url");
        // console.log(url);
    
        // Call REST API to get the post's information
        // console.log("feteching: " + url);
        fetch(urlRef.current, { credentials: "same-origin" })
          .then((response) => {
            if (!response.ok) {
              throw Error(response.statusText);
            }
            // console.log("fetched" + url);
            return response.json();
          })
          .then((data) => {
            // If ignoreStaleRequest was set to true, we want to ignore the results of the
            // the request. Otherwise, update the state to trigger a new render.
            if (!ignoreStaleRequest) {
              // console.log("setters called: " + url);
              
              setOwner(data.owner);
              setText(data.text);

              //processTimestamp(data.created);
              setTimestamp(dayjs.utc(data.created).local().fromNow());
              setVidTimestamp(data.vid_timestamp);
    

              data.comments.forEach(item => {
                item.created = dayjs.utc(item.created).local().fromNow()  // Example: updating to the current date
              });
              setComments(data.comments);
              
              
             setlogOwnsThis(data.logOwnsThis);
              // Set like button
              // setPostid(data.postid);
              setownerShowUrl(data.ownerShowUrl);
              setFetched(true);
            }
          })
          .catch((error) => console.log(error));
    
        return () => {
          // This is a cleanup function that runs whenever the Post component
          // unmounts or re-renders. If a Post is about to unmount or re-render, we
          // should avoid updating state.
          ignoreStaleRequest = true;
        };
      }, []);

      const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          addComment(e); // Submit the form when Enter is pressed
        }
      };

    if (!Fetched){
        return <p>Loading Post...</p>
    }

    return (

        <StrictMode style={{textAlign: "center"}}>
            <div className = "pcomment">
            {vid_timestamp < 3600 ? (
                <h3 className="left-align">{((vid_timestamp-(vid_timestamp%60))/60).toString().padStart(2, '0')}:{(vid_timestamp%60).toString().padStart(2, '0')} &#9; </h3>
                ) : (
                <h3 className="left-align">{((vid_timestamp-(vid_timestamp%3600))/3600).toString().padStart(1, '0')}:{(((vid_timestamp-(vid_timestamp%60))/60)%60).toString().padStart(2, '0')}:{(vid_timestamp%60).toString().padStart(2, '0')} &#9; </h3>  
                )}
                <p className="center-align">{text}</p>
                {logOwnsThis ? (
                    confirmDel ? (
                        <p className="right-align">
                        {owner} <br />
                        {timestamp} <br />
                        <button onClick={() => Del_post(postid)}> Confirm Delete </button>
                        <br></br>
                        <button onClick={() => setConfirmDel(false)}> Nevermind </button>
                        </p>
                    ) : <p className="right-align">
                    {owner} <br />
                    {timestamp} <br />
                    <button onClick={() => setConfirmDel(true)}>  Delete </button>
                    </p>
                    ) : <p className="right-align">
                    {owner} <br />
                    {timestamp} <br />
                    </p>}
            </div>
            
            {comments.map((x) => (
                <div className = "pcomment1">
                    <p className="center-align">{x.text}</p>
                    {x.logOwnsThis ? (
                    <p className="right-align">{x.owner}: {x.created} <button onClick={() => delete_comment_net(x.commentid)}> Delete </button></p>
                    ) : (
                        <p className="right-align">{x.owner}: {x.created} </p>
                    )}
                </div>
                
                

            ))}
            <br></br>
            <form style = {{ width: '80%', textAlign: 'center' }} onSubmit={addComment}>
                <textarea
                    style = {{ width: '40%', minHeight: '50px' }}
                    value={comment}
                    onChange={(e) => setComment(e.target.value)} // Update state with input
                    placeholder="Enter your Comment"
                    disabled={isDisabled}
                    onKeyDown={handleKeyPress} // Listen for key press event
                />
                
            </form>
            <br></br>
        </StrictMode>
    )

}