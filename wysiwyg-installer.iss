; Inno Setup Script for WYSIWYG
; Installs the compiled EXE, static assets, and sub-components.

#define MyAppName "WYSIWYG"
#define MyAppVersion "1.9.30.3"
#define MyAppPublisher "Xeno Head"
#define MyAppExeName "WYSIWYG.exe"

[Setup]
AppId={{C349C35F-55AA-466D-B029-6D39D55C0E28}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName=C:\FYRTOOLS\WYSIWYG
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=INSTALL_WYSIWYG
SetupIconFile=fyr-logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
CloseApplications=force

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Run at Windows Startup"; GroupDescription: "Additional options:"; Flags: unchecked

[Files]
; Main Executable
Source: "dist\WYSIWYG.exe"; DestDir: "{app}"; Flags: ignoreversion

; Root Configuration & Assets (only copy data.json if it doesn't already exist to preserve local profiles)
Source: "index.html"; DestDir: "{app}"; Flags: ignoreversion
Source: "editor.html"; DestDir: "{app}"; Flags: ignoreversion
Source: "admin.html"; DestDir: "{app}"; Flags: ignoreversion
Source: "search.html"; DestDir: "{app}"; Flags: ignoreversion
Source: "data.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "fyrlogo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "fyr-logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "media_formats.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "version.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "changelog.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "styles.css"; DestDir: "{app}"; Flags: ignoreversion
Source: "style_guide.html"; DestDir: "{app}"; Flags: ignoreversion
Source: "walmart.html"; DestDir: "{app}"; Flags: ignoreversion
Source: "app.js"; DestDir: "{app}"; Flags: ignoreversion

; Subfolders
Source: "WalmartSheet\*"; DestDir: "{app}\WalmartSheet"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Uberpaste\*"; DestDir: "{app}\Uberpaste"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "WysiScan\config.json"; DestDir: "{app}\WysiScan"; Flags: ignoreversion onlyifdoesntexist
Source: "WysiScan\*"; DestDir: "{app}\WysiScan"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "config.json,*.log,*.bak*,*.redo,temp\*,scans\*"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.json"
Type: files; Name: "{app}\*.txt"
Type: files; Name: "{app}\*.PNG"
Type: files; Name: "{app}\*.ico"
Type: filesandordirs; Name: "{app}\WalmartSheet"
Type: filesandordirs; Name: "{app}\Uberpaste"
Type: filesandordirs; Name: "{app}\WysiScan"

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  // Gracefully terminate running instances of the app or its components prior to copying files
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM WYSIWYG.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM WysiScan.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM XDevHubX.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Sleep(1500); // Give the OS time to release file handles
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Configure network sharing for C:\FYRTOOLS (Read access for Everyone)
    Exec('cmd.exe', '/c net share FYRTOOLS="C:\FYRTOOLS" /GRANT:Everyone,READ', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    // Terminate processes before deleting files so they are not locked
    Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM WYSIWYG.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM WysiScan.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM XDevHubX.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Sleep(1500); // Give the OS time to release file handles
  end;
end;
