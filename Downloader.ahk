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
{
    FileRead, newContent, % "C:\Users\" . userPath . "\Documents\ytlink.txt"
    if (newContent != lastContent) {
        lastContent := newContent
        SetTimer, CheckForChanges, Off  ; Stop watching once change is detected

        ; Check if askDownload is yes or y
        if (askDownload = "yes" || askDownload = "y") {
            MsgBox, 4, New Link Detected, New link detected:`n%newContent%`nDownload it?
            IfMsgBox, Yes
            {
                ; Continue with download logic here
            }
        }
    }
}
