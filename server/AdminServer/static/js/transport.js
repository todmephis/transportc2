function Clear(str){
    if (document.getElementById(str).value == "CMD Here")
        document.getElementById(str).value= "";
}

function Home(){
    window.location.href = "/";
}

function AddAdmin(){
    window.location.href = "/add_admin";
}

function Refresh(){
      // Manually refresh dynamic fields on page
      CommandLog();
      ActiveClients();
      ActiveUsers();
}

function MasterLog(){
    window.location.href = "/api/master_log";
}

function PassChange(){
    window.location.href = "/change_pwd";
}

function ClearCMD(){
    window.location.href = "/api/clear";
}

function LogOut(){
    window.location.href = "/logout";
}

function CommandLog(){
    // Insert HTML for dynamic log entries
    $.getJSON( "/api/log", function(data) {
        // Delete all rows in log table
        $("#log_table tbody").empty();
        // loop through array and populate log table
        $.each(data, function(item) {
            var User = $("<td>");
            User.append(data[item].User)

            var Agent = $("<td>");
            Agent.append(data[item].Agent)

            var Time = $("<td>");
            Time.append(data[item].Time)

            var Command = $("<td>");
            Command.append(data[item].Command)

            var Response = $("<td>");
            Response.append(data[item].Response)

            var row = $("<tr>")
            row.append(User);
            row.append(Agent);
            row.append(Time);
            row.append(Command);
            row.append(Response);
            $("#log_table tbody").append(row);
        });
    });
}

function SelectAll() {
    var items = document.getElementsByName('chkHost');
    for (var i = 0; i < items.length; i++) {
        if (items[i].type == 'checkbox')
            items[i].checked = true;
    }
}

function UnSelectAll() {
    var items = document.getElementsByName('chkHost');
    for (var i = 0; i < items.length; i++) {
        if (items[i].type == 'checkbox')
            items[i].checked = false;
    }
}

function ActiveClients(){
    // Insert HTML for dynamic active agents
    $.getJSON("/api/client", function(data) {
        // Delete all rows in table
        $("#active_clients").empty();
        $("#client_table tbody").empty();

        $.each(data, function(item) {
            $("#active_clients").append($("<li>").text(data[item].Hostname));
            $("#client_table tbody").append("<tr>");
            $("#client_table tbody tr").append("<td>");
            $("#client_table tbody tr td").append($("<input>",
                {
                    type: "checkbox",
                    value: data[item].ID,
                    name: "chkHost"
                }));
            $("#client_table tbody tr").append($("<td>", {text: data[item].HOSTNAME}));
            $("#client_table tbody tr").append($("<td>", {text: data[item].OS}));
            $("#client_table tbody tr").append($("<td>", {text: data[item].IP}));
            $("#client_table tbody tr").append($("<td>", {text: data[item].PID}));
            $("#client_table tbody tr").append($("<td>", {text: data[item].TYPE}));
            $("#client_table tbody tr").append($("<td>", {text: data[item].PROTOCOL}));

        });
    });
}

function PostCmd(params) {
    // CREDIT: https://stackoverflow.com/questions/133925/javascript-post-request-like-a-form-submit
    var form = document.createElement("form");
    form.setAttribute("method", "post");
    form.setAttribute("action", "/api/cmd");

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);
            form.appendChild(hiddenField);
        }
    }
    document.body.appendChild(form);
    form.submit();
}

function CmdSubmit(){
    var DATA = {};
    // Read in checked clients to apply CMD
    var clients = []
    var items = document.getElementsByName("chkHost");
    for (var i = 0; i < items.length; i++) {
        if (items[i].type == "checkbox")
            clients.push(items[i].value);
    }
    DATA["clients"] = clients;
    // Read in command
    var cmd = $("#ClientCmd").val();
    DATA["command"] = cmd;
    // Submit form
    PostCmd(DATA);
    //Reset Form
    $(".cmd_form").reset();
}

function ActiveUsers(){
    // Insert HTML for dynamic active agents
    $.getJSON( "/api/admin", function(data) {
        // Delete all rows in list
        $("#active_users").empty();
        // loop through array and populate active agents
        $.each(data, function(item) {
            $("#active_users").append($("<li>").text(data[item].User));
        });
    });
}