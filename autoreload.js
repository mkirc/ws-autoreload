window.addEventListener("DOMContentLoaded", () => {
  if (typeof wsPort === 'undefined') {
    let wsPort = 5001
  }
  const websocket = new WebSocket("ws://localhost:" + wsPort + "/");
  sendReady(websocket);
  receiveFilechange(websocket);
});

function sendReady(websocket) {
    websocket.onopen = function(e) {
        websocket.send('ping')
    }
}

function receiveFilechange(websocket) {
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case "fileChange":
        // refresh page 
        console.log(event.path);
        if (window.location.pathname == event.path) {
            // console.log('paths are same')
            websocket.close(1000)
            window.location.reload();
        }

        break
      case "error":
        console.error(event.message);
        break;
      default:
        throw new Error(`Unsupported event type: ${event.type}.`);
    }
    return
  });
}

