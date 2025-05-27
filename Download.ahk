#Requires AutoHotkey v1.1
#Persistent
askDownload := "yes"  ; Change to "no" to skip asking
hiddenHwnd := ""      ; stores the window that was hidden

SetTimer, CheckForNewLink, 1000
return

CheckForNewLink:
    FileRead, link, C:\Users\aiden\Documents\ytlink.txt
    if (link != "" && link != lastLink) {
        lastLink := link
        
        downloadFolder := "C:\Users\" . A_UserName . "\Videos\youtube"
        
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

        ; Always clear the file at the end
        FileDelete, C:\Users\aiden\Documents\ytlink.txt
        FileAppend,, C:\Users\aiden\Documents\ytlink.txt

        ; Open the download folder in Explorer
        Run, explorer.exe "%downloadFolder%"
    }
return

; Ctrl+Shift+M - Hide active window
^+m::
    WinGet, hiddenHwnd, ID, A
    DllCall("ShowWindow", "UInt", hiddenHwnd, "Int", 0x0) ; SW_HIDE
return

; Ctrl+Shift+U - Restore the last hidden window
^+u::
    if (hiddenHwnd != "")
    {
        DllCall("ShowWindow", "UInt", hiddenHwnd, "Int", 0x5) ; SW_SHOW
        WinActivate, ahk_id %hiddenHwnd%
        hiddenHwnd := "" ; optional: clear so it doesn't keep reopening
    }
return
