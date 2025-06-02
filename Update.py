#Requires AutoHotkey v1.1
#Persistent

askDownload := "yes"  ; Change to "no" to skip asking
downloadFolder := "C:\Users\" . A_UserName . "\Videos\youtube"  ; Change this path to whatever you want

SetTimer, CheckForNewLink, 1000
return

CheckForNewLink:
    FileRead, link, C:\Users\aiden\Documents\ytlink.txt
    if (link != "" && link != lastLink) {
        lastLink := link

        if (askDownload = "yes") {
            MsgBox, 4,, YouTube link detected:`n%link%`nDownload it?
            IfMsgBox, Yes
            {
                fullCommand := "cmd.exe /c cd /d """ . downloadFolder . """ && yt-dlp """ . link . """"
                RunWait, %fullCommand%
            }
            ; If No, skip download
        }
        else
        {
            fullCommand := "cmd.exe /c cd /d """ . downloadFolder . """ && yt-dlp """ . link . """"
            RunWait, %fullCommand%
        }

        ; Clear the file at the end
        FileDelete, C:\Users\aiden\Documents\ytlink.txt
        FileAppend,, C:\Users\aiden\Documents\ytlink.txt

        ; Open the download folder in Explorer
        Run, explorer.exe "%downloadFolder%"
    }
return
