; AutoHotkey v1 script
#Persistent
SetTimer, CheckQueue, 1000  ; Check every 1 second

; === CONFIG ===
audioFormat := "mp3" ; use formats like mp3, m4a, aac, opus, vorbis, wav, flac, alac
openFolder := true       ; true = open the folder after download
showConsole := "min"     ; options: "hidden" = no way to view the download window, "min" = minimized but still accessible, "shown" = becomes main window when it opens
watchFolder := A_MyDocuments

CheckQueue:
IfExist, %watchFolder%\ytlink.txt
{
    ; Read and parse ytlink.txt
    FileRead, fileContent, %watchFolder%\ytlink.txt

    link := ""
    type := ""
    savePath := ""

    Loop, Parse, fileContent, `n, `r
    {
        line := A_LoopField
        if (InStr(line, "Link:"))
            StringTrimLeft, link, line, 5
        else if (InStr(line, "Type:"))
            StringTrimLeft, type, line, 5
        else if (InStr(line, "SavePath:"))
            StringTrimLeft, savePath, line, 9
    }

    ; Determine console mode
    if (showConsole = "hidden")
        runMode := "Hide"
    else if (showConsole = "min")
        runMode := "Min"
    else
        runMode := ""  ; shown

    ; Run command based on type and wait for it to complete
        if (type = "Audio")
    {
        RunWait, %ComSpec% /c cd "%savePath%" && yt-dlp -x --audio-format %audioFormat% "%link%",, %runMode%
    }
    else if (type = "Normal")
    {
        RunWait, %ComSpec% /c cd "%savePath%" && yt-dlp "%link%",, %runMode%
    }

    ; Open folder only after full processing is done
    if (openFolder)
        Run, %ComSpec% /c start "" "%savePath%",, Hide

    FileDelete, %watchFolder%\ytlink.txt
    return
}

; If no ytlink.txt, check for queue#.txt
queueFiles := ""
Loop, Files, %watchFolder%\queue*.txt
{
    queueFiles .= A_LoopFileName "|"
}

if (queueFiles != "")
{
    Sort, queueFiles, D|
    StringSplit, qArr, queueFiles, |
    firstQueue := qArr1
    FileMove, %watchFolder%\%firstQueue%, %watchFolder%\ytlink.txt, 1
}
return
