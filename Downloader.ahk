#Requires AutoHotkey v1.1
#Persistent

askDownload := "yes"
userPath := A_UserName
savePath := "C:\\Users\\" . userPath . "\\Videos\\YouTube"
lastContent := ""
showConsole := "yes"  ; change to "yes" to show command window

SetTimer, CheckForChanges, 1000
return

CheckForChanges:
FileRead, newContent, % "C:\\Users\\" . userPath . "\\Documents\\ytlink.txt"
if (newContent != lastContent) {
    lastContent := newContent
    SetTimer, CheckForChanges, Off

    if (askDownload = "yes" || askDownload = "y") {
        MsgBox, 4, New Link Detected, New link detected:`n%newContent%`nDownload it?
        IfMsgBox, Yes
        {
            if (!FileExist(savePath)) {
                MsgBox, 16, Error, Save path does not exist:`n%savePath%
                return
            }
            
            cmd =
            (
%ComSpec% /c pushd "%savePath%" && yt-dlp "%newContent%" && popd
            )
            if (showConsole = "yes" || showConsole = "y") {
                RunWait, %cmd%
            } else {
                RunWait, %cmd%, , Hide
            }
            
            Run, %savePath%
        }
    }
}
return
