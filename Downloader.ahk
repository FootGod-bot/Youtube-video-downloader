#Requires AutoHotkey v1.1
#Persistent

; === Variables ===
askDownload := "yes"
userPath := A_UserName  ; Auto-detect user folder
savePath := "C:\Users\" . userPath . "\Videos\YouTube"

; === Watch ytlink.txt for changes ===
lastContent := ""
SetTimer, CheckForChanges, 1000
return

CheckForChanges:
    FileRead, newContent, % "C:\Users\" . userPath . "\Documents\ytlink.txt"
    if (newContent != lastContent) {
        lastContent := newContent
        SetTimer, CheckForChanges, Off  ; Stop watching once change is detected

        ; Check if askDownload is yes or y
        if (askDownload = "yes" || askDownload = "y") {
            MsgBox, 4, New Link Detected, New link detected:`n%newContent%`nDownload it?
            IfMsgBox, Yes
            {
                ; Check if savePath exists
                if (!FileExist(savePath)) {
                    MsgBox, 16, Error, Save path does not exist:`n%savePath%
                    return
                }
                ; Run yt-dlp with the link in the savePath directory (hidden)
                cmd := "cmd.exe /c cd /d \"" . savePath . "\" && yt-dlp \"" . newContent . "\""
                Run, %cmd%, , Hide

                ; Open the savePath folder
                Run, %savePath%
            }
        }
    }
return
