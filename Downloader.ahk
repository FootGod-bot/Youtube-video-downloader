#Requires AutoHotkey v1.1
#Persistent
; User Editable Variables:
; showConsole: "yes" to show yt-dlp console normally, "no" to run minimized
; openAfterDownload: "yes" to open folder after download, "no" to skip
; baseSavePath: default download folder

showConsole := "no"
openAfterDownload := "yes"
baseSavePath := "C:\Users\" . A_UserName . "\Videos\YouTube"

userPath := A_UserName
docsPath := "C:\Users\" . userPath . "\Documents"
ytDlpPath := "C:\yt-dlp\yt-dlp.exe"
ffmpegPath := "C:\ffmpeg\ffmpeg-git-full\ffmpeg-2025-06-02-git-688f3944ce-full_build\bin"

lastContent := ""
savePath := baseSavePath

SetTimer, CheckForChanges, 1000
return

CheckForChanges:
FileRead, newContent, % docsPath "\ytlink.txt"
if (newContent != "" && newContent != lastContent) {
    lastContent := newContent
    folderList := []
    folderList.Push(baseSavePath)
    GetSubfolders(baseSavePath, folderList)
    ShowFolderGui(folderList)
    SetTimer, CheckForChanges, Off
}
return

GetSubfolders(path, ByRef list) {
    Loop, Files, % path "\*", D
        list.Push(A_LoopFileFullPath), GetSubfolders(A_LoopFileFullPath, list)
}

ShowFolderGui(folderList) {
    global
    guiStr := ""
    for index, folderPath in folderList
        guiStr .= folderPath "|"
    guiStr := RTrim(guiStr, "|")

    Gui, FolderSelector:New, +AlwaysOnTop +OwnDialogs
    Gui, Add, Text,, Select folder to save the download:
    Gui, Add, DropDownList, vChosenFolder w600 r10, %guiStr%
    Gui, Add, Button, gButtonOK default, OK
    Gui, Add, Button, gButtonCancel, Cancel
    Gui, Show,, Choose Save Folder
}

ButtonOK:
Gui, FolderSelector:Submit
Gui, FolderSelector:Destroy

global savePath, ChosenFolder
if (ChosenFolder != "")
    savePath := ChosenFolder
else
    savePath := baseSavePath

Gosub, DoDownload
return

ButtonCancel:
Gui, FolderSelector:Destroy
Gosub, CancelDownload
return

DoDownload:
global newContent, savePath, ytDlpPath, ffmpegPath, docsPath, showConsole, openAfterDownload, lastContent

if (!FileExist(savePath)) {
    MsgBox, 16, Error, Save path does not exist:`n%savePath%
    SetTimer, CheckForChanges, On
    return
}

cmdLine := ytDlpPath . " --ffmpeg-location " . Chr(34) . ffmpegPath . Chr(34) . " " . Chr(34) . newContent . Chr(34)

if (showConsole = "yes") {
    cmd := ComSpec . " /c pushd " . Chr(34) . savePath . Chr(34) . " && " . cmdLine . " && popd"
    RunWait, %cmd%
} else {
    cmd := ComSpec . " /c pushd " . Chr(34) . savePath . Chr(34) . " && " . cmdLine . " && popd"
    RunWait, %cmd%, , Min
}

FileDelete, % docsPath "\ytlink.txt"
lastContent := ""

if (openAfterDownload = "yes") {
    Run, %savePath%
}

savePath := baseSavePath
SetTimer, CheckForChanges, On
return

CancelDownload:
global docsPath, lastContent
FileDelete, % docsPath "\ytlink.txt"
lastContent := ""
SetTimer, CheckForChanges, On
return

GuiClose:
Gui, Destroy
SetTimer, CheckForChanges, On
return
