#Requires AutoHotkey v1.1
#Persistent

; === YouTube downloader setup ===
askDownload := "yes"  ; Change to "no" to skip asking

SetTimer, CheckForNewLink, 1000

; === Variables for hiding cmd window ===
hiddenHwnd := 0

; === Tray menu for restoring CMD or exiting ===
Menu, Tray, Add, Restore CMD, RestoreCMD
Menu, Tray, Add, Exit, ExitScript
Menu, Tray, Hide  ; start hidden

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

; === Hotkey to hide active cmd window and show tray menu ===
^+m::  ; Ctrl+Shift+M
    WinGetClass, class, A
    if (class = "ConsoleWindowClass") {
        WinGet, hiddenHwnd, ID, A
        WinHide, ahk_id %hiddenHwnd%
        Menu, Tray, Show
    }
return

; === Tray menu item to restore hidden cmd window ===
RestoreCMD:
    if (hiddenHwnd) {
        WinShow, ahk_id %hiddenHwnd%
        WinActivate, ahk_id %hiddenHwnd%
        hiddenHwnd := 0
        Menu, Tray, Hide
    }
return

; === Tray menu item to exit the script ===
ExitScript:
    ExitApp
