; Installer Windows di BTC Cycle Planner (compilato dal workflow con /DVERSION=x.y.z)
!include "MUI2.nsh"

!ifndef VERSION
  !define VERSION "0.0.0"
!endif
!define APPNAME "BTC Cycle Planner"
!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\BTC_Cycle"

Name "${APPNAME} ${VERSION}"
OutFile "..\dist\BTC_Cycle-Setup-${VERSION}.exe"
InstallDir "$LOCALAPPDATA\Programs\BTC_Cycle"
RequestExecutionLevel user
Unicode true

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\BTC_Cycle.exe"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Italian"

Section "Install"
  SetOutPath "$INSTDIR"
  ; rimuove i file della versione precedente prima di copiare i nuovi
  RMDir /r "$INSTDIR\_internal"
  File /r "..\dist\BTC_Cycle\*.*"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\BTC_Cycle.exe"
  CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\BTC_Cycle.exe"
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayName" "${APPNAME}"
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKCU "${UNINST_KEY}" "Publisher" "enkas79"
  WriteRegStr HKCU "${UNINST_KEY}" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
SectionEnd

Section "Uninstall"
  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  RMDir "$SMPROGRAMS\${APPNAME}"
  Delete "$DESKTOP\${APPNAME}.lnk"
  DeleteRegKey HKCU "${UNINST_KEY}"
SectionEnd
