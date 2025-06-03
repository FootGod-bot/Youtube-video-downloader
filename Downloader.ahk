#Requires AutoHotkey v1.1
#Persistent

askDownload := "yes"  ; y/yes to ask, n/no to skip prompt
userPath := A_UserName
savePath := "C:\\Users\\" . userPath . "\\Videos\\YouTube"
lastContent := ""
showConsole := "no"  ; y/yes to show command window, n/no to hide

SetTimer, CheckForChanges, 1000
return

CheckForChanges:
FileRead, newContent, % "C:\\Users\\" . userPath . "\\Documents\\ytlink.txt"
if (newContent != lastContent) {
    lastContent := newContent
    SetTimer, CheckForChanges, Off

    if (askDownload ~= "^(no|n)$") {
        goto StartDownload
    } else if (askDownload ~= "^(yes|y)$") {
        MsgBox, 4, New Link Detected, New link detected:`n%newContent%`nDownload it?
        IfMsgBox, No
            return
    } else {
        return
    }

    StartDownload:
    if (!FileExist(savePath)) {
        MsgBox, 16, Error, Save path does not exist:`n%savePath%
        return
    }

    cmd =
    (
%ComSpec% /c pushd "%savePath%" && yt-dlp "%newContent%" && popd
    )
    if (showConsole ~= "^(yes|y)$") {
        RunWait, %cmd%
    } else {
        RunWait, %cmd%, , Hide
    }

    Run, %savePath%
}
return
