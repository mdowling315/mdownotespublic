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


export default function SimplePost({ url, postid}) {

    const urlRef = useRef(url);
    const [owner, setOwner] = useState("");
    const [vid_timestamp, setVidTimestamp] = useState("");
    const [text, setText] = useState("");
    // for conditional rendering
    const [Fetched, setFetched] = useState(false);
    const [ownerShowUrl, setownerShowUrl] = useState("");
    // text box

    useEffect(() => {
        // Declare a boolean flag that we can use to cancel the API request.
        let ignoreStaleRequest = false;
        // console.log("url");
        // console.log(url);
    
        // Call REST API to get the post's information
        // console.log("feteching: " + url);
        fetch( `${urlRef.current}?simple=1`, { credentials: "same-origin" })
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

              setVidTimestamp(data.vid_timestamp);
              
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


    if (!Fetched){
        return <div className = "comment" style={{backgroundColor: "orange"}}> <p className = "left-align"> :P </p><p className="center-align">Cannot Render Post</p>  <p className = "right-align"> :P </p></div>
    }
    return (

        <StrictMode style={{textAlign: "center"}}>
            <div className = "comment">
            {vid_timestamp < 3600 ? (
                <h3 className="left-align">{((vid_timestamp-(vid_timestamp%60))/60).toString().padStart(2, '0')}:{(vid_timestamp%60).toString().padStart(2, '0')} &#9; </h3>
                ) : (
                <h3 className="left-align">{((vid_timestamp-(vid_timestamp%3600))/3600).toString().padStart(1, '0')}:{(((vid_timestamp-(vid_timestamp%60))/60)%60).toString().padStart(2, '0')}:{(vid_timestamp%60).toString().padStart(2, '0')} &#9; </h3>  
                )}
                <p className="center-align">{text}</p>
                <p className="right-align">
                    {owner}
                    </p>
            </div>
        </StrictMode>
    )

}