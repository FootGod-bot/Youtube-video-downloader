#Requires AutoHotkey v1.1
#Persistent
SetTimer, CheckForNewLink, 1000  ; Check every 1 second
return

CheckForNewLink:
    FileRead, link, C:\Users\aiden\Documents\ytlink.txt
    if (link != "" && link != lastLink) {
        lastLink := link
        MsgBox, 4,, YouTube link detected:`n%link%`nDownload it?
        IfMsgBox, Yes
        {
            fullCommand := "cmd.exe /c cd /d %USERPROFILE%\Videos\youtube && yt-dlp """ link """"
            RunWait, %fullCommand%
            FileDelete, C:\Users\aiden\Documents\ytlink.txt
        }
    }
return
