#define AppName "Animora"
#define AppVersion "0.1.0"

[Setup]
AppId={{6B1431BD-70E3-4E70-8D12-EAB276A81FB7}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Animora contributors
DefaultDirName={autopf}\Animora
DefaultGroupName=Animora
PrivilegesRequired=lowest
OutputDir=installer-output
OutputBaseFilename=Animora-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
LicenseFile=LICENSE

[Files]
Source: "dist\Animora.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\Animora"; Filename: "{app}\Animora.exe"
Name: "{autodesktop}\Animora"; Filename: "{app}\Animora.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\Animora.exe"; Description: "Launch Animora"; Flags: postinstall nowait skipifsilent
