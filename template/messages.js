
function toggle_viewpoint() {
    /* toggles the person viewing the messages */
    var messages = document.getElementsByClassName("message");
    
    for (var i = 0; i < messages.length; ++i) {
        var message = messages[i];
        
        if (message.classList.contains("myMessage")) {
            message.classList.remove("myMessage");
            message.classList.add("fromThem");
        }
        
        else if (message.classList.contains("fromThem")) {
            message.classList.remove("fromThem");
            message.classList.add("myMessage");
        };
        
    };
    
    var title = document.getElementsByClassName("title")[0];
    
    var headers = title.getElementsByTagName("span");
    
    for (var i = 0; i < headers.length; ++i) {
        var header = headers[i];
        
        if (header.classList.contains("to")) {
            header.classList.remove("to");
            header.classList.add("from");
        }
        
        else if (header.classList.contains("from")) {
            header.classList.remove("from");
            header.classList.add("to");
        };
    }
}