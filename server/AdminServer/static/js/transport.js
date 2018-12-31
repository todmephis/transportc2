function Clear(str)
{
    if (document.getElementById(str).value == "CMD Here")
        document.getElementById(str).value= "";
}

function Home()
{
    window.location.href = "/";
}

function AddAdmin()
{
    window.location.href = "/add_admin";
}

function PassChange()
{
    window.location.href = "/change_pwd";
}

function ClearCMD()
{
    window.location.href = "/api/clear";
}

function LogOut()
{
    window.location.href = "/logout";
}

function CommandLog()
{
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

function ActiveClients()
{
    // Insert HTML for dynamic active agents
    $.getJSON( "/api/client", function(data) {
        // Delete all rows in list & form options
        $("#active_clients").empty();
        $("#dropdown_clients").empty();
        // loop through array and populate active agents
        $.each(data, function(item) {
            $("#active_clients").append($("<li>").text(data[item].Agent));
            $("#dropdown_clients").append($('<option>', {
                value: data[item].Agent,
                text: data[item].Agent
            }));
        });
    });
}

function ActiveUsers()
{
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
