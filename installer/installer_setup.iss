#define MyAppName "Kapytal"
#define MyAppVersion "1.2.2"
#define MyAppPublisher "Jakub Franek"
#define MyAppURL "https://github.com/JakubFranek/Kapytal"
#define MyAppExeName "Kapytal.exe"

[Setup]
AppId=4DDEDF56-5E83-4A1E-B930-D2D2E88F811C
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={localappdata}\Kapytal
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
LicenseFile=C:\Users\jfran\Coding\Kapytal\LICENCE.md
OutputBaseFilename=kapytal_v{#MyAppVersion}_win64
OutputDir={#SourcePath}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UsePreviousAppDir=yes
DirExistsWarning=auto
DisableDirPage=auto
DisableProgramGroupPage=auto
VersionInfoVersion={#MyAppVersion}
SetupIconFile=..\resources\icons\icons-custom\kapytal.ico
UninstallDisplayIcon={app}\Kapytal.exe


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\jfran\Coding\Kapytal\dist\main\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\jfran\Coding\Kapytal\dist\main\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\_internal\resources\icons\icons-custom\kapytal.ico";
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\_internal\resources\icons\icons-custom\kapytal.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

