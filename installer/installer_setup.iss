#define MyAppName "Kapytal"
#define MyAppVersion "0.15.0"
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
DefaultDirName={autopf}\{#MyAppName}
LicenseFile=D:\Coding\Kapytal\LICENCE.md
PrivilegesRequiredOverridesAllowed=dialog
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


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "D:\Coding\Kapytal\dist\main\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\Coding\Kapytal\dist\main\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\_internal\resources\icons\icons-custom\coin-k.ico";
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\_internal\resources\icons\icons-custom\coin-k-large.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

