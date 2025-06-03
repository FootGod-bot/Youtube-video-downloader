#Requires AutoHotkey v1.1
#Persistent

askDownload := "yes"  ; y/yes to ask, n/no to skip prompt
userPath := A_UserName
savePath := "C:\\Users\\" . userPath . "\\Videos\\YouTube"
lastContent := ""

; New variable: showConsole = "no" to hide, "yes" to show
showConsole := "no"  ; change to "yes" to show command window

SetTimer, CheckForChanges, 1000
return

CheckForChanges:
FileRead, newContent, % "C:\\Users\\" . userPath . "\\Documents\\ytlink.txt"
if (newContent != lastContent) {
    lastContent := newContent
    SetTimer, CheckForChanges, Off

    ; If askDownload is no, skip prompt and download immediately
    if (askDownload ~= "^(yes|y)$") {
        MsgBox, 4, New Link Detected, New link detected:`n%newContent%`nDownload it?
        IfMsgBox, No
            return
    }
    
    if (!FileExist(savePath)) {
        MsgBox, 16, Error, Save path does not exist:`n%savePath%
        return
    }
    
    cmd =
    (
%ComSpec% /c pushd "%savePath%" && yt-dlp "%newContent%" && popd
    )
    if (showConsole ~= "^(yes|y)$") {
        RunWait, %cmd%, , Hide
    } else {
        RunWait, %cmd%
    }
    
    Run, %savePath%
}
return
